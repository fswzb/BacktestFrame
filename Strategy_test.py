import pandas as pd
import frame_main
import time

FutureName = pd.read_csv('/Users/shawn/Documents/Quant/Internship/QStrategy/BacktestFrame/FutureName.csv', encoding='gbk', header=0)
time0 = time.time()
save = list()

for i in range(len(FutureName)):
    code = FutureName.Code[i]
    begin = '1990-01-01'
    end = '2017-01-01'
    # special criterion
    # if code =='CF':
    #     begin = '2008-01-01'
    # if code == 'RO':
    #     end = '2013-04-26'
    if code == 'ALL':
        all = FutureName.Code.iloc[:-1].tolist()
        # all.remove(u'RU')
        result = frame_main.test(all, begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    else:
        result = frame_main.test([code], begin, end, 'MA', (5, 20), 'percent', double_side=True, pic=True)
    # result = pd.DataFrame.from_dict(result)
    # result.to_csv('C:\lx\FutureStrategy\\returns\%s_return.csv' % code)
    save.append(result)
# buy and hold
begin = '1990-01-01'
end = '2017-01-01'
result = frame_main.test(all, begin, end, 'BnH', (), 'no', double_side=True, pic=True)
save.append(result)
save = pd.DataFrame(save)
save.to_csv('/Users/shawn/Documents/Quant/Internship/QStrategy/BacktestFrame/output/test_result.csv', index=False)
print time.time() - time0