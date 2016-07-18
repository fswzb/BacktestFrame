# -*- coding: utf-8 -*-

import numpy as np
import sys

def strategy(price, strategy, strat_params=()):
    """
    Given a strategy, return the signal.
    :param price: price series
    :param strategy: a string. 'MA' means Moving Average or 'BnH' means Buy and Hold
    :param strat_params: a tuple of elements, pass the parameters the strategy uses
    :return: strategy signal
    """
    if strategy is 'MA':
        short = strat_params[0]
        long = strat_params[1]
        if len(price) < long + 1:
            return 0
        else:
            ma_short_0 = np.mean(price[-short:])
            ma_short_1 = np.mean(price[-(short + 1):-1])
            ma_long_0 = np.mean(price[-long:])
            ma_long_1 = np.mean(price[-(long + 1):-1])
            if ma_short_0 > ma_long_0 and ma_short_1 < ma_long_1:
                return 1
            if ma_short_0 < ma_long_0 and ma_short_1 > ma_long_1:
                return -1
        return 0
    elif strategy is 'BnH':
        if len(price) == 1:
            return 1


def stop_loss(price, strat_signal, position, stop_loss, stop_strat='percent'):
    if stop_strat is 'percent':
        cost = price[np.where(strat_signal!=0)][-1]
        if position[-1] == 1:
            if price[-1] < cost * (100 - stop_loss) / 100: # 多头止损
                return -1
        elif position[-1] == -1:
            if price[-1] > cost * (100 + stop_loss) / 100: # 空头止损
                return 1
        return 0
    if stop_strat is 'no':
        return 0

def position_control(price, position, strat_signal, stop_signal, double_side=True, position_strategy='all-in'):
    if position_strategy == 'all-in':
        if strat_signal[-1] != 0: # 以交易信号为主
            if (position[-1] < 0 and strat_signal[-1] == 1) or (position[-1] > 0 and strat_signal[-1] == -1) or position[-1] == 0:
                if double_side is True: # 双边交易
                    return strat_signal[-1]
                else:
                    return max(0, strat_signal[-1]) # 单边交易，仓位为正
        if stop_signal[-1] != 0: # 没有交易信号，考虑止损
            return 0
        else:
            return position[-1] # 无交易信号也无止损信号，仓位不变


def package_path():
    """
    :return: current file path
    """
    global path
    path = sys.path[0]
    return path