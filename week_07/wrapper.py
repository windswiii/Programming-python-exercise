import os
import csv
import sys
from playsound import playsound
from line_profiler import LineProfiler
from memory_profiler import profile
from tqdm import tqdm
from pysnooper import snoop

#路径检查
def pathcheck(func):
    def wrapper(path):
        directory = '/'.join(path.split('/')[:-1])
        if os.path.exists(directory) == 0:
            print('The folder \"{0}\" does not exist.'.format(directory))
            c = input('Create this folder?(Y/N)')
            if c == 'Y':
                os.mkdir(directory)
            else: return
        return func(path)
    return wrapper

@pathcheck
def savetxt(path):
    with open(path, 'w', encoding = 'utf-8') as outfile:
        pass   

# savetxt('result/wrapperr/test_1.txt')


#声音通知
class Ring():
    def __init__(self):
        pass
    
    def __ring(self, arg):
        t =  type(arg)
        if t == int:
            playsound('D:/HUAWEI/Documents/all_code/Python/Data/wrapper/ring_1.mp3')
        elif t == str:
            playsound('D:/HUAWEI/Documents/all_code/Python/Data/wrapper/ring_2.mp3')
        elif t in [list, tuple, dict]:
            playsound('D:/HUAWEI/Documents/all_code/Python/Data/wrapper/ring_3.mp3')
        else:
            playsound('D:/HUAWEI/Documents/all_code/Python/Data/wrapper/ring_4.mp3')
    
    def __call__(self, func):
        def wrapper(*args):
            res = func(*args)
            if type(res) == tuple:
                for r in res:
                    self.__ring(r)
            else:
                self.__ring(res)
            return res
        return wrapper

@Ring()    
def add_mul(a, b):
    return (a + b), a * b, [a, b], str(a), str(b)
    
# add_mul(1, 2)



#输出转入文件
DATA_PATH = 'Data/PRSA_Data'
OUT_PATH = 'result/wrapper/'
def logging(log_path):
    def warpper0(func):
        def wrapper1(*args):
            savedStdout = sys.stdout
            print_log = open(log_path,"w")
            sys.stdout = print_log
            func(*args)
            sys.stdout = savedStdout
        return wrapper1
    return warpper0

lp = LineProfiler()
class DataAnalyze:
    '''
    读入数据,统计时间及空间分布
    '''
    def __init__(self, data_path):
        self.data_path = data_path

    @logging('result/wrapper/log_1.txt')
    @lp
    def load_data(self):
        data_path = self.data_path
        prsa_data = {}
        
        for path in os.listdir(data_path):
            print('Reading ' + path + '...')
            with open(data_path + '/' + path, 'r', encoding = 'utf-8') as infile:
                data = list(csv.DictReader(infile))
                
                washdata = []
                for i in range(len(data)):
                #for i in tqdm(range(len(data)), desc = path):
                    row = data[i]
                    for key in row.keys():
                        if (row[key] == '') or (row[key] == 'NA'):
                            print('The file {}, line {}, the value of {} is empty.'.format(path, i+2, key))
                            row[key] = data[i - 1][key]          
                    washdata.append(row)
                
                zone = path.split('_')[2]
                prsa_data[zone] = washdata
                
        self.prsa_data = prsa_data
    
    @profile()
    # @snoop()
    def temporal_pattern(self, zone, *pollutant):
        temporal_data = {}
        for pol in pollutant:
            temporal_data[pol] = [0] * 48
        
        for row in self.prsa_data[zone]:
            month = (int(row['year']) - 2013) * 12 + int(row['month']) - 3
            for pol in pollutant:
                temporal_data[pol][month] += float(row[pol])
        
        with open(OUT_PATH + 'temporal_data_' + zone + '.txt', 'w', encoding = 'utf-8') as outfile:
            for pol in pollutant:
                print('%5s' % pol, ':', temporal_data[pol], file = outfile)
                
        return temporal_data
    
data0 = DataAnalyze(DATA_PATH)
data0.load_data()
lp.print_stats()
data0.temporal_pattern('Changping', 'PM2.5', 'PM10', 'SO2')