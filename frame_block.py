# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import frame_model

def back_test(data, strategy, Stoploss, Slippage, tick, initial_value=1):
    Short = 5
    Long = 20
    price = np.array(data.Close)
    value = np.array([initial_value]) # initial asset
    position = np.array([0]) # 1 = long; -1 = short
    cost_price = 0
    cost_value = value[-1]
    signal = 0 # trade signal
    for i in range(len(data)):
        # 计算今日价值
        if i > 0:
            if position[-1] == 1:
                value = np.append(value, price[i] / cost_price * cost_value)
            elif position[-1] == 0:
                if signal is 0:
                    value = np.append(value, value[-1])
                elif signal == -1: # 卖出止损
                    value = np.append(value, (price[i] - Slippage * tick) / cost_price * cost_value)
                elif signal == 1: # 买入止损
                    value = np.append(value, (2 * cost_price - price[i] - Slippage * tick) / cost_price * cost_value)
            elif position[-1] == -1:
                value = np.append(value, (2 * cost_price - price[i]) / cost_price * cost_value)
        # 计算今日收盘时买卖信号
        if strategy == 'MA':
            signal = frame_model.MA(price[:i + 1], Short, Long) # 1: buy; -1: sell; 0: no trade.
        if strategy == 'BnH':
            signal = frame_model.buy_and_hold(price[:i + 1])
        # 止损
        if position[-1] != 0:
            stop_loss = frame_model.stop_loss(price[i], position[-1], cost_price, Stoploss) # 1: buy; -1: sell; 0: no trade.
        else:
            stop_loss = 0
        # 更新仓位
        if signal != 0:
            if position[-1] == 0: # 开仓
                if signal is 1: # 多头
                    position = np.append(position, 1)
                    cost_price = price[i] + Slippage * tick
                    cost_value = value[i]
                elif signal is -1: # 空头
                    position = np.append(position, -1)
                    cost_price = price[i] - Slippage * tick
                    cost_value = value[i]
            elif position[-1] == 1:
                if signal is -1: # 卖出平仓,空头开仓
                    value[-1] = value[-1] - Slippage * tick / cost_price * cost_value # 加入平仓滑点
                    position = np.append(position, -1)
                    cost_price = price[i] - Slippage * tick
                    cost_value = value[i]
            elif position[-1] == -1: # 买入平仓,多头开仓
                if signal is 1:
                    value[-1] = value[-1] - Slippage * tick / cost_price * cost_value # 加入平仓滑点
                    position = np.append(position, 1)
                    cost_price = price[i] + Slippage * tick
                    cost_value = value[i]
        elif stop_loss != 0: # 若没有信号,则考虑止损
            position = np.append(position, 0)
            signal = stop_loss
        else:
            position = np.append(position, position[-1])
        # print position, value
    print len(position), len(value)
    return value, position

def get_data(FutureCode, Begin, End):
    data = dict()
    length = list()
    for code in FutureCode:
        data[code] = pd.read_csv('C:\lx\MajorContract\%s.csv' % code,
            dtype={'Close': np.double, 'Contract': str, 'Date': pd.datetime, 'Volume': np.double})
        # data[code] = pd.read_csv(
        #         '/Users/shawn/Documents/Quant/Internship/QStrategy/FuturesBacktest/commodity/%s%s.csv' % (code, code),
        #         dtype={'Close': np.double, 'Date': pd.datetime, 'Volume': np.double})
        data[code] = data[code][data[code].Date >= Begin][data[code].Date <= End]
        length.append(len(data[code]))
    max_length = max(length)
    date = data[FutureCode[length.index(max(length))]].Date
    return data, date, max_length
