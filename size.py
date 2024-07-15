import math
import pandas_ta as pd_ta


def calculate_money_risk(number, risk_percentage):
    if number == 0:
        return 0
    
    exponent = int(math.log10(number))
    base = 10 ** exponent
    return base * (number // base) * risk_percentage


def calulate_lot(entry_price, stop_loss_price, money_risk, digits):
    # Calculate the stop loss amount
    stop_loss_amount = abs(entry_price - stop_loss_price)

    if digits == 3:
        quantity = 100
    else:
        quantity = 100000

    # Calculate the lot size
    lot_size = round(money_risk / stop_loss_amount / quantity, 2)
    return max(lot_size, 0.01)


def get_stop_loss(rates):
    rates['atr_high'] = rates['open'] + (pd_ta.atr(rates['high'], rates['low'], rates['close'], 
                                                   length=3, mamode='rma') * 1.1)
    rates['atr_low'] = rates['open'] - (pd_ta.atr(rates['high'], rates['low'], rates['close'], 
                                                  length=3, mamode='rma') * 1.1)

    return {
        "atr_buy": round(rates['atr_low'].values[-1], 5),
        "atr_sell": round(rates['atr_high'].values[-1], 5)
    }