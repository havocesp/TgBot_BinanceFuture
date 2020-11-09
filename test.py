import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

#开始连接时执行，需要订阅的消息和其它操作都要在这里完成
def on_open(ws):
    websocket.enableTrace(True)
    ws = websocket.create_connection("wss://fstream.binance.com")
    # print("Sending 'Hello, World'...")
    # ws.send("Hello, World")
    # print("Sent")
    # print("Receiving...")
    result = ws.recv()
    print("Received '%s'" % result)
    ws.close()
    # ws.send(wsGetAccount('ok_sub_spotcny_userinfo',api_key,secret_key))
    # ws.send("{'event':'addChannel','channel':'ok_sub_spotcny_btc_depth_60'}")
    # ws.send("{'event':'addChannel','channel':'ok_sub_spotcny_btc_ticker'}")

# websocket.enableTrace(True)
# ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr",
#                           on_message = on_message,
#                           on_error = on_error,
#                           on_close = on_close)
# ws.on_open = on_open
# ws.run_forever(sslopt={"check_hostname": False})


on_open("")