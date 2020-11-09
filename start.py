import json
import logging
from telegram import LabeledPrice, ShippingOption
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, ShippingQueryHandler
from telegram import InputTextMessageContent, InputMessageContent
from binance.client import Client
from settings import SKey, PKey, teltoken, telChanel
from binance.websockets import BinanceSocketManager


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def info(update, context):
    # Send a message when the command /start is issued.
    update.message.bot.send_message(chat_id=685705504, text="这是开始了")
    update.message.reply_text(
        'BALANCE BOT Ahoy!\nCommands to use:\n  /balance = Display Account´s Balance\n  /orders = Display Open Orders')


def balance(update, context):
    client = Client(api_key=SKey, api_secret=PKey)
    data = client.futures_account()
    balance = data.get("totalWalletBalance")
    Unrealprofit = data.get("totalUnrealizedProfit")
    x = float(balance)
    xx = round(x, 3)
    y = float(Unrealprofit)
    yy = round(y, 3)
    txt = "Binance Future Wallet! \nBalance: {}USDT\nUnrealizedProfit: {}USDT"
    balancemsg = txt.format(xx, yy)
    update.message.reply_text(balancemsg)


def orders(update, context):
    client = Client(api_key=SKey, api_secret=PKey)
    data = client.futures_get_open_orders()
    if len(data) == 0:
        update.message.reply_text("Buddy, No Open Orders!")
    else:
        price = data[0]['price']
        side = data[0]['side']
        symbol = data[0]['symbol']
        qty = data[0]['origQty']
        a = qty + symbol
        data2 = client.futures_mark_price(symbol=symbol)
        currentprice = data2.get("markPrice")
        x = float(currentprice)
        xx = round(x, 3)
        ordertxt = "Open Orders:\nCurrent Price:{}USDT\n{} EXIT AT {} WITH {}"
        ordermsg = ordertxt.format(xx, a, price, side)
        update.message.reply_text(ordermsg)


def error(update, context):
    # Log Errors caused by Updates.
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def websocket_t(update, content_text):
    def process_message(msg):
        print(str(msg))
        update.message.bot.send_message(chat_id=685705504, text=str(msg))
    client = Client(api_key=SKey, api_secret=PKey)
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    conn_key = bm.start_user_socket(process_message)
    update.message.bot.send_message(chat_id=685705504, text=conn_key)
    # then start the socket manager
    bm.start()


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    updater = Updater(teltoken, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.video, websocket_t))


    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("orders", orders))


    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()




if __name__ == '__main__':
    main()
