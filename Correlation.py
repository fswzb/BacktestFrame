import MA
import pandas as pd
import numpy as np

FutureName = pd.read_csv('C:\lx\FutureName.csv', encoding='gbk', header=0)
returns = dict()
for i in range(len(FutureName)):
    code = FutureName.Code[i]
    print 'Loop ', i
    print code
    begin = '1990-01-01'
    end = '2017-01-01'
    # special criterion
    if code =='CF':
        begin = '2008-01-01'
    if code == 'RO':
        end = '2013-04-26'
    if code == 'ALL':
        returns[code] = MA.MA(FutureName.Code[:-1].tolist(), begin, end,'MA', Output='returns')
    else:
        returns[code] = MA.MA([code], begin, end,'MA', Output='returns')
    pd.DataFrame(returns[code]).to_csv('C:\lx\BacktestFrame\\returns\\returns_%s.csv' % code)

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

correlation.to_csv('C:\lx\BacktestFrame\output\correlation.csv')