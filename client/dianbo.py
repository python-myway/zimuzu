import logging
from contextlib import contextmanager

from client.base import BaseClient
from ext.mailbase import email_dispatched, Message, Connection
from models import Resources, Location, session


class DianboClient(BaseClient):

    async def process_html(self, url):
        """ 返回一个html页面的数据 """

        try:
            resp = await self.session.get(url)
        except Exception as exc:
            logging.error('{} has error: {}'.format(url, str(exc)))
        else:
            if resp.status == 200 and ('text/html' in resp.headers.get('content-type')):
                data = (await resp.read()).decode('utf-8', 'replace')
                return data

    async def process_page_number(self):
        """ 返回每个大项的页数，如关于电视剧的所有资源的页数 """

        html = await self.process_html(self.root_url)
        raw_page = self.soup(html).find_all('a', attrs={'class': 'page-numbers'})[-2]
        pages = self.soup(str(raw_page)).a.string
        return int(pages)

    async def process_page_info(self, html):
        """ 返回单页上所有的数据列表 """

        soup2 = self.soup(html).find_all('a', attrs={'rel': 'bookmark'})
        info_list = []
        for s in soup2:
            s = self.soup(str(s))
            info_list.append((s.span.string, s.a['href']))  # todo 放进redis数据库后再读取
            resource = Resources(name=s.span.string, owner='电波字幕组',
                                 stype='tvshow', original=s.a['href'])
            session.add(resource)
        try:
            session.commit()
            info_list = []
        except Exception as e:
            session.rollback()
            logging.error('插入数据库发生错误--{}'.format(str(e)))
        finally:
            session.close()
            return info_list

    async def process_pan_info(self, html, resource, update=False):
        """ 返回每季资源的百度网盘地址 """

        soup2 = self.soup(html).find_all('a')
        if update:
            soup2 = list(soup2[-1])
        pan_list = []
        for s in soup2:
            s = self.soup(str(s))
            if s.a.string in ['百度网盘', '百度云盘']:
                pan_list.append(('episode', s.a['href'], resource))  # todo 放进redis数据库后再读取
                location = Location(episode='', url=s.a['href'], resource=resource)
                session.add(location)
        try:
            session.commit()
            pan_list = []
        except Exception as e:
            session.rollback()
            logging.error('插入数据库发生错误--{}'.format(str(e)))
        finally:
            session.close()
            return pan_list


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


if __name__ == '__main__':
    mail = EmailClient('smtp.163.com', 'your@email.address', 'your-email-password', 25)
    msg = Message(subject='测试', recipients=[('test', 'your@email.address')], sender=('test', 'your@email.address'))
    msg.body = 'http://test.com\nhttp://test.com\n'
    mail.send(msg)
