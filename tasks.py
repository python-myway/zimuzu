import asyncio
import smtplib
from hashlib import md5

from blinker import signal
from sqlalchemy import desc

import config
from client.dianbo import DianboClient, EmailClient
from ext.mailbase import Message
from models import Resources, Location, Subscriber, session

send_update_email = signal('send_update_email')
md5_dict = {}
pan_url_dict = {}
fail_page_info = []
fail_pan_info = []


# 建立客户端实例
loop = asyncio.get_event_loop()
dianbo_client = DianboClient(root_url=config.ROOT_URL_DIANBO_TVSHOW, loop=loop)
email_client = EmailClient(**config.HOST_EMAIL)


# 初始化，拉取所有的资源信息
async def init_page_task():
    global fail_page_info
    page_num = await dianbo_client.process_page_number()
    for i in range(page_num):
        html = await dianbo_client.process_html('{}/page/{}'.format(config.ROOT_URL_DIANBO_TVSHOW, i+1))
        fail_task = await dianbo_client.process_page_info(html)
        fail_page_info.extend(fail_task)


# 获取所有初始化获取的资源的网盘信息
async def init_pan_task():
    global pan_url_dict, fail_pan_info
    for key, value in pan_url_dict.items():
        html = await dianbo_client.process_html(value)
        fail_task = await dianbo_client.process_pan_info(html, key)
        fail_pan_info.extend(fail_task)


# 重试所有错误的任务--页面信息
async def retry_error_page():
    global fail_page_info
    while fail_page_info:
        page_info = fail_page_info.pop()
        resource = Resources(name=page_info[0], owner='电波字幕组',
                             stype='tvshow', original=page_info[1])
        session.add(resource)
        try:
            session.commit()
        except Exception:
            session.rollback()
            fail_page_info.append(page_info)
    else:
        session.close()


# 重试所有错误的任务--网盘信息
async def retry_error_pan():
    global fail_pan_info
    while fail_pan_info:
        pan_info = fail_pan_info.pop()
        location = Location(episode=pan_info[0], url=pan_info[1], resource=pan_info[2])
        session.add(location)
        try:
            session.commit()
        except Exception:
            session.rollback()
            fail_pan_info.append(pan_info)
    else:
        session.close()


# 初始化模块的变量
async def init_env_var():
    global pan_url_dict, md5_dict
    for uuid, original in session.query(Resources.uuid, Resources.original).all():
        pan_url_dict[uuid] = original
        html = await dianbo_client.process_html(original)
        md5_dict[uuid] = md5(html)


# 获取网盘信息
async def get_one_pan(resource_uuid, resource_url, update=True):
    global fail_pan_info
    html = await dianbo_client.process_html(resource_url)
    fail_task = await dianbo_client.process_pan_info(html, resource_uuid, update)
    if update:
        send_update_email.send(resource_uuid)
    fail_pan_info.extend(fail_task)


# 检查单个是否更新最新集，或者是新加入的资源(未获取网盘信息)
async def check_update(resource_uuid):
    global pan_url_dict, md5_dict

    value = pan_url_dict[resource_uuid]
    html = await dianbo_client.process_html(value)
    md5_page = md5(html)
    try:
        old_md5 = md5_dict[resource_uuid]
        if old_md5 == md5_page:
            return False, 'update'
        else:
            md5_dict[resource_uuid] = md5_page
            return True, 'update'
    except KeyError:
        md5_dict[resource_uuid] = md5_page
        return True, 'new'


# 检查所有资源是否更新
async def update_pan_task():
    for uuid, original in pan_url_dict.items():
        status, update_or_new = await check_update(uuid)
        if not status:
            continue
        if update_or_new == 'update':
            get_one_pan(resource_uuid=uuid, resource_url=original, update=True)
        if update_or_new == 'new':
            get_one_pan(resource_uuid=uuid, resource_url=original, update=False)


# 刚订阅时的邮件(会将所订阅资源的当季信息邮件通知)
async def init_email(nick_name, email, resource_ids):
    resource_list = []
    for resource_id in resource_ids.split(','):
        query = session.query(Resources.name, Location.url).outerjoin(Location, Resources.uuid == Location.resource).\
            filter(Resources.uuid == resource_id).all()
        for i, item in enumerate(query, start=1):
            url = item.url
            name = item.name
            resource_list.append(name + '第' + str(i) + '集' + url)
    msg = Message(subject='资源列表', recipients=[(nick_name, email)],
                  sender=(config.HOST_EMAIL['nick_name'], config.HOST_EMAIL['username']))
    msg.body = '\n'.join(resource_list)
    try:
        email_client.send(msg)
    except smtplib.SMTPDataError as e:
        return e.args
    return


# 资源更新时的邮件(通过blinker库触发)
@send_update_email.connect
async def update_email(resource_id):
    latest = session.query(Resources.name, Location).\
        outerjoin(Location, Resources.uuid == Location.resource).\
        filter(Location.resource == resource_id).\
        order_by(desc(Location.create_time)).limit(1)
    recipients = []
    query = session.query(Subscriber).filter(Subscriber.resources.contains(resource_id))
    for item in query:
        recipients.append((item.nick_name, item.email))
    msg = Message(subject='资源列表', recipients=recipients,
                  sender=(config.HOST_EMAIL['nick_name'], config.HOST_EMAIL['username']))
    msg.body = '{}第{}集{}'.format(latest.name, latest.episode, latest.url)
    try:
        email_client.send(msg)
    except smtplib.SMTPDataError as e:
        return e.args
    return


if __name__ == '__main__':
    pass
