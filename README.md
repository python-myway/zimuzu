
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
├── script.py  # 脚本文件
├── models.py  # 项目的数据表结构
├── tasks.py  # 任务文件
├── README.md  # 项目说明
├── requirements.txt  # 依赖包
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
git clone xxx
2. 在根目录下添加local_config.py文件，添加config.py中的个人配置
3. 在虚拟环境中安装依赖
4. 在本地的MySQL中添加zimuzu数据库
5. 执行脚本，初始化相关models
6. 执行脚本，初始化资源和网盘的信息
7. 启动后端代码
8. 在浏览器中打开index.html，查看效果
```

## TODO(更新中)
1. 优化邮件内容的格式
1. 任务使用huey框架(没有使用celery是因为太重了)
2. 前端使用vue优化下界面

## 问题&说明(更新中)



