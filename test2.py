# #!/usr/bin/python
#coding=utf-8
import requests
s = requests.session()
# from urllib import urlencode
# postData = {'_xsrf':'10758fdd2ab8d7747e88e28d5eae1b5f',
#             'password':'****',
#             'email':'373473032@qq.com',
#             'remember_me':'true',
#             }
# header = {
#         'User-Agent': "Dalvik/1.6.0 (Linux; U; Android 4.4.2; MX4 Build/KOT49H)",
#         'Host': "api.anzhuo.cn",
#         'appKey':'ZU349E79LUeZDkTbf',
#         'If-Modified-Since':'Mon, 28 Sep 2015 08:36:32 GMT+00:00',
#         'If-None-Match':'-1550145124',
#         'Connection':'Keep-Alive',
#         'Accept-Encoding':'gzip'
#         'Referer': "http://www.zhihu.com/",
#         'X-Requested-With': "XMLHttpRequest"
#     }
# # cookies={"q_c1":"004419b35af044458e3feb91b783fa39|1435552839000|1420703219000",
# # "_xsrf":"10758fdd2ab8d7747e88e28d5eae1b5f",
# # "__utmz":"51854390.1437969067.17.14.utmcsr=baidu|utmccn=(organic)|utmcmd=organic",
# # "__utmv":"51854390.100-1|2=registration_date=20150208=1^3=entry_date=20150108=1",
# # "__utmc":"51854390",
# # "__utmb":"51854390.40.10.1437993108",
# # "__utma":"51854390.81077950.1420703218.1437976996.1437993108.19",
# # "_ga":"GA1.2.81077950.1420703218",
# # "_za":"839ccada-5df4-48af-bc47-8ab7672ca0c1",
# # "cap_id":"MDZmNDk0ZDNmOTZhNDAwNmI1ZWFmN2M0YTU1NWEyMDI=|1436417608|47f7dd869b48f3fcc4eef91d8fcca4fcbea50916",
# # "__utmt":"1",}
# #post 换成登录的地址，



from pyquery import PyQuery as pq
import re
def wandoujia(x):
  if x.startswith('org.wandoujia'):
    appstoreUrl="https://itunes.apple.com/cn/app/id"+str(x[14:])
    r=s.get(appstoreUrl).content
    responseData=pq(r)
    appstoreEdition=responseData("span[itemprop='softwareVersion']").text()
    Edition.append(appstoreEdition+"\n")
  else:
    wandoujiaUrl="http://www.wandoujia.com/apps/"+str(x)
    r=s.get(wandoujiaUrl).content
    pattern = re.compile(r'<dt>版本</dt>[\s\S]*?<dd>([\s\S]*?)</dd>')
    match = pattern.search(r)
    if match:
      wandoujiaEdition= match.group(1)
      Edition.append(wandoujiaEdition+"\n")
    else:
      Edition.append("None\n")


def googleplay(x):
  googleplayUrl="https://play.google.com/store/apps/details?id="+str(x)
  r=s.get(googleplayUrl)
  responseData=pq(r.content)
  googleplayEdition=responseData("div.details-section-contents")("div.content[itemprop='softwareVersion']").text()
  if googleplayEdition=="":
    Edition.append("None\n")
  else:
    Edition.append(googleplayEdition+"\n")

def appstore(x):
  if x.startswith('org.wandoujia'):
    appstoreUrl="https://itunes.apple.com/cn/app/id"+str(x[14:])
    r=s.get("https://itunes.apple.com/cn/app/id373067909").content
    responseData=pq(r)
    appstoreEdition=responseData("span[itemprop='softwareVersion']").text()
    if appstoreEdition=="":
      Edition.append("None\n")
    else:
      Edition.append(appstoreEdition+"\n")
    print  appstoreEdition
  else:
    Edition.append(appstoreEdition+"\n")
  print  appstoreEdition


packagelist="""com.suryani.jiagallery
com.brixd.wallpager
com.sleepnova.punapp
cc.fotoplace.app
com.yyets.zimuzu
com.mandongkeji.comiclover
org.wandoujia.373067909
com.china.app.bbsandroid
org.wandoujia.1013793052
com.qinker.qinker"""
Edition=[]
packagelist=raw_input("请输入需要抓取的包名：")
# for x in packagelist.split("\n"):
#   wandoujia(x)
# print "".join(Edition)
print packagelist
