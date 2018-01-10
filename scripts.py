from datetime import datetime
import argparse

from tasks import init, update
import config


# 初始化数据库
def init_db():
    from models import Base, engine
    try:
        Base.metadata.drop_all(engine)
    except Exception:
        pass
    Base.metadata.create_all(engine)


# 定时任务
def update_db():
    update_config = config.UPDATE_DB
    while True:
        time_now = datetime.now()
        hour = time_now.hour
        minute = time_now.minute
        second = time_now.second
        if update_config[0] == hour and update_config[1] == minute and update_config[2] == second:
            print(update_config)
            update()


def main(func_name):
    func_dict = {
        'init_db': init_db,
        'init_data': init,
        'update': update_db,
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
