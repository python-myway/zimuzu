import time
import asyncio
from asyncio import Queue

from blinker import signal
import aiohttp

from client.dianbo import DianboClient, EmailClient
from models.models import Resources, Location, session
from ext.mailbase import Message


original_url = signal('original_url')
signal_list = []


class Crawler:
    def __init__(self, max_redirect=10, max_tries=4, max_tasks=10, *, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.q = Queue(loop=self.loop)
        self.client = DianboClient()
        self.headers = {}
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers, loop=self.loop)
        return self._session

    def close(self):
        self.session.close()

    async def store_resource_link(self, response):
        pass

    async def store_pan_info(self, response):
        pass

    async def fetch(self, url, max_redirect):
        pass

    async def work(self):
        pass

    async def crawl(self):
        self.__workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        await self.q.join()
        await self.q.join()
        for w in self.__workers:
            w.cancel()


dianbo_client = DianboClient()
email_client = EmailClient('smtp.163.com', 'chengganqin@163.com', 'hunting##161201', 25)


# 初始化，拉取所有的资源信息
def init_task():
    tvshow = dianbo_client.get_all_tvshow()
    try:
        for item in tvshow:  # todo 这个地方很奇怪,要修正,深入了解yield用法
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


def get_signal(sender, changes):
    signal_list.extend(changes)


# 拉取网盘的信息
def init_pan_task():
    for uuid, original in session.query(Resources.uuid, Resources.original).all()[51:100]:
        for i, url in enumerate(dianbo_client.get_pan_info(original)):
            location = Location()
            location.resource = uuid
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


async def init_email(resource_ids):
    resource_list = []
    for resource_id in resource_ids:
        query = session.query(Resources.name, Location.url).outerjoin(Location, Resources.uuid == Location.resource).\
            filter(Resources.uuid == resource_id).all()
        for i, item in enumerate(query, start=1):
            url = item.url
            name = item.name
            resource_list.append(name + '第' + str(i) + '集' + url)
    msg = Message(subject='测试', recipients=[('test', '1612134263@qq.com')], sender=('test', 'chengganqin@163.com'))
    msg.body = '\n'.join(resource_list)
    email_client.send(msg)
    return


def update_email():
    pass


if __name__ == '__main__':
    # original_url.connect(get_signal)
    # init_task()
    # init_pan_task()
    init_email(['20604dbf-c524-11e7-a3e2-002324af93be', '20604e19-c524-11e7-a3e2-002324af93be'])
