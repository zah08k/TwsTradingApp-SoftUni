from django.core.exceptions import ObjectDoesNotExist
from ibapi.contract import Contract
import pandas as pd
import time
from celery import shared_task

from TwsTradingApp.trading.tws_contract_details import contract_hist_specs
from TwsTradingApp.trading.models import HistoricalData
from TwsTradingApp.trading.tws_connection import GetTwsApp


def futures(symbol, exchange, last_trade_month, sec_type="FUT", currency="USD"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.lastTradeDateOrContractMonth = last_trade_month
    contract.includeExpired = True
    return contract


def histData(app, req_num, contract, duration, candle_size, end_date_time):
    app.reqHistoricalData(reqId=req_num,
                          contract=contract,
                          endDateTime=end_date_time,
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='TRADES',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=False,
                          chartOptions=[])


@shared_task
def get_historical_data():
    TIME_FRAME = '5 mins'
    LOOKBACK_DAYS = '20 D'
    UNTIL = '20230821 16:00:00'
    cntr_specs = contract_hist_specs()

    for contract, details in cntr_specs.items():
        prepare_app = GetTwsApp(contract, details[0], details[1], details[2])
        app = prepare_app.get_tws_app()

        if app is None:
            return {'status': 'Error', 'message': 'No connection to TWS!'}

        app.histData(details[2], LOOKBACK_DAYS, TIME_FRAME, UNTIL)
        data = app.data

        df = pd.DataFrame(data=data)
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d  %H:%M:%S')

        for row in df.index:
            historical_data, created = HistoricalData.objects.get_or_create(
                ticker=contract.lower(),
                time=df['date'][row],
                defaults={
                    'open': df['open'][row],
                    'high': df['high'][row],
                    'low': df['low'][row],
                    'close': df['close'][row],
                    'volume': df['volume'][row],
                }
            )

            if not created:
                print("Data already exists for this time; skipping.")

        time.sleep(20)

