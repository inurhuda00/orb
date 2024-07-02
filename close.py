
import MetaTrader5 as mt5
import time
import utils

if not mt5.initialize(login=79279974, server="Exness-MT5Trial8", password="Nurhud@123"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()

symbol = "EURUSD"
deviation = 20

ticket = utils.get_last_line()

position = mt5.positions_get(ticket=int(ticket))

if position is None or len(position) == 0:
    print("No position found with ticket", ticket)
else:
    position = position[0]
    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": position.ticket,
        "price": mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script close",
    }

    close_result = mt5.order_send(close_request)
    if close_result.retcode != mt5.TRADE_RETCODE_DONE:
        utils.remove_line_by_keyword(ticket)
        print("Failed to close order, error code =", close_result.retcode)
    else:
        
        print("Order closed successfully, ticket =", close_result.order)

mt5.shutdown()