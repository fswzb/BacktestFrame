# -*- coding: utf-8 -*-

import numpy as np
import frame_block

def test(future_code, begin, end, strategy, strat_params=(), output='info', pic=False):
    name = '-'.join(future_code)
    initial_value = 1. / len(future_code)

    tick = dict(CU=10, AL=5, ZN=5, AU=0.01, RU=5, RB=5, AG=1, M=1,
                A=1, C=1, Y=2, L=5, P=2, V=5, J=1, JM=1, SR=1, CF=5,
                TA=2, RO=2, ME=1, FG=1, RM=1, I=0.5, BU=2, CS=1, HC=1,
                JD=1, MA=1, NI=2, PP=1, ZC=1)

    data, date, max_length = frame_block.get_data(future_code, begin, end)

    # 回测
    portfolio_values = list()
    for code in future_code:
        value, position = frame_block.back_test(data[code], strategy, strat_params, 5, 2, tick[code], 1, initial_value)
        value = np.append(np.ones(max_length - len(data[code])) * initial_value, value)
        position = np.append(np.zeros(max_length - len(data[code])), position)
        portfolio_values.append(value)
        frame_block.save_output(position, strategy, name)
    portfolio_value = sum(portfolio_values)
    frame_block.save_output(portfolio_value, strategy, name)
    # 绘图
    if pic is True:
        frame_block.pic(future_code, portfolio_values, portfolio_value, data, date, name, strategy)

    # 计算比率
    return frame_block.evaluate(portfolio_value, strategy, strat_params, name, output)

if __name__ == '__main__':
    test(['RU'], '1990-01-01', '2017-01-01', 'MA', strat_params=(5, 20), pic=True)
