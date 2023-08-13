import pandas as pd
from celery import shared_task
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self, symbol, exchange, last_trade_month, client_id):
        EClient.__init__(self, self)
        self.symbol = symbol
        self.exchange = exchange
        self.last_trade_month = last_trade_month
        self.client_id = client_id
        self.contract = self.futures(self.symbol, self.exchange, self.last_trade_month)

        self.data = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId, errorCode, errorString))

    def historicalData(self, reqId, bar):
        self.data['date'].append(bar.date)
        self.data['open'].append(bar.open)
        self.data['high'].append(bar.high)
        self.data['low'].append(bar.low)
        self.data['close'].append(bar.close)
        self.data['volume'].append(bar.volume)

    def histData(self, req_num, duration, candle_size, end_date_time):
        """
        app.histData(1, '3 D', '5 mins', '20230313 16:00:00')
        """
        self.reqHistoricalData(reqId=req_num,
                              contract=self.contract,
                              endDateTime=end_date_time,
                              durationStr=duration,
                              barSizeSetting=candle_size,
                              whatToShow='TRADES',
                              useRTH=1,
                              formatDate=1,
                              keepUpToDate=False,
                              chartOptions=[])

        time.sleep(3)

    def futures(self, symbol, exchange, last_trade_month, sec_type="FUT", currency="USD"):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.currency = currency
        contract.exchange = exchange
        contract.lastTradeDateOrContractMonth = last_trade_month
        contract.includeExpired = True
        return contract

    def websocket_connection(self):
        thread = threading.Thread(target=self.run)
        thread.start()

    def connect_tws(self):
        self.connect("host.docker.internal", 7497, clientId=self.client_id)
        self.websocket_connection()


class GetTwsApp:
    def __init__(self, symbol, exchange, expiry, client_id):
        self.symbol = symbol
        self.exchange = exchange
        self.expiry = expiry
        self.client_id = client_id
        self.app = None

    def get_tws_app(self):
        if self.app is None or not self.app.isConnected():
            print("app is not connected and will reconnect now...")
            self.app = TradingApp(self.symbol,
                             self.exchange,
                             self.expiry,
                             self.client_id)
            self.app.connect_tws()
            time.sleep(10)
            if self.app.isConnected():
                print("app is connected...")
                return self.app
            else:
                print("app failed to connect...")
                return None

        return self.app


