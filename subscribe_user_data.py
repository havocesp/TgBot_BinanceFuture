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


def zh_position_side(ps):
    """
    持仓方向
    """
    if ps == "LONG":
        ps = "做多"
    elif ps == "SHORT":
        ps = "做空"
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
        ot = "止损单"
    elif ot == "TAKE_PROFIT":
        ot = "止盈单"
    elif ot == "LIQUIDATION ":
        ot = "强平单"
    return ot


def zh_order_status(order_s):
    """
    汉化订单状态
    """
    if order_s == "NEW":
        order_s = "新建订单"
    elif order_s == "PARTIALLY_FILLED":
        order_s = "部分成交"
    elif order_s == "FILLED":
        order_s = "全部成交"
    elif order_s == "CANCELED":
        order_s = "撤销订单"
    elif order_s == "EXPIRED":
        order_s = "订单过期"
    elif order_s == "REJECTED ":
        order_s = "订单被拒绝"
    elif order_s == "NEW_INSURANCE":
        order_s = "风险保障基金(强平)"
    elif order_s == "NEW_ADL":
        order_s = "自动减仓序列(强平)"
    return order_s


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
                # order_str = "交易对：{}\n" \
                #             "客户端自定订单ID：{}\n" \
                #             "订单方向：{}\n" \
                #             "订单类型：{}\n" \
                #             "有效方式：{}\n" \
                #             "订单原始数量：{}\n" \
                #             "订单原始价格：{}\n" \
                #             "订单平均价格：{}\n" \
                #             "条件订单触发价格，对追踪止损单无效：{}\n" \
                #             "本次事件的具体执行类型：{}\n" \
                #             "订单的当前状态：{}\n" \
                #             "订单ID：{}\n" \
                #             "订单末次成交量：{}\n" \
                #             "订单累计已成交量：{}\n" \
                #             "订单末次成交价格：{}\n" \
                #             "手续费资产类型：{}\n" \
                #             "手续费数量：{}\n" \
                #             "成交时间：{}\n" \
                #             "成交ID：{}\n" \
                #             "买单净值：{}\n" \
                #             "卖单净值：{}\n" \
                #             "该成交是作为挂单成交吗？：{}\n" \
                #             "是否是只减仓单：{}\n" \
                #             "触发价类型：{}\n" \
                #             "原始订单类型：{}\n" \
                #             "持仓方向：{}\n" \
                #             "是否为触发平仓单; 仅在条件订单情况下会推送此字段{}\n" \
                #             "追踪止损激活价格, 仅在追踪止损单时会推送此字段：{}\n" \
                #             "追踪止损回调比例, 仅在追踪止损单时会推送此字段：{}\n" \
                #             "该交易实现盈亏：{}".format(
                #     event.symbol, event.clientOrderId, event.side, event.type, event.timeInForce, event.origQty,
                #     event.price, event.avgPrice, event.stopPrice, event.executionType, event.orderStatus, event.orderId,
                #     event.lastFilledQty, event.cumulativeFilledQty, event.lastFilledPrice, event.commissionAsset,
                #     event.commissionAmount, event.orderTradeTime, event.tradeID, event.bidsNotional, event.asksNotional,
                #     event.isMarkerSide, event.isReduceOnly, event.workingType, event.initOrderStatus,
                #     event.positionSide, event.isClosePosition, event.activationPrice, event.callbackRate,
                #     event.orderProfit
                # )

                symbol = event.symbol  # 交易对
                positionSide = ""  # 订单方向
                if event.side == "SELL":
                    positionSide = "做空"
                else:
                    positionSide = "做多"
                origQty = event.origQty  # 订单原始数量
                avgPrice = event.avgPrice  # 订单平均价格
                # 订单筛选
                orderStatus = event.orderStatus  # 订单的当前状态

                orderId = event.orderId  # 订单ID
                tz = pytz.timezone('Asia/ShangHai')
                dt = pytz.datetime.datetime.fromtimestamp(event.orderTradeTime / 1000, tz)
                dt.strftime('%Y-%m-%d %H:%M:%S')
                orderTradeTime = str(dt)[:-10]  # 成交时间
                orderProfit = event.orderProfit  # 该交易实现盈亏
                if float(orderProfit) != 0:
                    if float(orderProfit) < 0:
                        order_str = "账户：{}\n" \
                                    "交易对：{}\n" \
                                    "持仓方向：{}\n" \
                                    "持仓数量：{}\n" \
                                    "持仓均价：{}\n" \
                                    "本单盈亏：{} USDT %f0%9f%a5%ba%f0%9f%a5%ba%f0%9f%a5%ba\n" \
                                    "订单号：{}\n" \
                                    "订单状态：{}\n" \
                                    "成交时间：{}".format(user_info[0], symbol.replace('USDT', '-USDT'), positionSide,
                                                     origQty, avgPrice, orderProfit, orderId,
                                                     zh_order_status(orderStatus) or orderStatus, orderTradeTime)
                    else:
                        order_str = "账户：{}\n" \
                                    "交易对：{}\n" \
                                    "持仓方向：{}\n" \
                                    "持仓数量：{}\n" \
                                    "持仓均价：{}\n" \
                                    "本单盈亏：{} USDT %f0%9f%92%b0%f0%9f%92%b0%f0%9f%92%b0\n" \
                                    "订单号：{}\n" \
                                    "订单状态：{}\n" \
                                    "成交时间：{}".format(user_info[0], symbol.replace('USDT', '-USDT'), positionSide,
                                                     origQty, avgPrice, orderProfit, orderId,
                                                     zh_order_status(orderStatus) or orderStatus, orderTradeTime)
                else:
                    order_str = "账户：{}\n" \
                                "交易对：{}\n" \
                                "持仓方向：{}\n" \
                                "持仓数量：{}\n" \
                                "持仓均价：{}\n" \
                                "订单号：{}\n" \
                                "订单状态：{}\n" \
                                "成交时间：{}".format(user_info[0], symbol.replace('USDT', '-USDT'),
                                                 positionSide, origQty, avgPrice, orderId,
                                                 zh_order_status(orderStatus) or orderStatus, orderTradeTime)

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
        if user_info[2] != 1375095749:
            continue
        t = threading.Thread(target=run, args=(user_info,))
        t.start()
        # TODO 开启一个
        break


if __name__ == '__main__':
    main()
    pass
