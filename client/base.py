#!/usr/bin/env python3

import logging

import aiohttp
from bs4 import BeautifulSoup

from client.log import CLIENT_LOGGING


class BaseClient:

    def __init__(self, root_url, loop, log_config=CLIENT_LOGGING, parser='lxml'):
        self.root_url = root_url
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)
        self.parser = parser

        if log_config:
            logging.config.dictConfig(log_config)

    def __repr__(self):
        return '<Client at {}>'.format(id(self))

    def __call__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def soup(self, html):
        return BeautifulSoup(html, self.parser)


if __name__ == '__main__':
    pass
