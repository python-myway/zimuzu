
## 项目说明
### 项目初衷
1. 整合网上字幕组的资源，节省自己追剧的时间
2. 练习Python异步编程
3. 练习Sanic扩展

### 功能说明(更新中)
1. 订阅剧集，每周剧集更新，会将更新的内容邮件通知

### 代码结构
```
├── app.py  # 项目后端接口
├── config.py  # 配置文件
├── index.html  # 前端页面
├── scripts.py  # 脚本文件
├── models.py  # 项目的数据表结构
├── tasks.py  # 任务文件
├── signals.py  # 主要信号
├── utils.py  # 有用的插件
├── README.md  # 项目说明
├── requirements.txt  # 依赖包
│
├── tests  # 测试
│   ├── test_tasks.py
│
├── client  # 各种字幕组的客户端
│   ├── __init__.py
│   ├── base.py
│   ├── dianbo.py
│   ├── email.html
│   ├── log.py
│
├── ext  # 为Sanic框架的扩展，大部分是从Flask扩展中copy过来的
│   ├── __init__.py
│   ├── jsonbase.py
│   ├── log.py
│   ├── mailbase.py
│   ├── modelbase.py
│   ├── reloader.py
│   ├── resp.py
│   ├── schemabase.py
│   └── utils.py
│ 
├── deploy  # 部署相关的文件
    └── cron.conf
    
```

## 技术栈(更新中)
- Sanic
- SQLALchemy(PyMySQL)
- aiohttp
- BootstrapTable

## 本地开发

```
1. fork项目，并克隆到本地
git clone https://github.com/python-myway/zimuzu.git

2. 在根目录下添加local_config.py文件，添加config.py中的个人配置
vim local_config.py

3. 在虚拟环境中安装依赖
pip install -r requirements.txt

4. 在本地的MySQL中添加zimuzu数据库
mysql && CREATE SCHEMA `zimuzu` DEFAULT CHARACTER SET utf8;

5. 执行脚本，初始化相关models
python script.py --func init_db

6. 执行脚本，初始化资源和网盘的信息
python script.py --func init_data

7. 启动后端代码
python app.py

8. 在浏览器中打开index.html，查看效果
```

## TODO(更新中)
1. 优化邮件内容的格式
2. 前端使用vue优化下界面

## 问题&说明(更新中)
- 问题1
```
ERROR:asyncio:Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x7fc359a84f28>
```

- 问题2
```
RuntimeWarning: coroutine 'DianBoTask.get_one_pan' was never awaited
```

- 问题3
```
ImportError: cannot import name 'SIGTERM'

原因：在项目中命名了一个signal.py的文件，覆盖了标准库的signal.py，导致sanic在导入时出错
```




