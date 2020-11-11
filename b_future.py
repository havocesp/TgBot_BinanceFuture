import logging
from time import time

import pytz
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import teltoken
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
    send_text = 'https://api.telegram.org/bot' + teltoken + '/sendMessage?chat_id=' + str(user_id) + '&parse_mode=Markdown&text=' + message
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
    # select_sql = "select b_api_key, b_secret_key from binance_tg where tg_id={}".format(user_id)
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
    # 查询当前API是否被绑定
    select_sql = "select * from binance_tg where b_api_key='{}'".format(api_info_list[0])
    results = select_data(select_sql)
    if results:
        update.message.reply_text("此API已经被绑定！")
        return

    # 绑定用户信息到数据库
    insert_sql = "insert into binance_tg(tg_id, b_api_key, b_secret_key, tg_token) value(%s, '%s', '%s', '%s')" \
                 % (user_id, api_info_list[0], api_info_list[1], teltoken.replace(":", ""))
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
    select_sql = "select b_api_key, b_secret_key from binance_tg where tg_id={}".format(user_id)
    results = select_data(select_sql)
    if not results:
        update.message.reply_text("请先绑定API")
        return
    total_usdt = "0USDT"
    total_bnb = "0BNB"
    update.message.reply_text("资产核算中，请稍后。")
    for u_api in results:
        balance_info = send_signed_request('GET', '/fapi/v2/balance', u_api)
        if len(balance_info) != 0:
            for balance in balance_info:
                if float(balance["balance"]) <= 0.0:
                    continue
                asset = balance['asset']  # 资产（币种）
                total_balance = balance['balance']  # 总余额
                if total_usdt.endswith(asset.upper()):
                    total_usdt = str(float(total_usdt.replace("USDT", "")) + float(total_balance)) + "USDT"
                elif total_bnb.endswith(asset.upper()):
                    total_bnb = str(float(total_bnb.replace("BNB", "")) + float(total_balance)) + "BNB"
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
            print("======="*30)
            continue
    # 发送余额
    update.message.reply_text("核算完成，合计：\n"
                              "{}\n"
                              "{}".format(total_usdt, total_bnb))


def b_orders(update, context):
    """
    Get binance history orders
    """
    have_order = False
    # 检查用户ID
    user_id = update.message.from_user.id
    select_sql = "select b_api_key, b_secret_key from binance_tg where tg_id={}".format(user_id)
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
                # 没有持仓的去掉
                if float(symbol['entryPrice']) == 0.0:
                    continue
                symbol_ = symbol['symbol']  # 交易对
                positionAmt = symbol['positionAmt']  # 持仓数量
                entryPrice = symbol['entryPrice']  # 持仓成本价
                unrealizedProfit = symbol['unrealizedProfit']  # 持仓未实现盈亏
                order_info_str = "交易对：{}\n" \
                                 "持仓数量：{}\n" \
                                 "持仓成本价：{}\n" \
                                 "持仓未实现盈亏：{}" .format(symbol_, positionAmt, entryPrice, unrealizedProfit)
                # 推送到指定用户
                update.message.reply_text(order_info_str)
                have_order = True
            if not have_order:
                update.message.reply_text("当前暂无持单，请稍后重试。")
            else:
                update.message.reply_text("查询完成。")
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
