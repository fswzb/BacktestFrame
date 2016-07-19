# -*- coding: utf-8 -*-

import numpy as np
import frame_block
import frame_module
import pandas as pd
import matplotlib.pyplot as plt


def multi_test(future_code, begin, end, strategy, strat_params, stop_strat, stop_loss=3, slippage=2, double_side=True, pic=False):
    """
    多品种组合回测，各个组合平均配资，策略相同，独立交易
    :param future_code:
    :param begin:
    :param end:
    :param strategy:
    :param strat_params:
    :param stop_strat:
    :param double_side:
    :param pic:
    :return:
    """
    name = '-'.join(future_code)
    initial_value = 1. / len(future_code) # 平均分配给各个标的资产

    tick = dict(CU=10, AL=5, ZN=5, AU=0.01, RU=5, RB=5, AG=1, M=1,
                A=1, C=1, Y=2, L=5, P=2, V=5, J=1, JM=1, SR=1, CF=5,
                TA=2, RO=2, ME=1, FG=1, RM=1, I=0.5, BU=2, CS=1, HC=1,
                JD=1, MA=1, NI=2, PP=1, ZC=1)
    res = frame_block.get_data(future_code, begin, end)
    data = res['data']
    date = res['max_date']
    max_length = res['max_length']

    # 回测
    portfolio_values = list()
    for code in future_code:
        # 获取信号
        strat_signal, stop_signal, position = frame_block.get_position(np.array(data[code].Close), strategy, strat_params, stop_strat, stop_loss, double_side)
        # 考虑滑点，计算调整收益率
        adjusted_returns = frame_block.get_adjusted_returns(np.array(data[code].Close), position, slippage, tick[code])
        # 计算组合价值
        value = frame_block.get_value(adjusted_returns, position, 1, initial_value)
        # 对齐时间
        value = np.append(np.ones(max_length - len(data[code])) * initial_value, value)
        position = np.append(np.zeros(max_length - len(data[code])), position)
        portfolio_values.append(value)
        frame_block.save_output(position, 'positions',strategy, name)
    # 汇总各品种得到组合总价值
    portfolio_value = sum(portfolio_values)
    frame_block.save_output(portfolio_value, 'values', strategy, name)

    # 绘图
    if pic is True:
        frame_block.pic(future_code, portfolio_values, portfolio_value, data, date, name, strategy)

    # 计算比率
    return frame_block.evaluate(portfolio_value, strategy, strat_params, name)


def cross_trade_test(future_code, begin, end, strategy, strat_params, stop_strat, stop_loss=3, slippage=2, double_side=True, pic=False):
    """
    跨品/跨市交易，配对反向操作，双向配资量相同
    :param future_code:
    :param begin:
    :param end:
    :param strategy:
    :param strat_params:
    :param stop_strat:
    :param double_side:
    :param pic:
    :return:
    """
    name = '-cross-'.join(future_code)
    tick = dict(CU=10, AL=5, ZN=5, NI=2, CU_LME=0.25, NI_LME=1,
                ZN_LME=0.25, AL_LME=0.25, CU_LME_min=0.25, CU_min=10)
    unit = dict()
    future_code.append('USDCNY')
    res = frame_block.get_data(future_code, begin, end)

    data = res['data']
    merge_1 = pd.merge(data[future_code[0]], data[future_code[1]], on='Date')
    merge_2 = pd.merge(merge_1, data[future_code[2]], on='Date')
    length = len(merge_2)
    date = merge_2.Date
    future_code.pop(2)


    exchage_rate = np.array(merge_2.Close)
    price_0 = np.array(merge_2.Close_x)
    price_1 = np.array(merge_2.Close_y)
    spread = price_0 * exchage_rate - price_1

    # 回测
    strat_signal, stop_signal, position = frame_block.get_position(spread, strategy, strat_params, stop_strat, 3, double_side)
    adjusted_returns_0 = frame_block.get_adjusted_returns(price_0, position, slippage, tick[future_code[0]])
    adjusted_returns_1 = frame_block.get_adjusted_returns(price_1, -position, slippage, tick[future_code[1]])

    # 资金涉及再分配，不能调用get_value函数
    value_0 = [0.5]
    value_1 = [0.5]
    for i in range(1, len(position)):
        if position[i] == 0: # 空仓或平仓
            value_0.append(value_0[-1])
            value_1.append(value_1[-1])
        elif position[i-1] != position[i]: # 新开仓，平均配资
            value_0.append((adjusted_returns_0[i] * position[i] + 1) * (value_0[-1] + value_1[-1]) / 2)
            value_1.append((adjusted_returns_1[i] * -position[i] + 1) * (value_0[-1] + value_1[-1]) / 2)
        elif position[i-1] == position[i]: # 持仓
            value_0.append((adjusted_returns_0[i] * position[i] + 1) * value_0[-1])
            value_1.append((adjusted_returns_1[i] * -position[i] + 1) * value_1[-1])

    portfolio_value = np.array(value_0) + np.array(value_1)
    frame_block.save_output(position, 'positions',strategy, name)
    frame_block.save_output(stop_signal, 'stoploss',strategy, name)
    frame_block.save_output(strat_signal, 'signal',strategy, name)
    frame_block.save_output(portfolio_value, 'values', strategy, name)
    frame_block.save_output(merge_2, '', strategy, name)

    # 绘图
    plt.figure(figsize=(16,9))
    ax1 = plt.subplot()
    ax2 = ax1.twinx()
    ax1.plot(portfolio_value, 'r-', label='portfolio_value', linewidth=1.5)
    ax2.plot(spread, 'g-', label='spread')

    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, fontsize=10, loc=2)
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, fontsize=10, loc=1)
    xtick = np.floor(np.linspace(0, len(portfolio_value) - 1, 5)).astype(int)
    ax1.set_xticks(xtick)
    ax1.set_ylim(bottom=0)
    label = list()
    for i in range(0, 5):
        label.append(date.iat[xtick[i]])
    ax1.set_xticklabels(label)
    plt.title(name + str(strat_params))
    plt.savefig(frame_module.package_path() + '\output\pics\%s_%s%s.png' % (strategy, name, str(strat_params)), dpi=100)
    plt.close('all')


    # 计算比率
    return frame_block.evaluate(portfolio_value, strategy, strat_params, name)


if __name__ == '__main__': # 测试
    multi_test(['V'], '2007-01-01', '2017-01-01', 'Mean_Reversion', (20, 1.5, 0.5), 'percent', 3, pic=True)
    # cross_trade_test(['CU_LME_min', 'CU_min'], '2016-07-05  21:00:05', '2016-07-19  14:59:05', 'Mean_Reversion', (20, 2, -2), 'percent', 3, double_side=True, pic=False)
