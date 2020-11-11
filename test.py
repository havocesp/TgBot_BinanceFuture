# # 获取每个交易对的历史记录
# history_orders = send_signed_request('GET', '/fapi/v1/allOrders', results[0], {'symbol': symbol['symbol']})  # 订单历史
# if not history_orders:
#     continue
# # 排序
# # history_orders.sort(key=lambda k: (k.get('time', 0)))
# # 获取持有的币种的最后五笔订单
# history_orders = history_orders[-5:]
# for info in history_orders:
#     orderId = info['orderId']  # 订单ID
#     symbol = info['symbol']  # 交易对
#     avgPrice = info['avgPrice']  # 平均成交价
#     executedQty = info['executedQty']  # 成交量
#     cumQuote = info['cumQuote']  # 成交金额
#     side = info['side']  # 买卖方向
#     status = info['status']  # 订单状态
#     time_ = info['time']  # 下单时间
#     # 超过一天订单去除
#     if time() - time_/1000 > 12*60*60:
#         continue
#     # 转换时区
#     tz = pytz.timezone('Asia/ShangHai')
#     dt = pytz.datetime.datetime.fromtimestamp(time_/1000, tz)
#     dt.strftime('%Y-%m-%d %H:%M:%S')
#     order_info_str = "订单ID：{}\n" \
#                      "交易对：{}\n" \
#                      "平均成交价：{}\n" \
#                      "成交量：{}\n" \
#                      "成交金额：{}\n" \
#                      "买卖方向：{}\n" \
#                      "订单状态：{}\n" \
#                      "下单时间：{}".format(orderId, symbol, avgPrice,
#                                       executedQty, cumQuote, side, status, dt)
#     # 推送到指定用户
#     update.message.reply_text(order_info_str)


# if len(balance_info) != 0:
#     for balance in balance_info:
#         if float(balance["balance"]) <= 0.0:
#             continue
#         asset = balance['asset']  # 资产（币种）
#         total_balance = balance['balance']  # 总余额
#         if total_usdt.endswith(asset.upper()):
#             total_usdt = str(float(total_usdt.replace("USDT", "")) + float(total_balance)) + "USDT"
#         elif total_bnb.endswith(asset.upper()):
#             total_bnb = str(float(total_bnb.replace("BNB", "")) + float(total_balance)) + "BNB"
#         crossWalletBalance = balance['crossWalletBalance']  # 全仓余额
#         crossUnPnl = balance['crossUnPnl']  # 全仓未实现盈亏
#         availableBalance = balance['availableBalance']  # 可用余额
#         maxWithdrawAmount = balance['maxWithdrawAmount']  # 最大可转出余额
#
#         send_str = "{}：资产：{}\n" \
#                    "总余额：{}\n" \
#                    "全仓余额：{}\n" \
#                    "全仓未实现盈亏：{}\n" \
#                    "可用余额：{}\n" \
#                    "最大可转出余额：{}".format(u_api['api_lable'], asset, total_balance, crossWalletBalance,
#                                        crossUnPnl, availableBalance, maxWithdrawAmount)
#         update.message.reply_text(send_str)
# else:
#     continue