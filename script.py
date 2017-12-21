import argparse


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
    pass


# 命令行订阅，发邮件
def geek_subscribe():
    pass


# 执行更新命令
def update():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='命令行执行脚本')
    parser.add_argument('-func', "--function", type=callable,
                        choices=[init_db, init_data, geek_subscribe, update],
                        help='选择要执行的函数')
    args = parser.parse_args()
    if args.function:
        args.function()
    else:
        print('请输入正确的函数执行')
