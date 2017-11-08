from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pymysql
from blinker import signal
from client.dianbo import DianboClient
from client.models import Resources, Location


pymysql.install_as_MySQLdb()
engine = create_engine('mysql+pymysql://root:123456@localhost/zimuzu?charset=utf8', encoding='utf-8')
Session = sessionmaker(bind=engine)
session = Session()
original_url = signal('original_url')
signal_list = []
dianbo_client = DianboClient()


# 初始化，拉取所有的资源信息
def init_task():
    tvshow = dianbo_client.get_all_tvshow()
    try:
        temp_list = iter(tvshow)
        for item in temp_list:  # todo 这个地方很奇怪,要修正,深入了解yield用法
            for item_ in item:
                resource = Resources()
                resource.name = item_.name
                resource.original = item_.original
                resource.stype = 'tvshow'
                resource.owner = '电波字幕组'
                session.add(resource)
        try:
            session.commit()
            # try:
            #     d = session._model_changes
            #     if d:
            #         original_url.send('original_url', list(d.values()))  # todo 信号发送不成功，深入了解blinker用法
            #         d.clear()
            # except AttributeError:
            #     pass
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

    # for change in signal_list:
    #     for i, url in enumerate(dianbo_client.get_pan_info(change.__dict__['original'])):
    #         location = Location()
    #         location.resource = change.__dict__['uuid']
    #         location.url = url
    #         location.episode = i + 1
    #         session.add(location)
    # try:
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    #     print(e.args)
    for uuid, original in session.query(Resources.uuid, Resources.original).all():
        for i, url in enumerate(dianbo_client.get_pan_info(original)):
            location = Location()
            location.resource = uuid
            location.url = url
            location.episode = i + 1
            session.add(location)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(e.args)


if __name__ == '__main__':
    # original_url.connect(get_signal)
    # init_task()
    init_pan_task()
