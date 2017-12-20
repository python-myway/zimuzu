import smtplib
import asyncio
from asyncio import Queue
from hashlib import md5

import requests
from blinker import signal
import aiohttp

from client.dianbo import DianboClient, EmailClient
from models.models import Resources, Location, session
from ext.mailbase import Message


original_url = signal('original_url')
signal_list = []
md5_dict = {}
url_dict = {}

dianbo_client = DianboClient()
email_client = EmailClient('smtp.163.com', 'xxx', 'xxx', 25)


# 初始化，拉取所有的资源信息
def init_task():
    tvshow = dianbo_client.get_all_tvshow()
    while True:
        try:
            item = next(tvshow)
            for item_ in item:
                resource = Resources()
                resource.name = item_.name
                resource.original = item_.original
                resource.stype = 'tvshow'
                resource.owner = '电波字幕组'
                session.add(resource)
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                session.close()
                print(e.args)
        except StopIteration:
            session.close()
            print('ok')
            break


def get_signal(sender, changes):
    signal_list.extend(changes)


def init_pan_task():
    global url_dict
    for key, value in url_dict.items():
        for i, url in enumerate(dianbo_client.get_pan_info(value)):
            location = Location()
            location.resource = key
            location.url = url
            location.episode = i + 1
            session.add(location)
        try:
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            print(e.args)
    print('ok')


def init_env_var():
    global url_dict, md5_dict
    for uuid, original in session.query(Resources.uuid, Resources.original).all():
        url_dict[uuid] = original
        md5_dict[uuid] = md5(requests.get(original).content)


def get_one_pan(resource_uuid, resource_url, update=True):
    if update:
        pan_info = [dianbo_client.get_pan_info(resource_url)[-1]]
        episode = len(dianbo_client.get_pan_info(resource_url))
    else:
        pan_info = dianbo_client.get_pan_info(resource_url)
        episode = 0

    for i, url in enumerate(pan_info):
        location = Location()
        location.resource = resource_uuid
        location.url = url
        location.episode = episode or i + 1
        session.add(location)
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
        print(e.args)


def check_update(resource_uuid):
    global url_dict, md5_dict

    value = url_dict[resource_uuid]
    md5_page = md5(requests.get(value).content)
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


def update_pan_task():
    for uuid, original in url_dict.items():
        status, update_or_new = check_update(uuid)
        if not status:
            continue
        if update_or_new == 'update':
            get_one_pan(resource_uuid=uuid, resource_url=original, update=True)
        if update_or_new == 'new':
            get_one_pan(resource_uuid=uuid, resource_url=original, update=False)


async def init_email(nick_name, email, resource_ids):
    resource_list = []
    for resource_id in resource_ids.split(','):
        query = session.query(Resources.name, Location.url).outerjoin(Location, Resources.uuid == Location.resource).\
            filter(Resources.uuid == resource_id).all()
        for i, item in enumerate(query, start=1):
            url = item.url
            name = item.name
            resource_list.append(name + '第' + str(i) + '集' + url)
    msg = Message(subject='资源列表', recipients=[(nick_name, email)], sender=('test', 'chengganqin@163.com'))
    msg.body = '\n'.join(resource_list)
    try:
        email_client.send(msg)
    except smtplib.SMTPDataError as e:
        return e.args
    return


async def update_email():
    pass


if __name__ == '__main__':
    get_one_pan('dd0def6a-d4de-11e7-b4ae-002324af93be', 'http://dbfansub.com/tvshow/10592.html', update=False)
