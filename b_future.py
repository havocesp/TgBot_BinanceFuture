import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, ShippingQueryHandler
from settings import SKey, PKey, teltoken, telChanel
from futures import send_signed_request

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def tg_help(update, context):
    description_str = "Welcome to use Trading bot!\n " \
                      "/help = 查看所有命令\n" \
                      "/balance = 查看账户余额\n" \
                      "/orders = 查询所有订单"
    update.message.reply_text(description_str)
    pass


def b_balance(update, context):
    balance_info = send_signed_request('GET', '/fapi/v2/balance')
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
                       "总余额:{}\n" \
                       "全仓余额:{}\n" \
                       "全仓未实现盈亏:{}\n" \
                       "可用余额:{}\n" \
                       "最大可转出余额:{}".format(asset, total_balance, crossWalletBalance,
                                           crossUnPnl, availableBalance, maxWithdrawAmount)
            update.message.reply_text(send_str)
    else:
        update.message.reply_text("您的资产正在结算中，请稍后重试！")


def b_orders(update, context):
    pass


def error(update, context):
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
    dp.add_handler(CommandHandler("help", tg_help))
    dp.add_handler(CommandHandler("balance", b_balance))
    dp.add_handler(CommandHandler("orders", b_orders))

   # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()




if __name__ == '__main__':
    main()
