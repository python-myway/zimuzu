import argparse

from tasks import *


# 初始化数据库
def init_db():
    from models import Base, engine
    try:
        Base.metadata.drop_all(engine)
    except Exception:
        pass
    Base.metadata.create_all(engine)


# 初始化数据
def init_data():
    init_page_task()
    init_env_var()
    init_pan_task()


# todo 命令行订阅，发邮件
def geek_subscribe():
    pass


# 执行更新命令
def update():
    pass


def main(func_name):
    func_dict = {
        'init_db': init_db,
        'init_data': init_data,
        'geek': geek_subscribe,
        'update': update,
    }
    func_dict.get(func_name)()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='命令行执行脚本')
    parser.add_argument('--func', type=str, help='选择要执行的函数')
    args = parser.parse_args()
    print(args)
    if args.func:
        main(args.func)
    else:
        print('请输入正确的函数执行')