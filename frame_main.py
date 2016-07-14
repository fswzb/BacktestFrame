# -*- coding: utf-8 -*-

import numpy as np
import frame_brick
import matplotlib.pyplot as plt
import pandas as pd


def MA(future_code, begin, end, strategy, strat_params, output='info', pic=False):
    # future_code = ['CU']
    # begin = '1990-01-01'
    # end = '2017-01-01'
    initial_value = 1. / len(future_code)

    tick = dict(CU=10, AL=5, ZN=5, AU=0.01, RU=5, RB=5, AG=1, M=1,
                A=1, C=1, Y=2, L=5, P=2, V=5, J=1, JM=1, SR=1, CF=5,
                TA=2, RO=2, ME=1, FG=1, RM=1, I=0.5, BU=2, CS=1, HC=1,
                JD=1, MA=1, NI=2, PP=1, ZC=1)

    data, date, max_length = frame_brick.get_data(future_code, begin, end)
    name = '-'.join(future_code)

    # 回测
    portfolio_values = list()
    for code in future_code:
        value, position = frame_block.back_test(data[code], strategy, strat_params, 3, 3, tick[code], initial_value)
        value = np.append(np.ones(max_length - len(data[code])) * initial_value, value)
        position = np.append(np.zeros(max_length - len(data[code])), position)
        portfolio_values.append(value)
        pd.DataFrame(position).to_csv('C:\lx\BacktestFrame\\positions\%s_%s.csv' % (strategy, name))
    portfolio_value = sum(portfolio_values)

    pd.DataFrame(portfolio_value).to_csv('C:\lx\BacktestFrame\\values\%s_%s.csv' % (strategy, name))
    # 绘图
    if pic is True:
        ax = plt.subplot()
        for i in range(len(future_code)):
            plt.plot(np.array(portfolio_values[i]), label=future_code[i])
            # plt.plot(np.array(data[code].Close) / data[code].Close.iat[0], label = 'Benchmark')
        plt.plot(portfolio_value, linewidth=0.5, label='Portfolio Value')
        # handles, labels = ax.get_legend_handles_labels()
        # ax.legend(handles, labels, fontsize=10, loc=2)
        xtick = np.floor(np.linspace(0, len(portfolio_value) - 1, 5)).astype(int)
        ax.set_xticks(xtick)
        label = list()
        for i in range(0, 5):
            label.append(date.iat[xtick[i]])
        ax.set_xticklabels(label)
        plt.title(name)
        plt.savefig('C:\lx\BacktestFrame\pics\%s_%s.png' % (strategy, name))
        plt.close('all')

    # 计算比率
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

    # output
    if output is 'info':
        return {'portfolio': name,
                'annul return': annul_return,
                'annul volatility': annul_volatility,
                'max drawdown': maxdrawdown,
                'sharp': sharp,
                'sortino': sortino,
                'total return / dawndown': final_return / maxdrawdown,
                'strategy': strategy + str(strat_params)
                }
    if output is 'returns':
        return returns

# MA(['ZC'], '1990-01-01', '2017-01-01', 'MA')
