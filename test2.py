#!/usr/bin/python
#coding=utf-8
import requests

s = requests.session()
# postData = {'_xsrf':'10758fdd2ab8d7747e88e28d5eae1b5f',
#             'password':'****',
#             'email':'373473032@qq.com',
#             'remember_me':'true',
#             }
header = {
        'User-Agent': "Dalvik/1.6.0 (Linux; U; Android 4.4.2; MX4 Build/KOT49H)",
        'Host': "api.anzhuo.cn",
        'appKey':'ZU349E79LUeZDkTbf',
        'If-Modified-Since':'Mon, 28 Sep 2015 08:36:32 GMT+00:00',
        'If-None-Match':'-1550145124',
        'Connection':'Keep-Alive',
        'Accept-Encoding':'gzip'
        # 'Referer': "http://www.zhihu.com/",
        # 'X-Requested-With': "XMLHttpRequest"
    }
# cookies={"q_c1":"004419b35af044458e3feb91b783fa39|1435552839000|1420703219000",
# "_xsrf":"10758fdd2ab8d7747e88e28d5eae1b5f",
# "__utmz":"51854390.1437969067.17.14.utmcsr=baidu|utmccn=(organic)|utmcmd=organic",
# "__utmv":"51854390.100-1|2=registration_date=20150208=1^3=entry_date=20150108=1",
# "__utmc":"51854390",
# "__utmb":"51854390.40.10.1437993108",
# "__utma":"51854390.81077950.1420703218.1437976996.1437993108.19",
# "_ga":"GA1.2.81077950.1420703218",
# "_za":"839ccada-5df4-48af-bc47-8ab7672ca0c1",
# "cap_id":"MDZmNDk0ZDNmOTZhNDAwNmI1ZWFmN2M0YTU1NWEyMDI=|1436417608|47f7dd869b48f3fcc4eef91d8fcca4fcbea50916",
# "__utmt":"1",}
#post 换成登录的地址，
r=s.get('http://www.speckyboy.com/wp-content/plugins/mobiloud-mobile-app-plugin/posts.php/');
#换成抓取的地址
# print r.content
from flask import session
print help(session)

