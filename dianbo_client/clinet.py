from contextlib import contextmanager

import aiohttp
import requests
from bs4 import BeautifulSoup

from dianbo_client.mailbase import email_dispatched, Message, Connection


async def get_source():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.github.com/events') as resp:
            print(resp.status)
            print(await resp.text())


class DianboAPIError(Exception):
    def __init__(self, resp):
        self.status = resp.status_code
        self.reason = resp.reason
        self.msg = resp.parsed

    def __str__(self):
        return '***{} ({})*** {}'.format(self.status, self.reason, self.msg)


def check_execption(func):
    def _check(*arg, **kwargs):
        resp = func(*arg, **kwargs)
        if resp.status >= 400:
            raise DianboAPIError(resp)
        body = resp.body
        if body:
            return resp.parsed
        return body
    return _check


class DianboClient:

    def __init__(self):
        self.session = requests.session()
        self.parser = 'lxml'
        self.page_url = 'http://dbfansub.com/category/{}'
        self.info_url = 'http://dbfansub.com/category/{}/page/{}'

    def __repr__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @check_execption
    def _get_page(self, part):
        html = self.session.get(self.page_url.format(part)).text
        base_soup = BeautifulSoup(html, self.parser)
        raw_page = base_soup.find_all('a', attrs={'class': 'page-numbers'})[-2]
        pages = BeautifulSoup(str(raw_page), self.parser).a.string
        return int(pages)

    @check_execption
    def _get_info(self, part, page):
        html = self.session.get(self.info_url.format(part, page)).text
        soup = BeautifulSoup(html, self.parser)
        soup2 = soup.find_all('a', attrs={'rel': 'bookmark'})
        url_list = []
        for s in soup2:
            s = BeautifulSoup(str(s), self.parser)
            url_list.append((s.a['href'], s.span.string))
        return url_list

    @check_execption
    def _get_pan_info(self, url):
        html = self.session.get(url).text
        base_soup = BeautifulSoup(html, self.parser)
        soup2 = base_soup.find_all('a')
        pan_url_list = []
        for s in soup2:
            s = BeautifulSoup(str(s), 'lxml')
            if s.a.string == '百度网盘':
                pan_url_list.append(s.a['href'])
        return pan_url_list

    @property
    def tvshow_pages(self):
        return self._get_page('tvshow')

    @property
    def movie_pages(self):
        return self._get_page('movie')

    @property
    def music_pages(self):
        return self._get_page('music')

    def get_one_page_tvshow(self, page):
        return self._get_info('tvshow', page)

    def get_one_page_movie(self, page):
        return self._get_info('movie', page)

    def get_one_page_music(self, page):
        return self._get_info('music', page)

    def get_all_tvshow(self):
        tvshow_list = []
        for num in range(self.tvshow_pages):
            tvshow_list.extend(self._get_info('tvshow', num+1))
        return tvshow_list

    def get_all_movie(self):
        movie_list = []
        for num in range(self.movie_pages):
            movie_list.extend(self._get_info('movie', num + 1))
        return movie_list

    def get_all_music(self):
        music_list = []
        for num in range(self.music_pages):
            music_list.extend(self._get_info('music', num + 1))
        return music_list

    def get_pan_info(self, url):
        return self._get_pan_info(url)


class EmailClient:
    def __init__(self, server, username, password, port, use_tls=False, use_ssl=False,
                 default_sender=None, debug=False, max_emails=None, suppress=False,
                 ascii_attachments=False):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.default_sender = default_sender
        self.debug = debug
        self.max_emails = max_emails
        self.suppress = suppress
        self.ascii_attachments = ascii_attachments

    @contextmanager
    def record_messages(self):
        if not email_dispatched:
            raise RuntimeError("blinker must be installed")
        outbox = []

        def _record(message):
            outbox.append(message)
        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        with self.connect() as connection:
            message.send(connection)

    def send_message(self, sender, recipients, subject='', body=None, html=None, ):
        self.send(Message(sender=sender, recipients=recipients, subject=subject, body=body, html=html))

    def connect(self):
        try:
            return Connection(self)
        except KeyError:
            raise RuntimeError('邮件客户端未配置好')

    def async_email(self):
        pass

    def with_attachment_email(self):
        pass

    def with_html_email(self):
        pass


class BaiduyunClient:
    pass


if __name__ == '__main__':
    mail = EmailClient('smtp.163.com', 'chengganqin@163.com', 'hunting##161201', 25)
    msg = Message(subject='测试', recipients=[('test', '1612134263@qq.com')], sender=('test', 'chengganqin@163.com'))
    msg.body = 'http://test.com\nhttp://test.com\n'
    mail.send(msg)
