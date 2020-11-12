import logging
import threading

import pytz

from binance_f import RequestClient
from binance_f import SubscriptionClient
from binance_f.constant.test import *
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException

from binance_f.base.printobject import *
from config import t_table
from sql_config import select_data
import requests


def tg_bot_send_text(send_message, user_id, tg_token):
    """
    To send message
    """
    send_text = 'https://api.telegram.org/bot' + tg_token + '/sendMessage?chat_id=' + \
                str(user_id) + '&parse_mode=Markdown&text=' + send_message
    print(send_text)
    try:
        response = requests.get(send_text)
        return response.json()
    except Exception as e:
        print(e)
        return {}


def run(user_info):
    """
    user_info：api_lable, tg_id, b_api_key, b_secret_key, tg_token
    启动单线程的数据订阅
    """
    def callback(data_type: 'SubscribeMessageType', event: 'any'):
        if data_type == SubscribeMessageType.RESPONSE:
            print("Event ID: ", event)
        elif data_type == SubscribeMessageType.PAYLOAD:
            if (event.eventType == "ACCOUNT_UPDATE"):
                print("Event Type: ", event.eventType)
                print("Event time: ", event.eventTime)
                print("Transaction time: ", event.transactionTime)

                print("=== Balances ===")
                PrintMix.print_data(event.balances)
                balance_str = ""
                for user_balance in event.balances:
                    asset = user_balance.asset  # 交易对
                    walletBalance = user_balance.walletBalance  # 余额
                    balance_str += "{} {}\n".format(walletBalance, asset)
                balance_str = "账户：{}\n".format(user_info[0]) + balance_str
                tg_bot_send_text(balance_str, user_info[1], user_info[4])
                print("================")

                print("=== Positions ===")
                PrintMix.print_data(event.positions)
                # positions_str = ""
                # for position_info in event.positions:
                #
                print("================")

            elif (event.eventType == "ORDER_TRADE_UPDATE"):
                print("Event Type: ", event.eventType)
                print("Event time: ", event.eventTime)
                print("Transaction Time: ", event.transactionTime)
                print("Symbol: ", event.symbol)
                print("Client Order Id: ", event.clientOrderId)
                print("Side: ", event.side)
                print("Order Type: ", event.type)
                print("Time in Force: ", event.timeInForce)
                print("Original Quantity: ", event.origQty)
                print("Position Side: ", event.positionSide)
                print("Price: ", event.price)
                print("Average Price: ", event.avgPrice)
                print("Stop Price: ", event.stopPrice)
                print("Execution Type: ", event.executionType)
                print("Order Status: ", event.orderStatus)
                print("Order Id: ", event.orderId)
                print("Order Last Filled Quantity: ", event.lastFilledQty)
                print("Order Filled Accumulated Quantity: ", event.cumulativeFilledQty)
                print("Last Filled Price: ", event.lastFilledPrice)
                print("Commission Asset: ", event.commissionAsset)
                print("Commissions: ", event.commissionAmount)
                print("Order Trade Time: ", event.orderTradeTime)
                print("Trade Id: ", event.tradeID)
                print("Bids Notional: ", event.bidsNotional)
                print("Ask Notional: ", event.asksNotional)
                print("Is this trade the maker side?: ", event.isMarkerSide)
                print("Is this reduce only: ", event.isReduceOnly)
                print("stop price working type: ", event.workingType)
                print("Is this Close-All: ", event.isClosePosition)
                print("========Orders=========")
                symbol = event.symbol  # 交易对
                side = ""  # 订单方向
                if event.side == "SELL":
                    side = "做空"
                else:
                    side = "做多"
                origQty = event.origQty  # 订单原始数量
                avgPrice = event.avgPrice  # 订单平均价格
                orderStatus = event.orderStatus  # 订单的当前状态
                orderId = event.orderId  # 订单ID
                tz = pytz.timezone('Asia/ShangHai')
                dt = pytz.datetime.datetime.fromtimestamp(event.orderTradeTime/1000, tz)
                dt.strftime('%Y-%m-%d %H:%M:%S')
                orderTradeTime = dt  # 成交时间
                # 该交易实现盈亏
                order_str = "账户：{}\n" \
                            "交易对：{}\n" \
                            "持仓方向：{}\n" \
                            "持仓数量：{}\n" \
                            "持仓均价：{}\n" \
                            "订单号：{}\n" \
                            "成交时间：{}".format(user_info[0], symbol.replace('USDT', '-USDT'),
                                             side, origQty, avgPrice, orderId, orderTradeTime)
                tg_bot_send_text(order_str, user_info[1], user_info[4])
                print("=======================")
                if not event.activationPrice is None:
                    print("Activation Price for Trailing Stop: ", event.activationPrice)
                if not event.callbackRate is None:
                    print("Callback Rate for Trailing Stop: ", event.callbackRate)
            elif (event.eventType == "listenKeyExpired"):
                print("Event: ", event.eventType)
                print("Event time: ", event.eventTime)
                print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
                print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
                print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
        else:
            print("Unknown Data:")
        print()

    def error(e: 'BinanceApiException'):
        print(e.error_code + e.error_message)

    # Start user data stream
    request_client = RequestClient(api_key=user_info[2], secret_key=user_info[3])
    listen_key = request_client.start_user_data_stream()
    print("listenKey: ", listen_key)

    # Keep user data stream
    result = request_client.keep_user_data_stream()
    print("Result: ", result)

    # Close user data stream
    # result = request_client.close_user_data_stream()
    # print("Result: ", result)

    logger = logging.getLogger("binance-client")
    logger.setLevel(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    sub_client = SubscriptionClient(api_key=g_api_key, secret_key=g_secret_key)

    sub_client.subscribe_user_data_event(listen_key, callback, error)


def main():
    """
    多线程开启订阅
    """
    all_user_sql = "select api_lable, tg_id, b_api_key, b_secret_key, tg_token from " + t_table
    all_users = select_data(all_user_sql)
    if not all_users:
        return
    for user_info in all_users:
        user_info[2] = threading.Thread(target=run, args=(user_info,))
        user_info[2].start()
        break


if __name__ == '__main__':
    main()
    pass
