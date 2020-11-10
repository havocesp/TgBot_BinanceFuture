import hashlib
import hmac
from future.builtins import bytes
import time
import requests

# API 密钥：
# vWfJaeWvfmxcaMKcFa4BqVUmUEiQaLDfKfxPdFQnu34RGAhrAJUj2uPveFpqUFaA
# 密钥:
# Di2IJd7cNJfecQKqvgQXWytVX9c2DOJoIV6eQMyJWdPrTdAZnqvh19syjZsepiXd


base_url = "https://api.binance.com"
r_url = '/sapi/v1/capital/config/getall&{}'.format(round(time.time()))
secret = bytes("Di2IJd7cNJfecQKqvgQXWytVX9c2DOJoIV6eQMyJWdPrTdAZnqvh19syjZsepiXd",'utf8')
message = bytes('GET /sapi/v1/capital/config/getall&{}'.format(round(time.time())),'utf8')
headers = {"X-MBX-APIKEY": "vWfJaeWvfmxcaMKcFa4BqVUmUEiQaLDfKfxPdFQnu34RGAhrAJUj2uPveFpqUFaA"}
si = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
print(hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest())
rp = requests.get(base_url + r_url +"&signature={}".format(si))
print(rp.text)