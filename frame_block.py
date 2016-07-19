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
        data[code] = data[code][data[code].Date >= Begin][data[code].Date <= End]
        length.append(len(data[code]))
    max_length = max(length)
    min_length = min(length)
    max_date = data[FutureCode[length.index(max_length)]].Date
    min_date = data[FutureCode[length.index(min_length)]].Date
    return {'data': data,
            'max_date': max_date,
            'min_date': min_date,
            'max_length': max_length,
            'min_length': min_length}


def get_position(price, strategy, strat_params, stop_strat, stop_loss, double_side=True):
    # parameters

    strat_signal = np.array([]) # strategy signal 1 = buy; -1 = sell.
    stop_signal = np.array([]) # stop loss signal 1 = buy; -1 = sell.
    position = np.array([0]) # positive means long position, negative means short position.
    # 逐日获取交易信号
    for i in range(len(price)):
        # 策略信号
        strat_signal = np.append(strat_signal, frame_module.strategy(price[:i + 1], strategy, strat_params))
        # 止损信号
        if position[-1] != 0:
            stop_signal = np.append(stop_signal, frame_module.stop_loss(price[:i + 1], strat_signal, stop_loss, stop_strat)) # 1: buy; -1: sell; 0: no trade.
        else:
            stop_signal = np.append(stop_signal, 0)
        # 更新仓位
        position = np.append(position, frame_module.position_control(price[:i + 1], position, strat_signal, stop_signal, double_side=double_side, position_strategy='all-in'))
    position = position[:-1] # 对齐序列
    return strat_signal, stop_signal, position


def get_adjusted_returns(price, position, slippage, tick):
    """
    根据滑点，获取标的资产调整收益率
    :param price:
    :param strategy:
    :param position:
    :param slippage:
    :param tick:
    :return:
    """
    # 计算标的资产收益率
    asset_returns = (price[1:] - price[:-1]) / price[:-1]
    asset_returns = np.append(0, asset_returns)
    # 根据滑点调整收益率(采用近似公式)
    adjust_asset_returns = asset_returns
    for i in range(1, len(asset_returns)):
        if (position[i - 1] == 0 and position[i] == 1): # 开多滑点
            adjust_asset_returns[i] = adjust_asset_returns[i] - slippage * tick / price[i - 1]
        elif (position[i - 1] == 0 and position[i] == -1): # 开空滑点
            adjust_asset_returns[i] = adjust_asset_returns[i] + slippage * tick / price[i - 1]
        elif (position[i - 1] == 1 and position[i] == 0): # 平多滑点
            adjust_asset_returns[i - 1] = adjust_asset_returns[i - 1] - slippage * tick / price[i - 2]
        elif (position[i - 1] == -1 and position[i] == 0): # 平空滑点
            adjust_asset_returns[i - 1] = adjust_asset_returns[i - 1] + slippage * tick / price[i - 2]
        elif (position[i - 1] == -1 and position[i] == 1): # 反手滑点
            adjust_asset_returns[i - 1] = adjust_asset_returns[i - 1] + slippage * tick / price[i - 2]
            adjust_asset_returns[i] = adjust_asset_returns[i] - slippage * tick / price[i - 1]
        elif (position[i - 1] == 1 and position[i] == -1):
            adjust_asset_returns[i - 1] = adjust_asset_returns[i - 1] - slippage * tick / price[i - 2]
            adjust_asset_returns[i] = adjust_asset_returns[i] + slippage * tick / price[i - 1]
    return adjust_asset_returns

def get_value(adjust_asset_returns, position, margin=1, initial_value=1):
    """
    获取组合价值(独立资金)
    :param adjust_asset_returns:
    :param position:
    :param margin:
    :param initial_value:
    :return:
    """
    # 计算策略收益率(考虑杠杆)
    returns = adjust_asset_returns * position / margin
        # 计算策略价值
    value = initial_value * np.cumprod(returns + 1)
    return value


def save_output(data, folder, strategy, name):
    pd.DataFrame(data).to_csv(frame_module.package_path() + '\output\\' + folder + '\%s_%s.csv' % (strategy, name))

def evaluate(portfolio_value, strategy, strat_params, name):
    returns = np.append(0, (portfolio_value[1:] - portfolio_value[:-1]) / portfolio_value[:-1])
    save_output(returns, 'returns', strategy, name)
    # 1. return
    final_return = (portfolio_value[-1] - 1) / 1
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
    info =  {'portfolio': name,
            'annul return': annul_return,
            'annul volatility': annul_volatility,
            'max drawdown': maxdrawdown,
            'sharp': sharp,
            'sortino': sortino,
            'total return / dawndown': final_return / maxdrawdown,
            'strategy': strategy + str(strat_params),
            'returns': returns
            }
    return info

def pic(future_code, portfolio_values, portfolio_value, data, date, name, strategy):
    plt.figure(figsize=(16,9))
    ax = plt.subplot()
    print future_code
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