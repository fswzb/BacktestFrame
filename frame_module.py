# -*- coding: utf-8 -*-

import numpy as np
import sys

def strategy(price, strategy, strat_params=()):
    """
    Given a strategy, return the signal.
    :param price: price series
    :param strategy: a string. 'MA' means Moving Average or 'BnH' means Buy and Hold
    :param strat_params: a tuple of elements, pass the parameters the strategy uses
    :return: strategy signal(1: open long position, 2: close long positoin, -1: open short position, -2: close short position)
    """

    # Moving average strategy
    # strat_params = (short_period, long_period)
    # only return 0, -1 or 1
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

    # Buy and Hold, please set stop_strat = 'no'
    # return 0, 1
    if strategy is 'BnH':
        if len(price) == 1:
            return 1
        return 0

    # Mean Reversion
    # require position infomation
    # strat_params = (sigma estimate period, open criterion, close criterion)
    # return 0, 1, 2, -1, -2
    if strategy is 'Mean_Reversion':
        estimate_period = strat_params[0]
        open_multiple = strat_params[1]
        close_multiple = strat_params[2]
        if len(price) < estimate_period + 1:
            return 0
        else:
            ma_ago = np.mean(price[-(estimate_period+1):-1])
            ma_now = np.mean(price[-estimate_period:])
            std_ago = np.std(price[-(estimate_period+1):-1])
            std_now = np.std(price[-estimate_period:])
            if price[-2] > ma_ago - open_multiple * std_ago and price[-1] < ma_now - open_multiple * std_now: # 下穿下开仓线
                return 1 # 开多
            if price[-2] < ma_ago + open_multiple * std_ago and price[-1] > ma_now + open_multiple * std_now: # 上穿上开仓线
                return -1 # 开空
            if price[-2] < ma_ago - close_multiple * std_ago and price[-1] > ma_now - close_multiple * std_now: # 上穿下平仓线
                return 2 # 平多
            if price[-2] > ma_ago + close_multiple * std_ago and price[-1] < ma_now + close_multiple * std_now: # 下穿上平仓线
                return -2 # 平空
        return 0 # 没有交易信号


def stop_loss(price, strat_signal, stop_loss, stop_strat='percent'):
    """
    stop loss signal
    :param price: price series
    :param strat_signal: strategy_signal
    :param stop_loss: stop_loss percent
    :param stop_strat: 'percent' or 'no'
    :return: 0: no stop, 2: stop long position, -2: stop short position
    """
    if stop_strat is 'percent':
        cost = price[np.where(np.where(strat_signal==-1, 1, strat_signal) == 1)][-1]
        if price[-1] < cost * (100 - stop_loss) / 100: # 多头止损
            return 2
        if price[-1] > cost * (100 + stop_loss) / 100: # 空头止损
            return -2
        return 0
    if stop_strat is 'no':
        return 0

def position_control(price, position, strat_signal, stop_signal, double_side=True, position_strategy='all-in'):
    if position_strategy == 'all-in':
        if strat_signal[-1] != 0: # 以交易信号为主
            if position[-1] == 0:
                if strat_signal[-1] == 1 or strat_signal[-1] == -1: # 开仓信号
                    return strat_signal[-1]
            elif position[-1] == 1:
                if strat_signal[-1] == -1: # 反手信号
                    return -1
                if strat_signal[-1] == 2: # 平多信号
                    return 0
            elif position[-1] == -1:
                if strat_signal[-1] == 1: # 反手信号
                    return 1
                if strat_signal[-1] == -2: #平空信号
                    return 0
        if (stop_signal[-1] == 2 and position[-1] == 1) or (stop_signal[-1] == -2 and position[-1] == -1): # 没有有效交易信号，考虑止损
            return 0
        return position[-1] # 无交易信号也无止损信号，仓位不变


def package_path():
    """
    :return: current file path
    """
    path = sys.path[0]
    return path