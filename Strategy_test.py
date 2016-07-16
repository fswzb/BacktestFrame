# -*- coding: utf-8 -*-

import pandas as pd
import frame_main
import frame_module
import time

FutureName = pd.read_csv(frame_module.package_path() + '\FutureName.csv', encoding='gbk', header=0)
time0 = time.time()
save = list()

for i in range(len(FutureName)):
    code = FutureName.Code[i]
    begin = '1990-01-01'
    end = '2017-01-01'
    if code == 'ALL':
        all = FutureName.Code.iloc[:-1].tolist()
        # all.remove(u'RU')
        result = frame_main.test(all, begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    else:
        result = frame_main.test([code], begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    print 'a', result.pop('returns')
    print 'b', result
    save.append(result)
# buy and hold
begin = '1990-01-01'
end = '2017-01-01'
result = frame_main.test(all, begin, end, 'BnH', (), 'no', double_side=True, pic=True)
save.append(result)
# 储存回测结果
save = pd.DataFrame(save)
save.to_csv(frame_module.package_path() + '\output\\test_result.csv', index=False)
print time.time() - time0