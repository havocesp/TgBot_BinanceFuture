import hashlib
import hmac
from future.builtins import bytes
import time
import requests

# API 密钥：
# vWfJaeWvfmxcaMKcFa4BqVUmUEiQaLDfKfxPdFQnu34RGAhrAJUj2uPveFpqUFaA
# 密钥:
# Di2IJd7cNJfecQKqvgQXWytVX9c2DOJoIV6eQMyJWdPrTdAZnqvh19syjZsepiXd

#
# base_url = "https://api.binance.com"
# r_url = '/sapi/v1/capital/config/getall?timestamp={}'.format(round(time.time()*1000))
# secret = bytes("Di2IJd7cNJfecQKqvgQXWytVX9c2DOJoIV6eQMyJWdPrTdAZnqvh19syjZsepiXd",'utf8')
# message = bytes(r_url,'utf8')
# headers = {
#     "X-MBX-APIKEY": "vWfJaeWvfmxcaMKcFa4BqVUmUEiQaLDfKfxPdFQnu34RGAhrAJUj2uPveFpqUFaA",
#     "contentType": "application/x-www-form-urlencoded"
# }
# si = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
# print(hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest())
# rp = requests.get(base_url + r_url +"&signature={}".format(si), headers=headers)
# print(rp.text)


#coding:UTF-8
import time

#获取当前时间
print(time.time())
#转换成localtime
time_local = time.localtime(1605011004107/1000)
#转换成新的时间格式(2016-05-09 18:59:20)
dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(1605011004107/ 1000))

print(dt)

