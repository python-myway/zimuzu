#!/usr/bin/env python3

import asyncio
import logging
import re
import signal
import sys
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from client.log import CLIENT_LOGGING


class BaseClient:

    def __init__(self, root_url, loop, max_tasks=100, log_config=CLIENT_LOGGING, parser=None):
        self.root_url = root_url
        self.loop = loop
        self.todo = set()
        self.busy = set()
        self.done = {}
        self.tasks = set()
        self.sem = asyncio.Semaphore(max_tasks, loop=loop)
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


def main():
    loop = asyncio.get_event_loop()

    c = Crawler(sys.argv[1], loop)
    asyncio.ensure_future(c.run(), loop=loop)

    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass
    loop.run_forever()
    print('todo:', len(c.todo))
    print('busy:', len(c.busy))
    print('done:', len(c.done), '; ok:', sum(c.done.values()))
    print('tasks:', len(c.tasks))


if __name__ == '__main__':
    if '--iocp' in sys.argv:
        from asyncio import events, windows_events
        sys.argv.remove('--iocp')
        logging.info('using iocp')
        el = windows_events.ProactorEventLoop()
        events.set_event_loop(el)

    main()