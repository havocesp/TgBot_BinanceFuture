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



ss = [{'time':100}, {'time':90}]
for i in range(len(ss)):
    del ss[0]
print(ss)