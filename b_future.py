import logging
from time import time

import pytz
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import teltoken, t_table, win
from futures import send_signed_request

from sql_config import insert_data, select_data


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bind_enable = False


def tg_bot_send_text(message, user_id):
    """
    To send message
    """
    send_text = 'https://api.telegram.org/bot' + teltoken + '/sendMessage?chat_id=' + \
                str(user_id) + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)
    return response.json()


def tg_start(update, context):
    """
    Telegram bot beginning
    """
    update.message.reply_text("Welcome to use Trading bot!")
    description_str = "/help = 查看命令\n" \
                      "/balance = 查询余额\n" \
                      "/orders = 查询订单\n" \
                      "/bind = 绑定API"
    update.message.reply_text(description_str)
    pass


def tg_help(update, context):
    """
    Telegram bot help
    """
    description_str = "/help = 查看命令\n" \
                      "/balance = 查询余额\n" \
                      "/orders = 查询订单\n" \
                      "/bind = 绑定API"
    update.message.reply_text(description_str)
    pass


def tg_bind_command(update, context):
    """
    Bind binance API switch
    """
    # 绑定唯一API
    # user_id = update.message.from_user.id
    # select_sql = "select b_api_key, b_secret_key from " + t_table +" where tg_id={}".format(user_id)
    # results = select_data(select_sql)
    # if results:
    #     print("用户已存在！")
    #     update.message.reply_text("您已经绑定过API，无需重复绑定！")
    #     return
    global bind_enable
    bind_enable = True
    update.message.reply_text("请输入相关API！")


def bind_b_api(update, context):
    """
    Bind binance API
    """
    user_id = update.message.from_user.id
    api_info = update.message.text.strip().replace(" ", "")
    if len(api_info) < 128:
        return
    # 对输入API进行处理
    api_info_list = api_info.split('\n')
    if len(api_info) < 3:
        return
    # 查询当前API是否被绑定
    select_sql = "select * from " + t_table +" where b_api_key='{}'".format(api_info_list[1])
    results = select_data(select_sql)
    if results:
        update.message.reply_text("此API已经被绑定！")
        return

    # 绑定用户信息到数据库
    insert_sql = "insert into " + t_table + "(tg_id, api_lable, b_api_key, b_secret_key, tg_token) " \
                 "value(%s, '%s','%s', '%s', '%s')" % \
                 (user_id, api_info_list[0], api_info_list[1], api_info_list[2], teltoken)
    result = insert_data(insert_sql)
    if result:
        success_str = "绑定成功。"
        update.message.reply_text(success_str)
    else:
        failure_str = "绑定失败，请重试。"
        update.message.reply_text(failure_str)
    global bind_enable
    bind_enable = False


def b_balance(update, context):
    """
    Get binance account balance info
    """
    # 检查用户ID
    user_id = update.message.from_user.id
    select_sql = "select b_api_key, b_secret_key,api_lable from " + t_table +" where tg_id={}".format(user_id)
    results = select_data(select_sql)
    if not results:
        update.message.reply_text("请先绑定API")
        return
    total_usdt = "0USDT"
    total_bnb = "0BNB"
    account_total = 0.0
    update.message.reply_text("资产核算中，请稍后。")
    for u_api in results:
        account_info = send_signed_request('GET', '/fapi/v2/account', u_api)
        totalWalletBalance = account_info['totalWalletBalance']  # 账户总余额
        account_total += float(totalWalletBalance)
        send_str = ""
        for asset in account_info['assets']:
            currency = asset['asset']  # 币种
            walletBalance = asset['walletBalance']  # 余额
            # 币种相加
            if total_usdt.endswith(currency.upper()):
                total_usdt = str(float(total_usdt.replace("USDT", "")) + float(walletBalance)) + "USDT"
            elif total_bnb.endswith(currency.upper()):
                total_bnb = str(float(total_bnb.replace("BNB", "")) + float(walletBalance)) + "BNB"
            send_str += "{} {}\n".format(walletBalance, currency)
        send_str = "账户：{}\n".format(u_api[2] or "User") + send_str
        update.message.reply_text(send_str)
    # 发送余额
    update.message.reply_text("全部账户共计总额：\n{} USDT \ud83d\udcb0\n{} BNB \ud83d\udcb0".format(round(float(account_total), 5), round(float(total_bnb.replace("BNB", "")), 5)))


def zh_order_type(flag):
    """
    订单类型
    """
    if flag:
        return "限价"
    else:
        return "市价"


def zh_order_position(order_s):
    """
    持仓方向
    """
    if order_s:
        return "买单"
    else:
        return "卖单"


def b_orders(update, context):
    """
    Get binance history orders
    """
    have_order = False
    # 检查用户ID
    user_id = update.message.from_user.id
    select_sql = "select b_api_key, b_secret_key, api_lable from " + t_table +" where tg_id={}".format(user_id)
    results = select_data(select_sql)
    if not results:
        update.message.reply_text("请先绑定API")
        return
    # 友情提示
    update.message.reply_text("订单查询中，请耐心等待。")
    for result in results:
        all_symbols = send_signed_request('GET', '/fapi/v2/account', result)  # 查询账户交易对
        # all_symbols = send_signed_request('GET', '/fapi/v1/openOrders', results[0])  # 所有挂单
        if all_symbols:
            all_symbols = all_symbols["positions"]
            for symbol in all_symbols:
                # ======================================================================================================
                # 没有持仓的去掉
                # if float(symbol['entryPrice']) == 0.0:
                #     continue
                # symbol_ = symbol['symbol']  # 交易对
                # positionAmt = symbol['positionAmt']  # 持仓数量
                # entryPrice = symbol['entryPrice']  # 持仓成本价
                # unrealizedProfit = symbol['unrealizedProfit']  # 持仓未实现盈亏
                # positionType = "多单"
                # if float(positionAmt) < 0:
                #     positionType = "空单"
                # order_info_str = "账户：{}\n" \
                #                  "交易对：{}\n" \
                #                  "持仓方式：{}\n" \
                #                  "持仓数量：{}\n" \
                #                  "持仓均价：{}\n" \
                #                  "持仓未实现盈亏：{}" .format(result[2], symbol_.replace("USDT", "_USDT"), positionType,
                #                                       positionAmt, entryPrice, unrealizedProfit)
                # # 推送到指定用户
                # update.message.reply_text(order_info_str)
                # ======================================================================================================
                # 获取每个交易对的历史记录
                history_orders = send_signed_request('GET', '/fapi/v1/userTrades', results[0],
                                                     {'symbol': symbol['symbol'], 'limit': 10})  # 订单历史
                if not history_orders:
                    continue
                # 排序
                # history_orders.sort(key=lambda k: (k.get('time', 0)))
                # 获取持有的币种的最后五笔订单
                # history_orders = history_orders[-10:]
                for info in history_orders:
                    buyer = info['buyer']  # 是否是买方
                    commission = info['commission']  # 手续费
                    commissionAsset = info['commissionAsset']  # 手续费计价单位
                    maker = info['maker']  # 是否是挂单方
                    orderId = info['orderId']  # 订单编号
                    price = info['price']  # 成交价
                    qty = info['qty']  # 成交量
                    quoteQty = info['quoteQty']  # 成交额
                    realizedPnl = info['realizedPnl']  # 实现盈亏
                    side = info['side']  # 买卖方向
                    positionSide = info['positionSide']  # 持仓方向
                    symbol = info['symbol']  # 交易对
                    time_ = info['time']  # 时间
                    # 从时间筛选订单，一个小时内订单
                    if time() - time_ > 60*60:
                        continue
                    # 转换时区
                    tz = pytz.timezone('Asia/ShangHai')
                    dt = pytz.datetime.datetime.fromtimestamp(time_/1000, tz)
                    time_ = str(dt.strftime('%Y-%m-%d %H:%M:%S'))
                    order_type = ""
                    order_info_str = ""
                    if float(realizedPnl) != 0.0:
                        order_info_str = "账户：{}\n" \
                                         "交易对：{}\n" \
                                         "订单编号：{}\n" \
                                         "订单类型：{} {}\n" \
                                         "成交价：{}\n" \
                                         "成交量：{}\n" \
                                         "成交额：{}\n" \
                                         "手续费：{} {}\n" \
                                         "实现盈亏：{}\n" \
                                         "时间：{}".format(result[2], symbol, orderId,
                                                        zh_order_type(maker), zh_order_position(buyer),
                                                        price, qty, quoteQty, commission, commissionAsset,
                                                        realizedPnl, time_)
                        update.message.reply_text(order_info_str)
                    else:
                        pass
                        # order_info_str = "账户：{}\n" \
                        #                  "交易对：{}\n" \
                        #                  "订单编号：{}\n" \
                        #                  "订单类型：{} {}\n" \
                        #                  "成交价：{}\n" \
                        #                  "成交量：{}\n" \
                        #                  "成交额：{}\n" \
                        #                  "手续费：{} {}\n" \
                        #                  "时间：{}".format(result[2], symbol, orderId,
                        #                                 zh_order_type(maker), zh_order_position(buyer),
                        #                                 price, qty, quoteQty, commission, commissionAsset, time_)


                    # orderId = info['orderId']  # 订单ID
                    # symbol = info['symbol']  # 交易对
                    # avgPrice = info['avgPrice']  # 平均成交价
                    # executedQty = info['executedQty']  # 成交量
                    # cumQuote = info['cumQuote']  # 成交金额
                    # side = info['side']  # 买卖方向
                    # status = info['status']  # 订单状态
                    # time_ = info['time']  # 下单时间
                    # # 超过一天订单去除
                    # if time() - time_/1000 > 1*60*60:
                    #     continue
                    # # 转换时区
                    # tz = pytz.timezone('Asia/ShangHai')
                    # dt = pytz.datetime.datetime.fromtimestamp(time_/1000, tz)
                    # dt.strftime('%Y-%m-%d %H:%M:%S')
                    # order_info_str = "订单ID：{}\n" \
                    #                  "交易对：{}\n" \
                    #                  "平均成交价：{}\n" \
                    #                  "成交量：{}\n" \
                    #                  "成交金额：{}\n" \
                    #                  "买卖方向：{}\n" \
                    #                  "订单状态：{}\n" \
                    #                  "下单时间：{}".format(orderId, symbol, avgPrice,
                    #                                   executedQty, cumQuote, side, status, str(dt)[:-10])
                    # 推送到指定用户
                    # update.message.reply_text(order_info_str)
                have_order = True
                # ======================================================================================================

    if not have_order:
        update.message.reply_text("当前暂无持单，请稍后重试。")
    else:
        update.message.reply_text("订单查询完成。")


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
