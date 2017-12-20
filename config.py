import sys


sys.modules["MySQLdb"] = sys.modules["_mysql"] = sys.modules["pymysql"]


try:
    from local_config import *
except ImportError:
    pass
