# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import frame_main
import frame_module
import time

FutureName = pd.read_csv(frame_module.package_path() + '\FutureName.csv', encoding='gbk', header=0)
time0 = time.time()
returns = dict()
save = list()
all = FutureName.Code.iloc[:-1].tolist()

for i in range(len(FutureName)):
    code = FutureName.Code[i]
    begin = '2006-01-01'
    end = '2017-01-01'
    if code == 'ALL':
        # all.remove(u'RU')
        result = frame_main.multi_test(all, begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    else:
        result = frame_main.multi_test([code], begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    returns[code] = result['returns']
    result.pop('returns')
    print result
    save.append(result)
# buy and hold
begin = '2006-01-01'
end = '2017-01-01'
result = frame_main.multi_test(all, begin, end, 'BnH', (), 'no', double_side=True, pic=True)
result.pop('returns')
save.append(result)

# 储存回测结果
save = pd.DataFrame(save)
save.to_csv(frame_module.package_path() + '\output\\test_result.csv', index=False)

# 计算相关系数
correlation = np.zeros((len(FutureName), len(FutureName)))
for i in range(len(FutureName)):
    code_1 = FutureName.Code[i]
    for j in range(i, len(FutureName)):
        code_2 = FutureName.Code[j]
        length = min(len(returns[code_1]), len(returns[code_2]))
        series_1 = returns[code_1][-length:]
        series_2 = returns[code_2][-length:]
        series_1 = series_1.reshape([1, length])
        series_2 = series_2.reshape([1, length])
        cov = np.cov(series_1, series_2, ddof=0)
        corr = cov[0, 1] / np.std(series_1) / np.std(series_2)
        correlation[i, j] = corr
        correlation[j, i] = corr
print correlation
correlation = pd.DataFrame(correlation, index=FutureName.Code, columns=FutureName.Code)
correlation.to_csv(frame_module.package_path() + '\output\correlation.csv')

print time.time() - time0
