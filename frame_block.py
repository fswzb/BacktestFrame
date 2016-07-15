# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import frame_module


def get_data(FutureCode, Begin, End):
    data = dict()
    length = list()
    for code in FutureCode:
        data[code] = pd.read_csv(frame_module.package_path() + '\MajorContract\%s.csv' % code,
            dtype={'Close': np.double, 'Contract': str, 'Date': pd.datetime, 'Volume': np.double})
        # data[code] = pd.read_csv(
        #         '/Users/shawn/Documents/Quant/Internship/QStrategy/FuturesBacktest/commodity/%s%s.csv' % (code, code),
        #         dtype={'Close': np.double, 'Date': pd.datetime, 'Volume': np.double})
        data[code] = data[code][data[code].Date >= Begin][data[code].Date <= End]
        length.append(len(data[code]))
    max_length = max(length)
    date = data[FutureCode[length.index(max(length))]].Date
    return data, date, max_length

def back_test(data, strategy, strat_params, Stoploss, Slippage, tick, initial_value=1):
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
            signal = frame_module.MA(price[:i + 1], Short, Long) # 1: buy; -1: sell; 0: no trade.
        if strategy == 'BnH':
            signal = frame_module.buy_and_hold(price[:i + 1])
        # 止损
        if position[-1] != 0:
            stop_loss = frame_module.stop_loss(price[i], position[-1], cost_price, Stoploss) # 1: buy; -1: sell; 0: no trade.
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
    return value, position


def save_output(data, strategy, name):
    pd.DataFrame(data).to_csv(frame_module.package_path() + '\\output\positions\%s_%s.csv' % (strategy, name))

def evaluate(portfolio_value, strategy, strat_params, name, output):
    returns = (portfolio_value[1:] - portfolio_value[0:-1]) / portfolio_value[0:-1]
    # 1. return
    final_return = ((portfolio_value - 1) / 1)[-1]
    annul_return = (final_return + 1) ** (1. / len(returns) * 250) - 1

    # 2. volatility
    volatility = float(np.std(returns))
    annul_volatility = volatility * np.sqrt(250)

    # 3. max drawdown
    length = len(portfolio_value)
    drawdown = list()
    for i in range(length):
        drawdown.append(1 - portfolio_value[i] / max(portfolio_value[0:i + 1]))
    maxdrawdown = max(drawdown)

    # 4. sharp ratio
    sharp = (annul_return - 0.02) / annul_volatility

    # 5. sortino ratio
    annul_down_std = np.sqrt(
        np.sum(((abs(returns - np.mean(returns)) - (returns - np.mean(returns))) / 2) ** 2) / len(returns)) * np.sqrt(250)
    sortino = (annul_return - 0.02) / annul_down_std
    if output is 'info':
        info =  {'portfolio': name,
                'annul return': annul_return,
                'annul volatility': annul_volatility,
                'max drawdown': maxdrawdown,
                'sharp': sharp,
                'sortino': sortino,
                'total return / dawndown': final_return / maxdrawdown,
                'strategy': strategy + str(strat_params)
                }
        print info
        return info
    if output is 'returns':
        return returns

def pic(future_code, portfolio_values, portfolio_value, data, date, name, strategy):
    plt.figure(figsize=(16,9))
    ax = plt.subplot()
    if len(future_code) > 1:
        for i in range(len(future_code)):
            plt.plot(np.array(portfolio_values[i]), label=future_code[i])
        plt.plot(portfolio_value, linewidth=1.5, label='Portfolio Value')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[-1:], labels[-1:], fontsize=10, loc=2)
    else:
        plt.plot(np.array(data[future_code[0]].Close) / data[future_code[0]].Close.iat[0], label = 'Benchmark')
        plt.plot(portfolio_value, linewidth=1.5, label='Portfolio Value')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[-2:], labels[-2:], fontsize=10, loc=2)
    xtick = np.floor(np.linspace(0, len(portfolio_value) - 1, 5)).astype(int)
    ax.set_xticks(xtick)
    ax.set_ylim(bottom=0)
    label = list()
    for i in range(0, 5):
        label.append(date.iat[xtick[i]])
    ax.set_xticklabels(label)
    plt.title(name)
    plt.savefig(frame_module.package_path() + '\output\pics\%s_%s.png' % (strategy, name), dpi=100)
    plt.close('all')