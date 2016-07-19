import frame_main
import frame_module
import numpy as np
import pandas as pd

pairs = [['CU_LME', 'CU'], ['ZN_LME', 'ZN'], ['NI_LME', 'NI'], ['AL_LME', 'AL']]
returns = dict()
save = list()
for pair in pairs:
    result = frame_main.cross_trade_test(pair, '2010-01-01', '2016-01-01', 'Mean_Reversion', (20, 1.5, 0.5), 'percent', 3, double_side=True, pic=False)
    returns[pair[0]] = result['returns']
    result.pop('returns')
    print result
    save.append(result)
save = pd.DataFrame(save)
save.to_csv(frame_module.package_path() + '\output\\test_result_cross_market.csv', index=False)

correlation = np.zeros([4, 4])
for i in range(4):
    code_1 = pairs[i][0]
    for j in range(i, 4):
        code_2 = pairs[j][0]
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
correlation = pd.DataFrame(correlation, index=[pair[0] for pair in pairs], columns=[pair[0] for pair in pairs])
correlation.to_csv(frame_module.package_path() + '\output\correlation_cross_market.csv')

