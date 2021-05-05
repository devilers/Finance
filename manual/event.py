import requests
import json
from configparser import ConfigParser
import os


def earnings_release(host, api):
    response = requests.get('{0}?function={1}&apikey={2}&datatype=json'.format
                            (
                                host,
                                'EARNINGS_CALENDAR',
                                api
                            ))
    if response.status_code == 200:
        return response.text


if __name__ == '__main__':
    config = ConfigParser()
    config.read(os.path.basename(__file__).capitalize().replace('.py', '.ini'))
    data = earnings_release(config['Api']['host'], config['Api']['apikey'])
