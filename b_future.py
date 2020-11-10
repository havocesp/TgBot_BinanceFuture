import logging
from time import time

import pytz
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, ShippingQueryHandler
from config import SKey, PKey, teltoken, telChanel
from futures import send_signed_request

from sql_config import insert_data, select_data

from config import user_info

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


bind_enable = False


def tg_bot_send_text(message, user_id):
    """
    To send message
    """
    send_text = 'https://api.telegram.org/bot' + teltoken + '/sendMessage?chat_id=' + str(user_id) + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)
    return response.json()


def tg_start(update, context):
    """
    Telegram bot beginning
    """
    update.message.reply_text("Welcome to use Trading bot!")
    pass


def tg_help(update, context):
    """
    Telegram bot help
    """
    description_str = "/help = 查看所有命令\n" \
                      "/balance = 查看账户余额\n" \
                      "/orders = 查询所有订单\n" \
                      "/bind = 绑定交易所API"
    update.message.reply_text(description_str)
    pass


def tg_bind_command(update, context):
    """
    Bind binance API switch
    """
    global bind_enable
    bind_enable = True
    tg_bot_send_text("请输入向相关密钥！", update.message.from_user.id)


def bind_b_api(update, context):
    """
    Bind binance API
    """
    user_id = update.message.from_user.id
    api_info = update.message.text.strip().replace(" ", "")
    if len(api_info) < 128:
        return
    api_info_list = api_info.split('\n')
    # 绑定用户信息到数据库
    insert_sql = "insert into binance_tg(tg_id, b_api_key, b_secret_key, tg_token) " \
                  "value(%s, '%s', '%s', '%s')" % (user_id, api_info_list[0], api_info_list[1], teltoken.replace(":", ""))
    print(insert_sql)
    result = insert_data(insert_sql)
    if result:
        success_str = "Bind API succeed"
        tg_bot_send_text(success_str, user_id)
    else:
        failure_str = "Bind API failure, please try again!"
        tg_bot_send_text(failure_str, user_id)


def b_balance(update, context):
    """
    Get binance account balance info
    """
    # 检查用户ID
    user_id = update.message.from_user.id
    select_sql = "select b_api_key, b_secret_key from binance_tg where tg_id={}".format(user_id)
    results = select_data(select_sql)
    if not results:
        print("不是注册的用户！")
        return
    balance_info = send_signed_request('GET', '/fapi/v2/balance', results[0])
    if len(balance_info) != 0:
        print(balance_info[0])
        for balance in balance_info:
            if float(balance["balance"]) <= 0.0:
                continue
            asset = balance['asset']  # 资产
            total_balance = balance['balance']  # 总余额
            crossWalletBalance = balance['crossWalletBalance']  # 全仓余额
            crossUnPnl = balance['crossUnPnl']  # 全仓未实现盈亏
            availableBalance = balance['availableBalance']  # 可用余额
            maxWithdrawAmount = balance['maxWithdrawAmount']  # 最大可转出余额

            send_str = "资产：{}\n" \
                       "总余额：{}\n" \
                       "全仓余额：{}\n" \
                       "全仓未实现盈亏：{}\n" \
                       "可用余额：{}\n" \
                       "最大可转出余额：{}".format(asset, total_balance, crossWalletBalance,
                                           crossUnPnl, availableBalance, maxWithdrawAmount)
            update.message.reply_text(send_str)
    else:
        update.message.reply_text("您的资产正在结算中，请稍后重试！")


def b_orders(update, context):
    """
    Get binance history orders
    """
    # 检查用户ID
    user_id = update.message.from_user.id
    select_sql = "select b_api_key, b_secret_key from binance_tg where tg_id={}".format(user_id)
    results = select_data(select_sql)
    if not results:
        return
    all_symbols = send_signed_request('GET', '/fapi/v2/account', results[0])
    if all_symbols:
        all_symbols = all_symbols["positions"]
        for symbol in all_symbols:
            # 没有持仓的去掉
            # if float(symbol['entryPrice']) == 0.0:
            #     continue
            history_orders = send_signed_request('GET', '/fapi/v1/allOrders', {'symbol': symbol['symbol']})
            if not history_orders:
                continue
            # 排序
            # history_orders.sort(key=lambda k: (k.get('time', 0)))
            # 获取持有的币种的最后五笔订单
            history_orders = history_orders[-5:]
            for info in history_orders:
                orderId = info['orderId']  # 订单ID
                symbol = info['symbol']  # 交易对
                avgPrice = info['avgPrice']  # 平均成交价
                executedQty = info['executedQty']  # 成交量
                cumQuote = info['cumQuote']  # 成交金额
                side = info['side']  # 买卖方向
                status = info['status']  # 订单状态
                time_ = info['time']  # 下单时间
                # 超过一天订单去除
                if time() - time_/1000 > 12*60*60:
                    continue
                # 转换时区
                tz = pytz.timezone('Asia/ShangHai')
                dt = pytz.datetime.datetime.fromtimestamp(time_/1000, tz)
                dt.strftime('%Y-%m-%d %H:%M:%S')
                order_info_str = "订单ID：{}\n" \
                                 "交易对：{}\n" \
                                 "平均成交价：{}\n" \
                                 "成交量：{}\n" \
                                 "成交金额：{}\n" \
                                 "买卖方向：{}\n" \
                                 "订单状态：{}\n" \
                                 "下单时间：{}".format(orderId, symbol, avgPrice,
                                                  executedQty, cumQuote, side, status,
                                                  dt)
                # 推送到指定用户
                update.message.reply_text(order_info_str)
    else:
        update.message.reply_text("您还未发生交易，暂无订单信息！")


def tg_error(update, context):
    # Log Errors caused by Updates.
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """
    Start the bot
    """
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    updater = Updater(teltoken, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", tg_start))
    dp.add_handler(CommandHandler("help", tg_help))
    dp.add_handler(CommandHandler("balance", b_balance))
    dp.add_handler(CommandHandler("orders", b_orders))
    dp.add_handler(CommandHandler("bind", tg_bind_command))
    dp.add_handler(MessageHandler(Filters.text, bind_b_api))

    # log all errors
    dp.add_error_handler(tg_error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()


if __name__ == '__main__':
    main()
