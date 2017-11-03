

# https://pan.baidu.com/share/transfer?
# shareid=2900817894&
# from=4281066597&
# bdstoken=b82cc0dd499b8f968c743ecfabc0856f&
# channel=chunlei&
# clienttype=0&
# web=1&
# app_id=250528&
# logid=MTUwOTY5NTM3NDc2NzAuNzI3MTU4MjE3NDA3MTM1OA==

# https://pan.baidu.com/share/transfer?
# shareid=2900817894&
# from=4281066597&
# bdstoken=1b713dddca8d3e323e3adefdb85a5c31&
# channel=chunlei&
# clienttype=0&
# web=1&
# app_id=250528&
# logid=MTUwOTcwMDM1NzkxMDAuMzI2Njk3NjMxODI5NTUyMTQ=

# ! -*- coding:utf-8 -*-

'''
操作百度网盘，自动添加资源到网盘。
注意点：
爬取源码可以使用urllib2模块，不需要使用phantomjs，因为不需要执行js。
* 获取cookie（可以手动登录然后抓包获取）
* 首先爬取如：http://pan.baidu.com/s/1o8LkaPc页面，获取源码
* 解析源码，筛选出该页面分享资源的名称、shareid、from（uk)、bdstoken、appid（app_id）。
* 构造post包（用来添加资源到网盘），该包需要用到以上4个参数，当然还有一个最重要的就是cookie

在post包的url中还有一个logid参数，内容可以随便写，应该是个随机值然后做了base64加密。
在post包的payload中，filelist是资源名称，格式filelist=["/name.mp4"]，path为保存到那个目录下，格式path=/pathname
'''
__author__ = "nMask"
__Blog__ = "http://thief.one"
__Date__ = "20170412"

# import re
# import urllib as urllib2
# import argparse
#
# shareurl = ""
# filename = ""
# Cookie = ""
# path = "/"
# res_content = r'"app_id":"(\d*)".*"path":"([^"]*)".*"uk":(\d*).*"bdstoken":"(\w*)".*"shareid":(\d*)'  # 正则，获取参数值
# '''
# cookie可以通过登录账号访问百度分享地址后，手动添加资源时用fiddler抓包获取,格式如下：
#
# BAIDUID=C1015A10A3FC569A66923EEF:FG=1;
# BIDUPSID=C1015A10A3FC569A6612AA6EF;
# PSTM=149154382;
# PANWEB=1;
# bdshare_firstime=1497460316;
# BDCLND=vm6Tu2BF8x8%2BwNBLh3XUQD5sfKCUx;
# PSINO=5;
# H_PS_PSSID=22583_22161_1463_2110_17001_21673_22158;
# BDUSS=hqR2RSOVROVmNHREwtV29xVkhBQ3pUb3ZLZlkxM3JGcVFqdmMtY3kzaDlaQUFBJCQAAAAAAAAAAAEAAAA~cQc40NLUy7XEwbm359PwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADJR-FgyUfhYM2;
# STOKEN=69734c07f605e8d0bb09e5513d24497702a32e11029617f54fa3baaa2d9;
# SCRC=0c9e10560d1f5de23b2cf8c42c7484ef;
# Hm_lvt_7a3960b6f0eb0085b7f96ff5e660b0=1492047460,1492396138,1492396201,1492667545;
# Hm_lpvt_7a3960b6f06b0085b7f96ff5e660b0=1492668725;
# PANPSC=1004971751379968%3AWaz2A%2F7j1vWLfEj2viX%2BHu0oj%2BY%2FIsAxoXP3kWK6VuJ5936qezF2bVph1S8bONssvn6mlYdRuXIXUCPSJ19ROAD5r1J1nbMCUL3KDnLECfYjzPb5hCCEJfIbGeUDFmg5zwpdg9WqRKWDBCT3FjnL6jsjP%2FyZiBX26YfN4HZ4D76jyG3uDkPYshZ7OchQK1KQDQpg%2B6XCV%2BSJWX9%2F9F%2FIkt7vMgzc%2BT'
# '''
#
#
# class bdpanSpider:
#     def __init__(self):
#         self.p = re.compile(res_content)
#         self.app_id = ""
#         self.uk = ""
#         self.bdstoken = ""
#         self.shareid = ""
#         self.path = ""
#         self.headers = {
#             'Host': "pan.baidu.com",
#             'Accept': '*/*',
#             'Accept-Language': 'en-US,en;q=0.8',
#             'Cache-Control': 'max-age=0',
#             'Referer': 'https://pan.baidu.com/s/1kUOxT0V?errno=0&errmsg=Auth%20Login%20Sucess&&bduss=&ssnerror=0&',
#             'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
#             'Cookie': Cookie
#         }
#
#     def run(self, url):
#         self.getbody(url)  ##获取源码并分析
#         self.addziyuan()  ##添加资源到网盘
#
#     def getbody(self, url):
#         '''
#         获取分享页面源码
#         '''
#         try:
#             req = urllib2.Request(url, headers=self.headers)
#             f = urllib2.urlopen(req)
#             content = f.read()
#         except Exception as e:
#            print(str(e))
#         else:
#             '''
#             从源码中提取资源的一些参数
#             '''
#             L = self.p.findall(content)
#             if len(L) > 0:
#                 self.app_id = L[0][0]
#                 self.path = L[0][1]
#                 self.uk = L[0][2]
#                 self.bdstoken = L[0][3]
#                 self.shareid = L[0][4]
#
#     def addziyuan(self):
#         '''
#         添加该资源到自己的网盘
#         '''
#         url_post = "https://pan.baidu.com/share/transfer?shareid=" + self.shareid + "&from=" + self.uk + "&bdstoken=" + self.bdstoken + "&channel=chunlei&clienttype=0&web=1&app_id=" + self.app_id + "&logid=MTQ5MjA0ODExOTE0NTAuNjg1ODk3MTk4ODIyNDE2Mw=="
#         payload = "filelist=%5B%22" + self.path + "%22%5D&path=/"  # 资源名称与要保存的路径
#
#
# def main():
#     global Cookie, path, shareurl, filename
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-filename', help="name of the file to process")
#     parser.add_argument("-shareurl", help="add your shareurl")
#     parser.add_argument("-path", help="add your baidupan-path")
#     parser.add_argument("-cookie", help="add your baidupan-cookie")
#
#     args = parser.parse_args()
#
#     if args.cookie:
#         Cookie = args.cookie
#     else:
#         parser.print_help()
#         exit(0)
#     if args.path:
#         path = urllib.quote(args.path)
#     if args.shareurl:
#         shareurl = args.shareurl
#     elif args.filename:
#         filename = args.filename
#     else:
#         parser.print_help()
#         exit(0)

# https://passport.baidu.com/v2/api/?login

import requests, re

cookie_dict = {
    'BAIDUID': 'B02462F0E967B3BE977C1B92D8715A3B:FG=1',
    'BIDUPSID': 'B02462F0E967B3BE977C1B92D8715A3B',
    'PSTM': '1509698808',
    'H_PS_PSSID': '1458_21087_24879_24658_20929',
    'BDORZ': 'B490B5EBF6F3CD402E515D22BCDA1598',
    'PSINO': '6',
    'panlogin_animate_showed': '1',
    'FP_UID': 'c455a99435ec503f840a318052aff8c2',
    'FP_LASTTIME': '1509699050834',
    'PANWEB': '1',
    'STOKEN': '485e979394df99b7a8fd3f0e1521dd…bb259c3eb9e6ff4abfcac51b6c193',
    'SCRC': '1509757d7d18d38d1a3bf1df71e4a2e2',
    'PANPSC': '1471570388922983544:5Us+Crpocq…3uSEptKjxFhtDdWL2TL3bwxtQHr5H',
    'Hm_lvt_7a3960b6f067eb0085b7f96ff5e660b0': '1509699104,1509699524',
    'Hm_lpvt_7a3960b6f067eb0085b7f96ff5e660b0': '1509699524',
    'cflag': '15:3',
    'BDUSS': '2VaeFlNcHB-QXktWXJTQUNVVFpKUHN…AAAAAAAAAAAAAAAAABwv~FkcL~xZY',
    'pan_login_way': '1',
    'recommendTime': 'guanjia2017-11-02 21:40:00',

}

res_content = r'"app_id":"(\d*)".*"path":"([^"]*)".*"uk":(\d*).*"bdstoken":"(\w*)".*"shareid":(\d*)'


def get_pan():
    # login_url = ''
    # login = requests.post(login_url, data={'username': 13714522464, 'password': 'wxy20170620'}).cookies
    pattern = re.compile(res_content)
    session = requests.Session()
    # session.cookies = cookie_dict
    raw = session.get('https://pan.baidu.com/s/1c2Ipul6', stream=True).raw
    content = raw.read()
    # from urllib import request
    # import json
    # headers = {
    #     'Host': "pan.baidu.com",
    #     'Accept': '*/*',
    #     'Accept-Language': 'en-US,en;q=0.8',
    #     'Cache-Control': 'max-age=0',
    #     'Referer': 'https://pan.baidu.com/s/1kUOxT0V?errno=0&errmsg=Auth%20Login%20Sucess&&bduss=&ssnerror=0&',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    #     'Cookie': json.dumps(cookie_dict)
    # }
    # req = request.Request('https://pan.baidu.com/s/1c2Ipul6', headers=headers)
    # content = request.urlopen(req).read()
    L = pattern.findall(content)
    if len(L) > 0:
        app_id = L[0][0]
        path = L[0][1]
        uk = L[0][2]
        bdstoken = L[0][3]
        shareid = L[0][4]
        print([app_id, path, uk, bdstoken, shareid])


if __name__ == "__main__":
    get_pan()
