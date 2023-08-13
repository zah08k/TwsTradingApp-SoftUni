import pandas as pd
import numpy as np
from celery import shared_task

from TwsTradingApp.trading.models import HistoricalData, BacktestResults, Strategy
import time


def get_data_for_ticker(ticker):
    data = HistoricalData.objects.filter(ticker=ticker).order_by('time')
    return data


def make_df(data):
    data_dict = {
        'time': [i.time for i in data],
        'open': [int(i.open) for i in data],
        'high': [int(i.high) for i in data],
        'low':[int(i.low) for i in data],
        'close': [int(i.close) for i in data],
        'volume': [int(i.volume) for i in data],
    }

    df = pd.DataFrame(data=data_dict)
    return df


def performance_metrics(pnl):
    pnl = [int(p) for p in pnl]
    cumsum = [int(p) for p in np.cumsum(pnl)]
    biggest_loss = float(min(pnl))
    biggest_win = float(max(pnl))
    avg_pnl = round(float(np.mean(pnl)), 2)

    return {'pnl': pnl,
           'cumsum': cumsum,
           'biggest_loss': biggest_loss,
           'biggest_win': biggest_win,
           'avg_pnl': avg_pnl}


@shared_task
def loxbars(ticker, lookback, target_profit, max_loss, strategy_id, parameters):
    data = get_data_for_ticker(ticker)
    df = make_df(data)

    pnl = []
    inpos = 0
    entry = None

    for i in df[lookback + 1:].index:
        if not inpos and df['close'][i - 1] > df['close'][i - 1 - lookback]:
            entry = df['open'][i]
            inpos = 1

        elif inpos == 1 and any([df['close'][i - 1] - entry > target_profit,
                                 df['close'][i - 1] - entry < max_loss]):
            profit = df['open'][i] - entry
            pnl.append(profit)
            inpos = 0

    results = performance_metrics(pnl)

    strategy = Strategy.objects.get(id=strategy_id)
    BacktestResults.objects.create(
        strategy=strategy,
        name=strategy.name,
        ticker=ticker,
        parameter_values=parameters,
        pnl_results=results,
    )


@shared_task
def prevrange(ticker, pct_range_long, pct_range_short, strategy_id, parameters):
    data = get_data_for_ticker(ticker)
    df = make_df(data)

    pnl = []
    inpos = 0
    entry = None

    for i in df[1:].index:
        bar_range = df['high'][i - 1] - df['low'][i - 1]
        high_minus_close = df['high'][i - 1] - df['close'][i - 1]
        relative_pct = (high_minus_close / bar_range) * 100

        if not inpos and relative_pct >= pct_range_long:
            entry = df['open'][i]
            inpos = 1

        elif not inpos and relative_pct <= pct_range_short:
            entry = df['open'][i]
            inpos = -1

        elif inpos == 1:
            profit = df['open'][i] - entry
            pnl.append(profit)
            inpos = 0

        elif inpos == -1:
            profit = entry - df['open'][i]
            pnl.append(profit)
            inpos = 0

    results = performance_metrics(pnl)

    strategy = Strategy.objects.get(id=strategy_id)
    BacktestResults.objects.create(
        strategy=strategy,
        name=strategy.name,
        ticker=ticker,
        parameter_values=parameters,
        pnl_results=results,
    )


@shared_task
def matrend(ticker, ma_window, strategy_id, parameters):
    data = get_data_for_ticker(ticker)
    df = make_df(data)

    df['ma'] = df['close'].rolling(window=ma_window).mean()

    pnl = []
    inpos = 0
    entry = None

    for i in df[ma_window + 1:].index:
        if inpos == 0 and df['close'][i - 1] > df['ma'][i - 1]:
            entry = df['open'][i]
            inpos = 1

        elif inpos == 0 and df['close'][i - 1] < df['ma'][i - 1]:
            entry = df['open'][i]
            inpos = -1

        elif inpos == 1 and df['close'][i - 1] < df['ma'][i - 1]:
            profit = df['open'][i] - entry
            pnl.append(profit)
            inpos = 0

        elif inpos == -1 and df['close'][i - 1] > df['ma'][i - 1]:
            profit = entry - df['open'][i]
            pnl.append(profit)
            inpos = 0

    results = performance_metrics(pnl)

    strategy = Strategy.objects.get(id=strategy_id)
    BacktestResults.objects.create(
        strategy=strategy,
        name=strategy.name,
        ticker=ticker,
        parameter_values=parameters,
        pnl_results=results,
    )


