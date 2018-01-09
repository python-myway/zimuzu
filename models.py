from uuid import uuid1
import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker


def gen_uuid():
    return str(uuid1())


class MyBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # todo 在此处写的comment，并没有在创建数据表的时候写出来,sqlalchemy2版本实现了这个功能
    id = Column(Integer, autoincrement=True, primary_key=True, comment='ID')
    uuid = Column(String(50), default=gen_uuid, comment='UUID')
    create_time = Column(DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now, comment='更新时间')


Base = declarative_base(cls=MyBase)
engine = create_engine('mysql+pymysql://root:123456@localhost/zimuzu?charset=utf8', encoding='utf-8')
Session = sessionmaker(bind=engine)
session = Session()


class Resources(Base):
    name = Column(String(255), comment='名称')
    owner = Column(String(255), comment='所属的字幕组')
    stype = Column(String(255), comment='类型，目前有music，movie，tvshow')
    original = Column(String(255), comment='原始的url')

    def __repr__(self):
        pass


class Subscriber(Base):
    nick_name = Column(String(50), comment='昵称')
    email = Column(String(50), comment='邮箱')
    resources = Column(String(255), comment='订阅的资源')

    def __repr__(self):
        pass


class Location(Base):
    episode = Column(String(50), comment='集数')
    url = Column(String(255), comment='url地址')
    resource = Column(String(50), comment='对应资源的UUID')
    password = Column(String(50), comment='百度网盘的密码')

    def __repr__(self):
        pass


if __name__ == '__main__':
    import pymysql
    pymysql.install_as_MySQLdb()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
