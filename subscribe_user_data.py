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

logger = logging.getLogger("binance-client")
logger.setLevel(level=logging.WARN)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def tg_bot_send_text(send_message, user_id, tg_token):
    """
    To send message
    """
    send_text = 'https://api.telegram.org/bot' + tg_token + '/sendMessage?chat_id=' + str(user_id) + '&text=' + send_message
    print(send_text)
    try:
        response = requests.get(send_text)
        return response.json()
    except Exception as e:
        print(e)
        return {}


def zh_position_side(ps, s):
    """
    持仓方向
    """
    if ps == "LONG":
        ps = "做多"
    elif ps == "SHORT":
        ps = "做空"
    elif ps == "BOTH":
        if s == "SELL":
            ps = "做空"
        else:
            ps = "做多"
    return ps


def zh_order_side(o_side):
    """
    订单方向
    """
    if o_side == "BUY":
        o_side = "买入"
    elif o_side == "SELL":
        o_side = "卖出"
    return o_side


def zh_order_types(ot):
    """
    订单类型
    """
    if ot == "LIMIT":
        ot = "限价单"
    elif ot == "MARKET":
        ot = "市价单"
    elif ot == "STOP":
        ot = "止损限价单"
    elif ot == "TAKE_PROFIT":
        ot = "止盈限价单"
    elif ot == "LIQUIDATION ":
        ot = "强平单"
    elif ot == "STOP_MARKET":
        ot = "止损市价单"
    elif ot == "TAKE_PROFIT_MARKET":
        ot = "止盈市价单"
    elif ot == "TRAILING_STOP_MARKET":
        ot = "跟踪止损单"
    return ot


def zh_order_status(order_s):
    """
    订单状态
    """
    if order_s == "NEW":
        order_s = "创建订单"
    elif order_s == "PARTIALLY_FILLED":
        order_s = "部分成交"
    elif order_s == "FILLED":
        order_s = "订单成交"
    elif order_s == "CANCELED":
        order_s = "订单撤销"
    elif order_s == "EXPIRED":
        order_s = "订单过期"
    elif order_s == "REJECTED ":
        order_s = "订单被拒绝"
    elif order_s == "NEW_INSURANCE":
        order_s = "风险保障基金(强平)"
    elif order_s == "NEW_ADL":
        order_s = "自动减仓序列(强平)"
    return order_s


def all_order_start(user_info):
    """
    user_info：api_lable, tg_id, b_api_key, b_secret_key, tg_token
    启动单线程的数据订阅
    """
    # TODO 查询当前持仓
    # 创建当前持仓列表，记录交易对，持仓方向，
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
                # 账户余额变化提醒
                # tg_bot_send_text(balance_str, user_info[1], user_info[4])
                print("================")
                print("=== Positions ===")
                PrintMix.print_data(event.positions)
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
                # order_str = "交易对：{}\n订单方向：{}\n订单类型：{}\n订单原始数量：{}\n订单原始价格：{}\n订单平均价格：{}\n" \
                #             "条件订单触发价格，对追踪止损单无效：{}\n本次事件的具体执行类型：{}\n订单的当前状态：{}\n订单ID：{}\n" \
                #             "订单末次成交量：{}\n订单累计已成交量：{}\n订单末次成交价格：{}\n手续费资产类型：{}\n手续费数量：{}\n" \
                #             "成交时间：{}\n该成交是作为挂单成交吗？：{}\n是否是只减仓单：{}\n触发价类型：{}\n原始订单类型：{}\n" \
                #             "持仓方向：{}\n该交易实现盈亏：{}".format(
                #     event.symbol, event.side, event.type, event.origQty,
                #     event.price, event.avgPrice, event.stopPrice, event.executionType, event.orderStatus, event.orderId,
                #     event.lastFilledQty, event.cumulativeFilledQty, event.lastFilledPrice, event.commissionAsset,
                #     event.commissionAmount, event.orderTradeTime, event.isMarkerSide, event.isReduceOnly,
                #     event.workingType, event.initOrderStatus, event.positionSide, event.orderProfit
                # )
                symbol = event.symbol  # 交易对
                order_id = event.orderId  # 订单ID
                order_type = event.type  # 订单类型
                side = event.side  # 订单方向

                # -----------------------------------------------------------
                origQty = event.origQty  # 订单原始数量
                price = event.price  # 订单原始价格
                # -----------------------------------------------------------
                avgPrice = event.avgPrice  # 订单平均价格
                # ------------------------------------------------------------
                cumulativeFilledQty = event.cumulativeFilledQty  # 订单累计成交量
                lastFilledPrice = event.lastFilledPrice  # 订单末次成交价
                # -----------------------------------------------------------

                executionType = event.executionType  # 本次事件的执行类型
                orderStatus = event.orderStatus  # 订单当前状态
                isMarkerSide = event.isMarkerSide  # 该成交是否为挂单成交
                positionSide = event.positionSide  # 持仓方向

                commissionAsset = event.commissionAsset  # 手续费资产类型
                commissionAmount = event.commissionAmount  # 手续费数量
                bidsNotional = event.bidsNotional  # 买单净值
                asksNotional = event.asksNotional  # 卖单净值
                orderProfit = event.orderProfit  # 该交易实现盈亏

                tz = pytz.timezone('Asia/ShangHai')
                dt = pytz.datetime.datetime.fromtimestamp(event.orderTradeTime / 1000, tz)
                dt.strftime('%Y-%m-%d %H:%M:%S')
                orderTradeTime = str(dt)[:-10]  # 成交时间

                # 创建/取消订单
                if (orderStatus == "NEW" or orderStatus == "CANCELED") and not isMarkerSide:
                    send_str = "账户：{}\n" \
                               "交易对：{}\n" \
                               "订单号：{}\n" \
                               "订单状态：{}\n" \
                               "订单类型：{}\n" \
                               "订单方向：{}\n" \
                               "数量：{} {}\n" \
                               "平均价格：{} {}/USDT\n" \
                               "下单时间：{}".format(user_info[0], symbol.replace("USDT", "_USDT"), order_id,
                                                zh_order_status(orderStatus), zh_order_types(order_type),
                                                zh_order_side(side),
                                                origQty, symbol.replace("USDT", ""), price,
                                                symbol.replace("USDT", ""), orderTradeTime)
                    tg_bot_send_text(send_str, user_info[1], user_info[4])
                elif (orderStatus == "PARTIALLY_FILLED" or orderStatus == "FILLED") and executionType == "TRADE":
                    if float(orderProfit) != 0:
                        send_str = "账户：{}\n" \
                                   "交易对：{}\n" \
                                   "订单号：{}\n" \
                                   "订单状态：{}\n" \
                                   "订单类型：{}\n" \
                                   "订单方向：{}\n" \
                                   "数量：{} {}\n" \
                                   "平均价格：{} {}/USDT\n" \
                                   "价值：{} USDT\n" \
                                   "手续费：{} {}\n" \
                                   "本单盈亏：{} USDT\n" \
                                   "下单时间：{}\n" \
                                   "买单净值：{}\n" \
                                   "卖单净值：{}\n".format(user_info[0], symbol.replace("USDT", "_USDT"), order_id,
                                                    zh_order_status(orderStatus), zh_order_types(order_type),
                                                    zh_order_side(side),
                                                    cumulativeFilledQty, symbol.replace("USDT", ""), avgPrice, symbol.replace("USDT", ""),
                                                    float(origQty) * float(avgPrice), commissionAmount, commissionAsset,
                                                    orderProfit, orderTradeTime, bidsNotional, asksNotional)
                        tg_bot_send_text(send_str, user_info[1], user_info[4])
                    else:
                        send_str = "账户：{}\n" \
                                   "交易对：{}\n" \
                                   "订单号：{}\n" \
                                   "订单状态：{}\n" \
                                   "订单类型：{}\n" \
                                   "订单方向：{}\n" \
                                   "持仓量：{} {}\n" \
                                   "持仓均价：{} USDT\n" \
                                   "价值：{} {}/USDT\n" \
                                   "手续费：{} {}\n" \
                                   "下单时间：{}".format(user_info[0], symbol.replace("USDT", "_USDT"), order_id,
                                                    zh_order_status(orderStatus), zh_order_types(order_type),
                                                    zh_order_side(side), origQty, symbol.replace("USDT", ""),
                                                    avgPrice, symbol.replace("USDT", ""),
                                                    float(origQty) * float(avgPrice), commissionAmount, commissionAsset,
                                                    orderTradeTime)
                        tg_bot_send_text(send_str, user_info[1], user_info[4])
                # ======================================================================================================
                # tg_bot_send_text(order_str, user_info[1], user_info[4])
                # ======================================================================================================
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

    sub_client = SubscriptionClient(api_key=g_api_key, secret_key=g_secret_key)

    sub_client.subscribe_user_data_event(listen_key, callback, error)


def profit_order_start(user_info):
    """
    user_info：api_lable, tg_id, b_api_key, b_secret_key, tg_token
    启动单线程的数据订阅
    """
    # TODO 查询当前持仓
    # 创建当前持仓列表，记录交易对，持仓方向，
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
                # 账户余额变化提醒
                # tg_bot_send_text(balance_str, user_info[1], user_info[4])
                print("================")
                print("=== Positions ===")
                PrintMix.print_data(event.positions)
                print("================")
            elif (event.eventType == "ORDER_TRADE_UPDATE"):
                symbol = event.symbol  # 交易对
                order_id = event.orderId  # 订单ID
                order_type = event.type  # 订单类型
                side = event.side  # 订单方向

                # -----------------------------------------------------------
                origQty = event.origQty  # 订单原始数量
                price = event.price  # 订单原始价格
                # -----------------------------------------------------------
                avgPrice = event.avgPrice  # 订单平均价格
                # ------------------------------------------------------------
                cumulativeFilledQty = event.cumulativeFilledQty  # 订单累计成交量
                lastFilledPrice = event.lastFilledPrice  # 订单末次成交价
                # -----------------------------------------------------------

                executionType = event.executionType  # 本次事件的执行类型
                orderStatus = event.orderStatus  # 订单当前状态
                isMarkerSide = event.isMarkerSide  # 该成交是否为挂单成交
                positionSide = event.positionSide  # 持仓方向

                commissionAsset = event.commissionAsset  # 手续费资产类型
                commissionAmount = event.commissionAmount  # 手续费数量
                bidsNotional = event.bidsNotional  # 买单净值
                asksNotional = event.asksNotional  # 卖单净值
                orderProfit = event.orderProfit  # 该交易实现盈亏

                tz = pytz.timezone('Asia/ShangHai')
                dt = pytz.datetime.datetime.fromtimestamp(event.orderTradeTime / 1000, tz)
                dt.strftime('%Y-%m-%d %H:%M:%S')
                orderTradeTime = str(dt)[:-10]  # 成交时间
                if float(orderProfit) != 0:
                    send_str = "账户：{}\n" \
                               "交易对：{}\n" \
                               "订单号：{}\n" \
                               "订单状态：{}\n" \
                               "订单类型：{}\n" \
                               "订单方向：{}\n" \
                               "数量：{} {}\n" \
                               "平均价格：{} {}/USDT\n" \
                               "价值：{} USDT\n" \
                               "手续费：{} {}\n" \
                               "本单盈亏：{} USDT\n" \
                               "下单时间：{}\n" \
                               "买单净值：{}\n" \
                               "卖单净值：{}\n".format(user_info[0], symbol.replace("USDT", "_USDT"), order_id,
                                                  zh_order_status(orderStatus), zh_order_types(order_type),
                                                  zh_order_side(side),
                                                  cumulativeFilledQty, symbol.replace("USDT", ""), avgPrice,
                                                  symbol.replace("USDT", ""),
                                                  float(origQty) * float(avgPrice), commissionAmount, commissionAsset,
                                                  orderProfit, orderTradeTime, bidsNotional, asksNotional)
                    tg_bot_send_text(send_str, user_info[1], user_info[4])
                # ======================================================================================================
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

    sub_client = SubscriptionClient(api_key=g_api_key, secret_key=g_secret_key)

    sub_client.subscribe_user_data_event(listen_key, callback, error)


def order_stop(user_info):
    """
    user_info：api_lable, tg_id, b_api_key, b_secret_key, tg_token
    停止订单推送
    """
    # Start user data stream
    request_client = RequestClient(api_key=user_info[2], secret_key=user_info[3])
    listen_key = request_client.start_user_data_stream()
    print("listenKey: ", listen_key)

    # Keep user data stream
    # result = request_client.keep_user_data_stream()
    # print("Result: ", result)

    # Close user data stream
    result = request_client.close_user_data_stream()
    print("**=="*90)
    print("Result: ", result)


def main():
    """
    多线程开启订阅
    """
    all_user_sql = "select api_lable, tg_id, b_api_key, b_secret_key, tg_token from " + t_table
    all_users = select_data(all_user_sql)
    if not all_users:
        return
    for user_info in all_users:
        if user_info[1] != 685705504:
            continue
        t = threading.Thread(target=order_start, args=(user_info,))
        t.start()


if __name__ == '__main__':
    main()
    pass
