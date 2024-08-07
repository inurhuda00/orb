from flask import Flask, request, jsonify
import logger
import MetaTrader5 as mt5
import utils
import pandas as pd
import size

app = Flask(__name__)

logger = logger.setup()

WHITELIST_IPS = [
    '52.89.214.238',
    '34.212.75.30',
    '54.218.53.128',
    '52.32.178.7', 
    '127.0.0.1', 
    '10.8.0.75',
]

def ip_whitelist(f):
    def decorator(*args, **kwargs):
        if request.remote_addr not in WHITELIST_IPS:
            logger.critical(f"Access denied, your IP is: {request.remote_addr}")
            return jsonify({"message": f"Access denied, your IP is: {request.remote_addr}"}), 403
        return f(*args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

@app.route('/', methods=['GET'])
def home():
    logger.debug('Endpoint / diakses.')
    return jsonify({"message": "Welcome Home"}), 200

@app.route('/webhook', methods=['POST'])
@ip_whitelist
def webhook():
    data = request.get_json()

    if not mt5.initialize(path=r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe", login=79279974, server="Exness-MT5Trial8", password="Nurhud@123"):
        logger.error(f'initialize() failed, error code ={mt5.last_error()}')
        return jsonify({'message': f'initialize() failed, error code ={mt5.last_error()}'}), 500

    action = data.get('action')
    ticker = data.get('ticker')
    comment = data.get('comment')

    symbol_info = mt5.symbol_info(ticker)
    if symbol_info is None:
        logger.error(f'Symbol {ticker} not found')
        return jsonify({'message': f'Symbol {ticker} not found'}), 404

    if 'Close entry' in comment:
        entry_type = 'close_entry'
    else:
        entry_type = 'open'

    if action == 'buy':
        order_type = mt5.ORDER_TYPE_BUY
        atr = 'atr_buy'
    elif action == 'sell':
        order_type = mt5.ORDER_TYPE_SELL
        atr = 'atr_sell'
    else:
        logger.error(f'Unsupported action: {action}')
        return jsonify({'message': f'Unsupported action: {action}'}), 400
    
    deviation = 20
    risk_percentage = 0.05 # 5%
    # lot = 0.05

    # LOT SIZING
    balance = mt5.account_info()._asdict()['balance']
    money_risk = size.calculate_money_risk(balance, risk_percentage)
    digit = mt5.symbol_info(ticker).digits
    
    rates = pd.DataFrame(mt5.copy_rates_from_pos(ticker, mt5.TIMEFRAME_M15, 1, 4))
    stop_loss = size.get_stop_loss(rates)
    lot = size.calulate_lot(rates['close'].values[-1], stop_loss[atr], money_risk, digit)


    if entry_type == "open":
        
        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": ticker,
            "volume": lot,
            "type": order_type,
            "deviation": deviation,
            "comment": data.get('comment', 'TradingView alert'),
            "type_time": mt5.ORDER_TIME_GTC,
        })

        logger.debug(f"{ticker} {entry_type} Order {result.order}, with IP {request.remote_addr}" )

        mt5.shutdown()

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            utils.store_order(
                action=action, 
                interval=data.get("interval"), 
                ticker=ticker, 
                exchange=data.get('exchange'), 
                ticket=result.order
            )

            logger.info(f'Order success {result.order}')
            return jsonify({'message': 'Order success', 'order': result.order})
        else:
            logger.error(f'Failed to process order, error {result.retcode}')
            return jsonify({'message': 'Failed to process order', 'error_code': result.retcode}), 500
    
    elif entry_type == 'close_entry':
        
        orders = utils.find_order_by_criteria(
            interval=data.get("interval"), 
            exchange=data.get('exchange'),
            ticker=ticker
        )

        if not orders:
            logger.error("Order not found")
            return jsonify({'message': 'Order not found.', 'error_code': 'ORDERS_NOT_FOUND'}), 404

        first_order = orders[0]
        ticket = first_order['ticket']

        position = mt5.positions_get(ticket=int(ticket))

        if position is None or len(position) == 0:
            logger.error(f"No position found with ticket {ticket}")
            utils.delete_by_ticket(ticket=ticket)
            return jsonify({'message': 'No position found', 'error_code': 'POSITION_NOT_FOUND'}), 404
        
        position = position[0]
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
        }

        result = mt5.order_send(close_request)

        logger.info(f"{ticker} {entry_type} Order {result.order}, with IP {request.remote_addr}" )

        mt5.shutdown()

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            utils.delete_by_ticket(ticket=ticket)
            logger.info(f'Order success {result.order}')
            return jsonify({'message': 'Close Order success', 'order': result.order})
        else:
            logger.error(f'Failed to process order, error {result.retcode}')
            return jsonify({'message': 'Failed to process order', 'error_code': result.retcode}), 500
        
    logger.critical("Invalid request")
    return jsonify({'message': 'Invalid request', 'error_code': 'INVALID_REQUEST'}), 400
    

@app.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.get_json()
    if data:
        return jsonify({"message": "Data received", "data": data}), 200
    else:
        return jsonify({"message": "No data received"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
