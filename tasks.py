import os
import subprocess
import asyncio
import smtplib

from sqlalchemy import desc

import config
from client.dianbo import DianboClient, EmailClient
from ext.mailbase import Message
from models import Resources, Location, Subscriber, session
from utils import singleton
from signals import send_update_email


@singleton
class DianBoTask:

    def __init__(self, crawl_client):
        self.crawl_client = crawl_client
        self.email_client = EmailClient(**config.HOST_EMAIL)
        self.fail_page_info = []
        self.fail_pan_info = []
        self.md5_dict = {}

    async def init_page_task(self):
        page_num = await self.crawl_client.process_page_number()
        for i in range(page_num):
            html = await self.crawl_client.process_html('{}/page/{}'.format(config.ROOT_URL_DIANBO_TVSHOW, i + 1))
            fail_task = await self.crawl_client.process_page_info(html)
            self.fail_page_info.extend(fail_task)

    async def init_pan_task(self):
        for uuid, original in session.query(Resources.uuid, Resources.original).all():
            html = await self.crawl_client.process_html(original)
            fail_task = await self.crawl_client.process_pan_info(html, uuid)
            self.fail_pan_info.extend(fail_task)

    # 获取网盘信息
    async def get_one_pan(self, resource_uuid, resource_url, update=True):
        html = await self.crawl_client.process_html(resource_url)
        fail_task = await self.crawl_client.process_pan_info(html, resource_uuid, update)
        if update:
            send_update_email.send(self, resource_id=resource_uuid)
        self.fail_pan_info.extend(fail_task)

    # 初始化变量
    async def init_env_var(self):
        for i, uuid, original in session.query(Resources.id, Resources.uuid, Resources.original).all():
            html = await self.crawl_client.process_html(original)
            file_name = './html/check_{}.html'.format(i)
            with open(file_name, 'w') as f:
                f.write(html)
        os.chdir('/home/chenggq/projects/api-show/')
        subprocess.check_output('git add . && git commit -m "update"', shell=True)

    # 检查所有资源是否更新
    async def update_pan_task(self):
        os.chdir('/home/chenggq/projects/api-show/')
        for i, uuid, original in session.query(Resources.id, Resources.uuid, Resources.original).all():
            html = await self.crawl_client.process_html(original)
            file_name = './html/check_{}.html'.format(i)
            with open(file_name, 'w') as f:
                f.write(html)
            output = subprocess.check_output('git diff', shell=True)
            output = output.decode(encoding="utf-8")
            if '百度网盘' in output:
                await self.get_one_pan(resource_uuid=uuid, resource_url=original, update=True)
            subprocess.call('git add . && git commit -m "update"', shell=True)

    # todo 重试错误信息
    async def _retry_error_page(self):
        while self.fail_page_info:
            page_info = self.fail_page_info.pop()
            resource = Resources(name=page_info[0], owner='电波字幕组',
                                 stype='tvshow', original=page_info[1])
            session.add(resource)
            try:
                session.commit()
            except Exception:
                session.rollback()
                self.fail_page_info.append(page_info)
        else:
            session.close()

    # todo 重试错误信息
    async def _retry_error_pan(self):
        while self.fail_pan_info:
            pan_info = self.fail_pan_info.pop()
            location = Location(episode=pan_info[0], url=pan_info[1], resource=pan_info[2])
            session.add(location)
            try:
                session.commit()
            except Exception:
                session.rollback()
                self.fail_pan_info.append(pan_info)
        else:
            session.close()

    def __repr__(self):
        return 'DianBoTask at {}'.format(id(self))


def init():
    loop = asyncio.get_event_loop()
    task = DianBoTask(DianboClient(root_url=config.ROOT_URL_DIANBO_TVSHOW, loop=loop))
    loop.run_until_complete(task.init_page_task())
    loop.run_until_complete(task.init_pan_task())
    loop.run_until_complete(task.init_env_var())
    loop.close()


def update():
    loop = asyncio.get_event_loop()
    task = DianBoTask(DianboClient(root_url=config.ROOT_URL_DIANBO_TVSHOW, loop=loop))
    loop.run_until_complete(task.update_pan_task())
    loop.close()


# 刚订阅时的邮件(会将所订阅资源的当季信息邮件通知)
async def init_email(nick_name, email, resource_ids):
    resource_list = []
    for resource_id in resource_ids.split(','):
        query = session.query(Resources.name, Location.url,
                              Location.episode, Location.password).\
            outerjoin(Location, Resources.uuid == Location.resource). \
            filter(Resources.uuid == resource_id).all()
        for i, item in enumerate(query, start=1):
            url = item.url
            name = item.name
            episode = item.episode
            password = item.password
            resource_list.append(name + episode + url + password)
    msg = Message(subject='资源列表', recipients=[(nick_name, email)],
                  sender=(config.HOST_EMAIL['nick_name'], config.HOST_EMAIL['username']))
    msg.body = '\n'.join(resource_list)
    try:
        email_client = EmailClient(**config.HOST_EMAIL)
        email_client.send(msg)
    except smtplib.SMTPDataError as e:
        return e.args


# 资源更新时的邮件(通过blinker信号触发)
@send_update_email.connect
def update_email(sender, **kw):
    resource_id = kw.pop('resource_id')
    latest = session.query(Resources.name, Location.episode,
                           Location.url, Location.password). \
        outerjoin(Location, Resources.uuid == Location.resource). \
        filter(Location.resource == resource_id). \
        order_by(desc(Location.create_time)).first()
    recipients = []
    query = session.query(Subscriber).filter(Subscriber.resources.contains(resource_id))
    for item in query:
        recipients.append((item.nick_name, item.email))
    msg = Message(subject='资源列表', recipients=recipients,
                  sender=(config.HOST_EMAIL['nick_name'], config.HOST_EMAIL['username']))
    msg.body = '{}-{}-{}-{}'.format(latest.name, latest.episode, latest.url, latest.password)
    try:
        email_client = EmailClient(**config.HOST_EMAIL)
        email_client.send(msg)
    except smtplib.SMTPDataError as e:
        return e.args
    except AssertionError:
        return


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    task = DianBoTask(DianboClient(root_url=config.ROOT_URL_DIANBO_TVSHOW, loop=loop))
    loop.run_until_complete(task.update_pan_task())
    # os.chdir('/home/chenggq/projects/api-show/')
    # subprocess.call('git add . && git commit -m "update"', shell=True)
