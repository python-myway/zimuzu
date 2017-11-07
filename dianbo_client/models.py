from uuid import uuid4
import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship


class MyBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    uuid = Column(String(50), default=uuid4(), primary_key=True)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)


Base = declarative_base(cls=MyBase)


class RefResourcesMixin:
    @declared_attr
    def resource_id(cls):
        return Column('resource_id', ForeignKey('resources.uuid'))

    @declared_attr
    def resources(cls):
        return relationship('Resources', back_populates=cls.__name__.lower())


subscriber_resources = Table('subscriber_resources', Base.metadata,
                             Column('subscriber_id', ForeignKey('subscriber.uuid'), primary_key=True),
                             Column('resources_id', ForeignKey('resources.uuid'), primary_key=True))


class Resources(Base):

    name = Column(String(255))
    owner = Column(String(255))
    stype = Column(String(255))
    subscriber = relationship('Subscriber', secondary=subscriber_resources, back_populates='resources')

    def __init__(self):
        pass

    def __repr__(self):
        pass


class Subscriber(Base):

    nick_name = Column(String(50))
    email = Column(String(50))
    resources = relationship('Resources', secondary=subscriber_resources, back_populates='subscriber')

    def __init__(self):
        pass

    def __repr__(self):
        pass


class Location(RefResourcesMixin, Base):

    episode = Column(Integer, default=1)
    url = Column(String(255))

    def __init__(self):
        pass

    def __repr__(self):
        pass


if __name__ == '__main__':
    from sqlalchemy import create_engine
    import pymysql

    pymysql.install_as_MySQLdb()
    engine = create_engine('mysql+pymysql://root:123456@localhost/zimuzu')
    Base.metadata.create_all(engine)
