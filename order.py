
import MetaTrader5 as mt5
import time
import utils

if not mt5.initialize(login=79279974, server="Exness-MT5Trial8", password="Nurhud@123"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()

ticker = "EURUSD"
lot = 0.01
point = mt5.symbol_info(ticker).point
price = mt5.symbol_info_tick(ticker).ask
deviation = 20

result = mt5.order_send({
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": ticker,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    # "price": price - 2000 * point,
    # "sl": price - 1000 * point,
    "tp": price + 5000 * point,
    "deviation": deviation,
    "comment": "test",
    "type_time": mt5.ORDER_TIME_GTC,
})

utils.add_new_line(result.order)

mt5.shutdown()