# ===================Telegram Bot===============================
# TODO 测试版
teltoken = '1473302982:AAH5HjAWjjimwL1xDNih7pfsZZ6BG2NUeTg'
# TODO 正式版
# teltoken = '1386154312:AAGhq_iROaCy0_99hWg-jNKmH0o16fH50K8'
# ====================Database==================================
# TODO　数据库
database = "binance_tg"
# TODO 数据表
t_table = "binance_tg_t"
# ==============================================================


# MySQL config
mysql_info = {
    "host": "35.241.121.76",
    "user": "root",
    "password": "Ep5rFww5PuMrtCxk",
    "database": database
}

connect_mysql = "mysql -h35.241.121.76 -uroot -pEp5rFww5PuMrtCxk"

failure = "\ud83e\udd7a"

win = "\ud83d\udcb0"

# ==================================================一下是测试代码======================================================

# 1605339476000
# 2020-11-14 15:37:56

import time
import pytz

ss = (time.time() + 60*60)*1000
tz = pytz.timezone('Asia/ShangHai')
dt = pytz.datetime.datetime.fromtimestamp(ss / 1000, tz)
time_ = str(dt.strftime('%Y-%m-%d %H:%M:%S'))
print(time_)