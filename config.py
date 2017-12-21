import sys


sys.modules["MySQLdb"] = sys.modules["_mysql"] = sys.modules["pymysql"]


HOST_EMAIL = {
    'nick_name': 'zinuzu',
    'server': 'smtp.163.com',
    'username': 'your@email.address',
    'password': 'your-email-password',
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
