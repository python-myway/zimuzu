from uuid import uuid1
import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship


def gen_uuid():
    return str(uuid1())


class MyBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(String(50), default=gen_uuid)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)


Base = declarative_base(cls=MyBase)


# class RefResourcesMixin:
#     @declared_attr
#     def resource_id(cls):
#         return Column('resource_id', ForeignKey('resources.uuid'))
#
#     @declared_attr
#     def resources(cls):
#         return relationship('Resources', back_populates=cls.__name__.lower())


# subscriber_resources = Table('subscriber_resources', Base.metadata,
#                              Column('subscriber_id', ForeignKey('subscriber.uuid'), primary_key=True),
#                              Column('resources_id', ForeignKey('resources.uuid'), primary_key=True))


class Resources(Base):

    name = Column(String(255))  # 名称
    owner = Column(String(255))  # 所属的字幕组
    stype = Column(String(255))  # 类型，目前有music，movie，tvshow
    original = Column(String(255))  # 原始的url

    def __init__(self):
        pass

    def __repr__(self):
        pass


class Subscriber(Base):

    nick_name = Column(String(50))  # 昵称
    email = Column(String(50))  # 邮箱
    resources = Column(String(255))  # 订阅的资源

    def __init__(self):
        pass

    def __repr__(self):
        pass


class Location(Base):

    episode = Column(Integer, default=1)  # 集数
    url = Column(String(255))
    resource = Column(String(50))  # 对应资源的UUID

    def __init__(self):
        pass

    def __repr__(self):
        pass


if __name__ == '__main__':
    from sqlalchemy import create_engine
    import pymysql

    pymysql.install_as_MySQLdb()
    engine = create_engine('mysql+pymysql://root:123456@localhost/zimuzu?charset=utf8', encoding='utf-8')
    try:
        Base.metadata.drop_all(engine)
    except Exception:
        pass
    Base.metadata.create_all(engine)
