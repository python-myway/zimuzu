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

    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(String(50), default=gen_uuid)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)


Base = declarative_base(cls=MyBase)
engine = create_engine('mysql+pymysql://root:123456@localhost/zimuzu?charset=utf8', encoding='utf-8')
Session = sessionmaker(bind=engine)
session = Session()


class Resources(Base):
    name = Column(String(255))  # 名称
    owner = Column(String(255))  # 所属的字幕组
    stype = Column(String(255))  # 类型，目前有music，movie，tvshow
    original = Column(String(255))  # 原始的url

    def __repr__(self):
        pass


class Subscriber(Base):
    nick_name = Column(String(50))  # 昵称
    email = Column(String(50))  # 邮箱
    resources = Column(String(255))  # 订阅的资源

    def __repr__(self):
        pass


class Location(Base):
    episode = Column(Integer, default=1)  # 集数
    url = Column(String(255))
    resource = Column(String(50))  # 对应资源的UUID

    def __repr__(self):
        pass


if __name__ == '__main__':
    try:
        Base.metadata.drop_all(engine)
    except Exception:
        pass
    Base.metadata.create_all(engine)
