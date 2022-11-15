# MapReduce Documents Processing

> MapReduce是利用多进程并行处理文件数据的典型场景。作为一种编程模型，其甚至被称为Google的”三驾马车“之一(尽管目前由于内存计算等的普及已经被逐渐淘汰)。在编程模型中，Map进行任务处理，Reduce进行结果归约。本周作业要求利用Python多进程实现MapReduce模型下的文档库[搜狐新闻数据](https://www.sogou.com/labs/resource/cs.php)，注意仅使用页面内容，即新闻正文）词频统计功能。具体地：
>
> 1. Map进程读取文档并进行词频统计，返回该文本的词频统计结果。
>
> 2. Reduce进程收集所有Map进程提供的文档词频统计，更新总的文档库词频，并在所有map完成后保存总的词频到文件。
>
> 3. 主进程可提前读入所有的文档的路径列表，供多个Map进程竞争获取文档路径；或由主进程根据Map进程的数目进行分发；或者单独实现一个分发进程，与多个Map进程通信。
>
> 4. 记录程序运行时间，比较不同Map进程数量对运行时间的影响，可以做出运行时间-进程数目的曲线并进行简要分析。进程数量并非越多越好。

## 文件预处理

给出的SougoCS下载地址似乎不可用，使用第一次作业的弹幕数据集进行处理。

将原始文档裁剪切分成小文件，便于后续处理。`NUM_DOC`为文件个数，`NUM_LIN`为单个文件中的数据行数。

```python
import csv

NUM_LIN = 30
NUM_DOC = 10000

infile = open('Data/TextProcess/danmuku.csv', 'r', encoding='utf-8')
danmu = list(csv.reader(infile))
now = 1
for i in range(NUM_DOC):
    print('\rWriting %d/%d ...'%(i, NUM_DOC), end='')
    outfile = open('Data/multidocs/doc_%d.txt'%i, 'w', encoding='utf-8')
    for j in range(NUM_LIN):
        print(danmu[now + j][0], file=outfile)
    now += NUM_LIN
```

## 整体结构

<img src="images\image-20221112151651561.png" alt="image-20221112151651561" style="zoom:50%;" />



分发进程向`Map`进程派发文件路径，`Map`进程处理完后将统计结果发送至`Reduce`进程，均通过单向管道连接。

### 分发进程

读入文件夹路径，获取文件路径列表，发送至`map`进程。`to_map`为连接`map`进程的管道发送端。

```python
def dispatch(to_map, data_path):
    path_list = os.listdir(data_path)
    for path in path_list:
        to_map.send(data_path + '/' + path)
```

### MAP进程

从分发进程获取文件路径，读取文件，分词并统计词频。

#### 分词统计功能实现

```python
def freq_statistic(data, stopwords):
    seg_list = list(word for word in jieba.lcut(data) if word not in stopwords)
    freq_dict = {}
    for word in seg_list:
        if word in freq_dict:
            freq_dict[word] += 1
        else:
            freq_dict[word] = 1
    return freq_dict 
```

#### 通信功能实现

`to_dp`为连接分发进程的接收端，`to_rd`为连接`Reduce`进程的接收端。

```python
def map_stat(to_dp, to_rd, stopwords):
    while 1:
        try:
            path = to_dp.recv()
            with open(path, 'r', encoding='utf-8') as infile:
                text = infile.read()
            freq_dict = freq_statistic(text, stopwords)
            to_rd.send(freq_dict)
        except EOFError:
            to_dp.close()
            break
```

### Reduce进程

持续接收来自各`Map`进程的词频统计结果（字典形式），更新总词频字典。所有`Map`进程的结果整理完成后，将最终总词频保存到文件。

```python
def reduce_freq_stat(to_map):
    freq_stat = {}
    count = 1
    while 1:
        try:
            s_freq = to_map.recv()
            print('\rProcessed %d ...'%count, end='')
            count += 1
            for key in s_freq.keys():
                if key in freq_stat:
                    freq_stat[key] += s_freq[key]
                else:
                    freq_stat[key] = s_freq[key]
        except EOFError:
            to_map.close()
            with open('result/mapreduce/stat_result.txt', 'w', encoding='utf-8') as outfile:
                for key in freq_stat.keys():
                    print(key, ':', freq_stat[key], file=outfile)    
            break
```

### 主函数实现

记录开始时间以计算程序运行时间；读取停用词表。

```python
    start = time.time()
    
    with open(STOP_PATH, 'r', encoding='utf-8') as infile:
        stopwords_0 = list(infile.readlines())
        stopwords = [word.strip('\n') for word in stopwords_0]
        stopwords.append('\n')
```

创建管道以及各个子进程。`PCS`为`Map`子进程的数量。所有`Map`子进程共用同一管道进行通信。

```
    maps = []
    recv_dptm, send_dptm = Pipe(False)
    recv_mtrd, send_mtrd = Pipe(False)
    for i in range(PCS):
        maps.append(Process(target=map_stat, 
                            args=(recv_dptm, send_mtrd, stopwords)))
    dispatcher = Process(target=dispatch, args=(send_dptm, DATA_PATH))
    dispatcher.start()
    reducer = Process(target=reduce_freq_stat, args=(recv_mtrd,))
    reducer.start()    
    for amap in maps: amap.start()
```

分发进程结束后，关闭分发管道发送端；`Map`进程结束后，关闭至`Reduce`的整合管道发送端。

```python
    dispatcher.join()
    send_dptm.close()
    for amap in maps: amap.join()
    send_mtrd.close()
```

所有进程结束后，统计并记录程序运行信息。

```python
    T = time.time() - start
    with open('result/mapreduce/log.txt', 'a', encoding='utf-8') as outfile:
        print('The number of process:%2d Runtime:%4.2f'%(PCS, T), file=outfile)
```

## 统计结果

### 词频统计部分结果

```python
...
睡 : 78
刚刚 : 268
辽 : 319
两 : 97
囍 : 54
发现 : 416
喜欢 : 3850
片头 : 3
武汉 : 20749
哇塞 : 199

还好 : 177
吃了饭 : 1
年轻 : 115
老板 : 886
一课 : 1
外卖 : 8
111 : 2
热热 : 2
三年 : 72
三个 : 164
每次 : 334
他俩 : 261
视频 : 191
饿 : 2889
四大 : 86
火炉 : 188
...
```

完整结果保存在文档`stat_result.txt`中。

### 子进程数-运行时间

```python
The number of process: 1 Runtime:121.93
The number of process: 2 Runtime:63.55
The number of process: 3 Runtime:62.18
The number of process: 4 Runtime:65.12
The number of process: 5 Runtime:79.29
The number of process: 6 Runtime:77.63
The number of process: 7 Runtime:76.83
The number of process: 8 Runtime:79.19
The number of process: 9 Runtime:81.70
The number of process:10 Runtime:80.72
```

绘制折线图：

<img src="images\image-20221112160453589.png" alt="image-20221112160453589" style="zoom:60%;" />

查询可知本设备CPU（intel core i5）核数为4。

观察图表，`Map`进程个数为2-4时，程序运行时间比起单线程明显缩短。`Map`进程数超过4以后运行速度又略微下降，因为此时单核要进行多个任务间的切换，产生额外开销。