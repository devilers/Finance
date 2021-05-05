import json
import os
import sys
from configparser import ConfigParser
import requests

LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../lib')
sys.path.append(os.path.dirname(LIB_DIR))

from lib.rabbit_mq import AMQP

CONFG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config')

class StockNewsCollector:
    def __init__(self):
        self.amqp = AMQP()
        self.config = ConfigParser()
        self.config.read(os.path.join(CONFG_DIR, self.__class__.__name__ + '.ini'))

    def start(self):
        self.amqp.connect()
        self.amqp.consume(
            self.config['amqp']['exch'],
            self.config['amqp']['queue'],
            self.config['amqp']['routing_key'], self.get_stock_news)

    def stock_news(self, ticker):
        self.host = self.config['Api']['host']
        self.api = self.config['Api']['apikey']
        response = requests.get('{0}/{1}/{2}/last/1?token={3}'.format
                                (
                                    self.host,
                                    ticker,
                                    'news',
                                    self.api
                                ))
        if response.status_code == 200:
            return response.json()

    def get_stock_news(self, ch, method, properties, body):
        ret = {}
        body = json.dumps(body.decode("utf-8")).strip('"')
        stock_news_info = self.stock_news(body)[0]
        ret.update(datetime=stock_news_info.get('datetime'),
                   headline=stock_news_info.get('headline', None),
                   url=stock_news_info.get('url', None),
                   summary=stock_news_info.get('summary', None),
                   image=stock_news_info.get('image', None))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        self.amqp.publish(
            self.config['amqp']['publish_exch'], self.config['amqp']['routing_key'], json.dumps(ret))


if __name__ == '__main__':
    stocknewscollector = StockNewsCollector()
    stocknewscollector.start()
