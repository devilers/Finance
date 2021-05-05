import json
from configparser import ConfigParser
import requests
import os
import sys

LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib')
sys.path.append(os.path.dirname(LIB_DIR))

from lib.rabbit_mq import AMQP

CONFG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config')

class StockPriceCollector:
    def __init__(self):
        self.amqp = AMQP()
        self.config = ConfigParser()
        self.config.read(os.path.join(CONFG_DIR, self.__class__.__name__ + '.ini'))

    def start(self):
        self.amqp.connect()
        self.amqp.consume(
            self.config['amqp']['exch'],
            self.config['amqp']['queue'],
            self.config['amqp']['routing_key'], self.get_stock_price)

    def stock_price(self, ticker):
        self.host = self.config['Api']['host']
        self.api = self.config['Api']['apikey']
        response = requests.get('{0}/{1}/{2}?token={3}'.format
                                (
                                    self.host,
                                    ticker,
                                    'quote',
                                    self.api
                                ))
        if response.status_code == 200:
            return response.json()

    def get_stock_price(self, ch, method, properties, body):
        body = json.dumps(body.decode("utf-8")).strip('"')
        stock_price_info = self.stock_price(body)
        ret = {}
        ret.update(symbol=stock_price_info.get('symbol'),
                   latestPrice=stock_price_info.get('latestPrice', None),
                   open=stock_price_info.get('open', None),
                   close=stock_price_info.get('close', None))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.amqp.publish(
            self.config['amqp']['publish_exch'], self.config['amqp']['routing_key'], json.dumps(ret))

if __name__ == '__main__':
    stockpricecollector = StockPriceCollector()
    stockpricecollector.start()
