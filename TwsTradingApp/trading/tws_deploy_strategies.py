import random
import time

from ibapi.order import Order

from TwsTradingApp.trading.tws_connection import GetTwsApp


class SimpleOrderStrategy:
    def __init__(self, symbol, exchange, expiry, client_id):
        self.app = GetTwsApp(symbol, exchange, expiry, client_id).get_tws_app()

    def place_order(self):
        if self.app:
            time.sleep(5)
            order = Order()
            order.action = 'BUY'
            order.totalQuantity = 1
            order.orderType = 'LMT'
            order.lmtPrice = 80.0
            order.transmit = True
            order.eTradeOnly = False
            order.firmQuoteOnly = False

            order_id = random.randint(100000, 999999)
            self.app.placeOrder(order_id, self.app.contract, order)
        else:
            print("Failed to place order. App not connected.")
