# Wrappers

## 库管理

```python
import os
import csv
import sys
from playsound import playsound
from line_profiler import LineProfiler
from memory_profiler import profile
from tqdm import tqdm
from pysnooper import snoop
```

## 各装饰器实现

### 路径检查

截取输入的文件路径的目录部分（即截去最后一个"/"以及其后的内容）。

```python
directory = '/'.join(path.split('/')[:-1])
```

用`os.path.exists`方法判断该目录是否存在，若不存在则提示创建文件夹。

```python
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
```

对该装饰器进行测试：

```python
@pathcheck
def savetxt(path):
    with open(path, 'w', encoding = 'utf-8') as outfile:
        pass   

savetxt('result/wrapper/test_1.txt')
```

```python
> The folder "result/wrapper" does not exist.
> Create this folder?(Y/N)Y
```

已创建wrapper文件夹后再次运行，没有错误提示。

### 声音通知

实现`Ring`装饰器类。

内部方法`__ring()`，用于判断单个参数类型并播放对应音效。

在`__call__`中根据返回值的数量调用`__ring`方法。

```python
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
```

对该装饰器进行测试：

```python
@Ring()    
def add_mul(a, b):
    return (a + b), a * b, [a, b], str(a), str(b)
    
add_mul(1, 2)
```

声音播放正常。

------

###### 后续装饰器在第7周作业中`DataAnalyze`类基础上进行测试:

```python
class DataAnalyze:
	def __init__(self, data_path):
        ...
	def load_data(self):
        ...
    def temporal_pattern(self, zone, *pollutant):
        ...
```

### 将函数的中间结果输入到文件中

原函数在进行数据清洗时会直接在控制台打印错误信息。

```python
		washdata = []
        for i in tqdm(range(len(data)), desc = path):
            row = data[i]
            for key in row.keys():
                if (row[key] == '') or (row[key] == 'NA'):
                    print('The file {}, line {}, the value of {} is empty.'.format(path, i+2, key))
                    row[key] = data[i - 1][key]          
            washdata.append(row)
```

要将这些输出保存到文件中，可通过改变系统的标准输出流来实现。

```python
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
```

对`load_data()`函数添加装饰器：

```python
@logging('result/wrapper/log_1.txt')
```

错误日志已经记录在文件`log_1.txt`中：

```
Reading PRSA_Data_Aotizhongxin_20130301-20170228.csv...
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 76, the value of SO2 is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 77, the value of CO is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 78, the value of NO2 is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 126, the value of CO is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 172, the value of SO2 is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 173, the value of CO is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 174, the value of NO2 is empty.
The file PRSA_Data_Aotizhongxin_20130301-20170228.csv, line 180, the value of CO is empty.
......
```

## 其他调试装饰器

### line_profiler

```python
lp = LineProfiler()
@lp
def load_data(self):
	...
	
lp.print_stats()
```

结果如下：

```python
Total time: 13.0032 s
File: d:\HUAWEI\Documents\all_code\Python\works\wrapper.py
Function: load_data at line 88

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    88                                               @logging('result/wrapper/log_1.txt')
    89                                               @lp
    90                                               def load_data(self):
    91         1         20.0     20.0      0.0          data_path = self.data_path
    92         1          7.0      7.0      0.0          prsa_data = {}
    93
    94        13       1029.0     79.2      0.0          for path in os.listdir(data_path):
    95        12        758.0     63.2      0.0              print('Reading ' + path + '...')
    96        12      22386.0   1865.5      0.0              with open(data_path + '/' + path, 'r', encoding = 'utf-8') as infile:
    97        12   31121345.0 2593445.4     23.9                  data = list(csv.DictReader(infile))
    98
    99        12        282.0     23.5      0.0                  washdata = []
   100    420780   10473323.0     24.9      8.1                  for i in tqdm(range(len(data)), desc = path):
   101    420768    2355188.0      5.6      1.8                      row = data[i]
   102   7994592   36824593.0      4.6     28.3                      for key in row.keys():
   103   7573824   43574622.0      5.8     33.5                          if (row[key] == '') or (row[key] == 'NA'):
   104     74027    2458441.0     33.2      1.9                              print('The file {}, line {}, the value of {} is empty.'.format(path, i+2, key))
   105     74027     568068.0      7.7      0.4                              row[key] = data[i - 1][key]
   106    420768    2627608.0      6.2      2.0                      washdata.append(row)
   107
   108        12        441.0     36.8      0.0                  zone = path.split('_')[2]
   109        12       4006.0    333.8      0.0                  prsa_data[zone] = washdata
   110
   111         1         17.0     17.0      0.0          self.prsa_data = prsa_data
```

### memory_profiler

```python
@profile()
def temporal_pattern(self, zone, *pollutant):
	...
```

结果如下：

```python
Line #    Mem usage    Increment  Occurrences   Line Contents
=============================================================
   113    696.3 MiB    696.3 MiB           1       @profile()
   114                                             # @snoop()
   115                                             def temporal_pattern(self, zone, *pollutant):
   116    696.3 MiB      0.0 MiB           1           temporal_data = {}
   117    696.3 MiB      0.0 MiB           4           for pol in pollutant:
   118    696.3 MiB      0.0 MiB           3               temporal_data[pol] = [0] * 48
   119
   120    696.3 MiB      0.0 MiB       35065           for row in self.prsa_data[zone]:
   121    696.3 MiB      0.0 MiB       35064               month = (int(row['year']) - 2013) * 12 + int(row['month']) - 3
   122    696.3 MiB      0.0 MiB      140256               for pol in pollutant:
   123    696.3 MiB      0.0 MiB      105192                   temporal_data[pol][month] += float(row[pol])
   124
   125    696.3 MiB      0.0 MiB           1           with open(OUT_PATH + 'temporal_data_' + zone + '.txt', 'w', encoding = 'utf-8') as outfile:
   126    696.3 MiB      0.0 MiB           4               for pol in pollutant:
   127    696.3 MiB      0.0 MiB           3                   print('%5s' % pol, ':', temporal_data[pol], file = outfile)
   128
   129    696.3 MiB      0.0 MiB           1           return temporal_data
```

### tqdm

在`load_data()`函数中添加进度条显示。在数据清洗时文件遍历的迭代器上添加`tqdm()`。

原语句：

```python
for i in range(len(data)):
```

添加进度条（`desc`参数用于为进度条添加描述信息）：

```python
for i in tqdm(range(len(data)), desc = path):
```

### pysnooper

部分调试信息如下：

```python
...
Modified var:.. pol = 'PM2.5'
22:35:14.858925 line       123                 temporal_data[pol][month] += float(row[pol])
Modified var:.. temporal_data = {'PM2.5': [73594.0, 42978.0, 61745.0, 24612.0, 0... 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
22:35:14.858925 line       122             for pol in pollutant:
Modified var:.. pol = 'PM10'
22:35:14.858925 line       123                 temporal_data[pol][month] += float(row[pol])
22:35:14.858925 line       122             for pol in pollutant:
Modified var:.. pol = 'SO2'
22:35:14.859923 line       123                 temporal_data[pol][month] += float(row[pol])
22:35:14.859923 line       122             for pol in pollutant:
22:35:14.859923 line       120         for row in self.prsa_data[zone]:
Modified var:.. row = {'No': '2505', 'year': '2013', 'month': '6', 'da...'wd': 'S', 'WSPM': '0.6', 'station': 'Changping'}
22:35:14.859923 line       121             month = (int(row['year']) - 2013) * 12 + int(row['month']) - 3
22:35:14.859923 line       122             for pol in pollutant:
Modified var:.. pol = 'PM2.5'
22:35:14.859923 line       123                 temporal_data[pol][month] += float(row[pol])
Modified var:.. temporal_data = {'PM2.5': [73594.0, 42978.0, 61745.0, 24624.0, 0... 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
...
```

