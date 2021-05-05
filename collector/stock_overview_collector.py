import json
from configparser import ConfigParser
import requests
import os
import sys

LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib')
sys.path.append(os.path.dirname(LIB_DIR))

from lib.rabbit_mq import AMQP

CONFG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config')

class StockOverviewCollector:
    def __init__(self):
        self.amqp = AMQP()
        self.config = ConfigParser()
        self.config.read(os.path.join(CONFG_DIR, self.__class__.__name__ + '.ini'))

    def start(self):
        self.amqp.connect()
        self.amqp.consume(
            self.config['amqp']['exch'],
            self.config['amqp']['queue'],
            self.config['amqp']['routing_key'], self.get_stock_overview)

    def stock_overview(self, ticker):
        self.host = self.config['Api']['host']
        self.api = self.config['Api']['apikey']
        response = requests.get('{0}?symbol={1}&function={2}&apikey={3}'.format
                                (
                                    self.host,
                                    ticker,
                                    'OVERVIEW',
                                    self.api
                                ))
        if response.status_code == 200:
            return response.json()

    def get_stock_overview(self, ch, method, properties, body):
        ret = {}
        body = json.dumps(body.decode("utf-8")).strip('"')
        stock_info = self.stock_overview(body)
        ret.update(symbol=stock_info.get('Symbol'),
                   name=stock_info.get('Name', None),
                   description=stock_info.get('Description', None),
                   eps=stock_info.get('EPS', None),
                   market_capitalization=stock_info.get(
                       'MarketCapitalization', None),
                   pe_ratio=stock_info.get('PERatio', None),
                   dividend_yield=stock_info.get('DividendYield', None),
                   year_high=stock_info.get('52WeekHigh', None),
                   year_low=stock_info.get('52WeekLow', None),
                   latest_quarter=stock_info.get('LatestQuarter', None))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.amqp.publish(
            self.config['amqp']['publish_exch'], self.config['amqp']['routing_key'], json.dumps(ret))


if __name__ == '__main__':
    stockoverviewcollector = StockOverviewCollector()
    stockoverviewcollector.start()
