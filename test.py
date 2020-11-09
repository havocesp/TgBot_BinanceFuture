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

websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr",
                          on_message = on_message,
                          on_error = on_error,
                          on_close = on_close)
ws.run_forever(sslopt={"check_hostname": False})