import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, ShippingQueryHandler
from settings import SKey, PKey, teltoken, telChanel

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def tg_help(update, context):
    description_str = "Welcome to use Trading bot!\n " \
                      "All commands list:\n" \
                      "/help = 查看所有命令\n" \
                      "/balance = 查看账户余额\n" \
                      "/orders = 查询所有订单"
    update.message.reply_text(description_str)
    pass


def b_balance(update, context):
    pass


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
