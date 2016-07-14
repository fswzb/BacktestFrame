# -*- coding: utf-8 -*-

import numpy as np

def MA(price, Short, Long):
    if len(price) < Long + 1:
        return 0
    else:
        ma_short_0 = np.mean(price[-Short:])
        ma_short_1 = np.mean(price[-(Short + 1):-1])
        ma_long_0 = np.mean(price[-Long:])
        ma_long_1 = np.mean(price[-(Long + 1):-1])
        if ma_short_0 > ma_long_0 and ma_short_1 < ma_long_1:
            return 1
        if ma_short_0 < ma_long_0 and ma_short_1 > ma_long_1:
            return -1
    return 0

def buy_and_hold(price):
    if len(price) == 1:
        return 1

def stop_loss(current_price, cost_price, position, Stoploss):
    if position == 1:
        if current_price < cost_price * (100 - Stoploss) / 100: # 多头止损
            return -1
    elif position == -1:
        if current_price > cost_price * (100 + Stoploss) / 100: # 空头止损
            return 1
    return 0

