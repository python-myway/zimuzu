import pymysql

pymysql.install_as_MySQLdb()

HOST_EMAIL = {
    'nick_name': '共享俱乐部',
    'server': 'smtp.163.com',
    'username': 'xxx',
    'password': 'xxx',
    'port': 25,
}


ROOT_URL_DIANBO_TVSHOW = 'http://dbfansub.com/category/tvshow/'
ROOT_URL_DIANBO_MOVIE = 'http://dbfansub.com/category/movie/'


MYSQL = {
    'username': 'root',
    'password': '123456',
    'host': 'localhost',
    'db': 'zimuzu',
}


try:
    from local_config import *
except ImportError:
    pass
