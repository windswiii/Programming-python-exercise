# Emotion_analyze

### 库管理

```python
import jieba											#分词								
import os												#用于批量读取文件
import re												#文本处理
import matplotlib.pyplot as plt							#可视化
from math import sin, asin, cos, radians, fabs, sqrt	#计算
import numpy as np										
```

### 主函数

```python
def main():
    weibos = wash('emotion_lexicon', 'stopwords_list.txt', 'r_weibo.txt')  
    emo_count = count_emovector('emotion_lexicon')
    add_emovector(weibos, emo_count)
    temporal_pattern(weibos, 'week', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    temporal_pattern(weibos, 'day', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    spatial_pattern(weibos, 'beijing', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    return 0
```

## 具体函数实现

### 读取文件

```python
def read_txt(path):
    '''
    输入txt文件路径,返回列表
    '''
    print('Reading ' + path)
    lst = [l.strip('\n') for l in open(path, 'r', encoding = "utf-8")]
    return lst
```

### 数据清洗

每一条微博数据包含经纬度坐标、正文内容、发布时间等信息。

由于后续要进行时间模式和空间模式分析，首先要将经纬度坐标和时间提取出来。观察数据，时间信息具有统一的格式，可以直接通过字符串截取需要的时间信息。

```python
weibo_time = (line[-30:-11]).split(' ')
```

`weibo_time`是一个形如`['Fri', 'Oct', '22:19:51']`的列表。

原数据集中有一些格式错误及重复的微博，可借助时间信息的格式将其过滤掉。

```python
x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
if weibo_time[0] not in x: continue
```

提取空间信息时，由于经纬度坐标小数位数不一致，无法直接截取字符串，采用正则表达式匹配坐标文本。

```python
position = re.search(r'[0-9.]+[, ]+[0-9.]+', line).group()
```

最后处理正文，用正则表达式删去网址、数字、特殊符号等无意义的文本。

```python
URL_REGEX = re.compile(
    		'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?',
            re.IGNORECASE)
    text = re.sub(URL_REGEX, "", line[:-30])      #去除网址
    text = re.sub(r'[0-9.?,@\t]+', '', text)   #去除数字及部分符号
```

将情绪词典加入jieba库的自定义词典中，再导入停用词表，对正文进行分词。

```python
emofiles = os.listdir(emo_path)
for file in emofiles: 
    jieba.load_userdict(emo_path + '/' + file)
stopwords = read_txt(stop_path)
```

最后，将每条微博的上述信息（时间、空间、正文分词结果）整合为列表，最终函数如下：

```python
def wash(emo_path, stop_path, weibo_path):
    '''
    输入对应路径,以多维列表形式返回整理好的数据
    '''
    
    emofiles = os.listdir(emo_path)
    for file in emofiles: 
        jieba.load_userdict(emo_path + '/' + file)
    stopwords = read_txt(stop_path)
    
    weibo_l = []
    c = 1
    x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    for line in read_txt(weibo_path)[1:NOD + 1]:
        
        if c % 1000 == 0: 
            print('\rWashing the Weibo data:%4.2f' % float(100 * c / NOD), '%', sep = '', end = '')
        c += 1
        weibo = []
        
        #读取时间
        weibo.append((line[-30:-11]).split(' '))
        if weibo[0][0] not in x: continue       #过滤掉格式出错的文本
                
        #读取正文内容
        URL_REGEX = re.compile(
            '(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", line[:-30])      #去除网址
        text = re.sub(r'[0-9.?,@\t]+', '', text)   #去除数字及部分符号
        weibo.insert(0, [word for word in jieba.lcut(text) if word not in stopwords])
        
        #读取位置
        position = re.search(r'[0-9.]+[, ]+[0-9.]+', line).group()
        weibo.insert(1, [float(i) for i in position.split(', ')])

        weibo_l.append(weibo)
    
    print('\rWashing the Weibo data:100.00%')
    return weibo_l
```

### 情绪分析

采用向量法分析情绪，即统计每种情绪词在文本中的出现次数，再计算各情绪所占比例。

```python
def count_emovector(emo_path):
    '''
    输入情绪字典文件路径,计算情绪向量
    '''
    
    #读入字典
    files= os.listdir(emo_path)
    elist = []
    for file in files: 
        elist.append(read_txt(emo_path + '/' + file))
        
    #情绪分析
    def e_count(text):
        emo_vector = [0, 0, 0, 0, 0]    #[anger, disgust, fear, joy, sadness]
        for word in text:
            for i in range(5):
                if word in elist[i]:
                    emo_vector[i] += 1
                    break
        
        if emo_vector.count(emo_vector[0]) == 5: 
            return [0] * 5
        #向量标准化处理
        length = sum(emo_vector)
        for i in range(5):
            emo_vector[i] /= length
        
        return emo_vector
    
    return e_count
```

对每条微博数据，计算并记录其情绪向量。

```python
def add_emovector(weibos, e_count):
    '''
    输入微博数据集及情绪计算方法,为其添加情绪向量
    '''
    c = 0
    for weibo in weibos: 
        if c % 1000 == 0: 
            print('\rGenetating emotion vectors:%4.2f' % float(100 * c / len(weibos)), '%', sep = '', end = '')
        c += 1
        weibo.append(e_count(weibo[0]))
        
    print('\rGenetating emotion vectors:100.00%')
```

### 时间模式分析

主要实现了两种时间模式分析，即周模式和日模式。

情绪参数通过元组形式输入，可以一次性生成输入的所有情绪的图像。

首先建立情绪-索引值、情绪-颜色的字典，方便对输入的情绪参数进行处理。

```python
emo_index = {'anger': 0,'disgust': 1,'fear': 2,'joy': 3,'sadness': 4}
emo_color = {'anger': 'r','disgust': 'm','fear': 'k','joy': 'y','sadness': 'b'}
```

对于日模式，建立长度为24的列表`y`，记录每小时该情绪出现的次数，同时用一个列表`y_total`记录对应时段内参与计算的微博数据总数，以计算情绪比例。周模式同理。

```python
def temporal_pattern(weibos, mode, *emos):
    '''
    输入情绪类型和模式,绘制情绪强度-时间折线图
    '''
    if mode == 'week':
        x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for emo in emos:
            y = [0] * 7
            y_total = [1] * 7
            c = 0
            
            for weibo in weibos:
                
                if c % 1000 == 0 : 
                    print('\rCounting ', emo, ':%4.2f' % float(100 * c / len(weibos)), '%', sep = '', end = '')
                c += 1
                
                i = x.index(weibo[2][0])
                y[i] += weibo[3][emo_index[emo]]
                y_total[i] += 1
            print('\rCounting ', emo, ':100.00%', sep = '')
            
            for i in range(7):
                y[i] /= y_total[i]
                
            plt.plot(x, y, emo_color[emo])
            
        plt.xticks(x)
        plt.xlabel('Day')
        
    if mode == 'day':
        x = list(range(24))
        for emo in emos:
            c = 0
            y = [0] * 24
            y_total = [1] * 24
            
            for weibo in weibos:
                
                if c % 1000 == 0 : 
                    print('\rCounting ', emo, ':%4.2f' % float(100 * c / len(weibos)), '%', sep = '', end = '')
                c += 1
                
                i = int(weibo[2][3][0:2])
                y[i] += weibo[3][emo_index[emo]]
                y_total[i] += 1
            print('\rCounting ', emo, ':100.00%', sep = '')
            
            for i in range(24):
                y[i] /= y_total[i]
                
            plt.plot(x, y, emo_color[emo])
            
        xtick = [str(i).zfill(2) + ':30' for i in x]      
        plt.xticks(x, xtick, rotation = 60)   
        plt.xlabel('Hour')
        
    plt.legend(emos)
    plt.ylabel('Percentage')
    name = ''
    for emo in emos:
        name = name + '_' + emo
    plt.savefig('result/' + mode + name + '.png')
    plt.show()
```

### 空间模式

该数据集的微博数据大致来源于四个城市：北京、上海、广州、成都，查询其经纬度分别为：

```python
city_coord = {
    'beijing'  : [39.92, 116.46],
    'shanghai' : [31.22, 121.48],
    'guangzhou': [23.16, 113.23],
    'chengdu'  : [30.67, 104.06]
}
```

以此为城市中心坐标。

通过经纬度获取空间距离，可通过Haversine公式进行计算，其中 ：
$$
haversin(\theta) = sin^2(\theta/2) = (1-cos(\theta))/2
$$

$$
hav(\theta) = hav(\varphi_2-\varphi_1)+cos(\varphi_1)cos(\varphi_2)hav(\lambda_2-\lambda_1)
$$

其中θ为d/R，R为地球半径，d为两地间距离。

```python
def get_distance(coord1, coord2):
    '''
    输入两点经纬坐标,用haversine公式计算球面两点间的距离
    '''
    def hav(theta):
        s = sin(theta / 2)
        return s * s

    lat1 = radians(coord1[0])
    lng1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lng2 = radians(coord2[1])
    dlng = fabs(lng1 - lng2)
    dlat = fabs(lat1 - lat2)
    h = hav(dlat) + cos(lat1) * cos(lat2) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))
    return distance
```

对每一条微博，首先过滤掉经纬度差超过1（离城市中心过远）的，再生成一个包含距城市中心距离及各情绪值的列表，并根据距离进行排序。

```python
    for weibo in weibos:
        
        if (abs(weibo[1][0] - center[0]) < 1) and (abs(weibo[1][1] - center[1]) < 1):
            dist_emos = [get_distance(center, weibo[1]),]
            for emo in emos:
                dist_emos.append(weibo[3][emo_index[emo]])
            dist_emo_list.append(dist_emos)

    dist_emo_list = sorted(dist_emo_list, key = (lambda x:x[0]))
```

对排好序的列表进行遍历，将各情绪值累加起来，同时记录总的情绪向量数以计算比例。创建一个均匀分布的距离序列`x`，分别记录一定距离下的情绪比例，以生成距离-情绪关系。

```python
	count = 1
	length = len(dist_emo_list)
	emo = [0,] * len(emos)
    x = list(np.arange(0, 30, 0.2))
    ys = []
    
    for i in x:
        while dist_emo_list[count][0] < i:
            
            for j in range(len(emos)):
                emo[j] += dist_emo_list[count][j + 1]
            count += 1
            if count >= length: break
            
        ys.append([e / count for e in emo])
```

最终函数如下：

```python
def spatial_pattern(weibos, city, *emos):
    '''
    输入情绪类型及城市,绘制对应城市的情绪强度-距离折线图
    '''    
    center = city_coord[city]
    dist_emo_list = []
    c = 0
    
    for weibo in weibos:
        
        if c % 1000 == 0 : 
            print('\rCalculating the distance:%4.2f' % float(100 * c / len(weibos)), '%', sep = '', end = '')
        c += 1
        
        if (abs(weibo[1][0] - center[0]) < 1) and (abs(weibo[1][1] - center[1]) < 1):
            dist_emos = [get_distance(center, weibo[1]),]
            for emo in emos:
                dist_emos.append(weibo[3][emo_index[emo]])
            dist_emo_list.append(dist_emos)
            
    print('\rCalculating the distance:100.00%')
    dist_emo_list = sorted(dist_emo_list, key = (lambda x:x[0]))    # 按与中心的距离排序
    
    count = 1
    length = len(dist_emo_list)
    emo = [0,] * len(emos)
    x = list(np.arange(0, 30, 0.2))
    ys = []
    
    c = 0
    for i in x:
        while dist_emo_list[count][0] < i:
            
            if c % 1000 == 0 : 
                print('\rCounting emotions:%4.2f' % float(100 * c / length), '%', sep = '', end = '')
            c += 1
            
            for j in range(len(emos)):
                emo[j] += dist_emo_list[count][j + 1]
            count += 1
            if count >= length: break
            
        ys.append([e / count for e in emo])
    print('\rCounting emotions:100.00%')
        
    for i in range(len(emos)):
        y = [x[i] for x in ys]
        plt.plot(x, y, emo_color[emos[i]])
    
    plt.xlabel('Distance from the city center (KM)')
    plt.ylabel('Percentage')
    plt.legend(emos)
    name = ''
    for emo in emos:
        name = name + '_' + emo
    plt.savefig('result/' + city + name + '.png')
    plt.show()
```

## 思考

- 采用字典方法进行情绪理解，思路简单易于实现，但是需要极大的样本量以生成情绪字典并提高准确性，另外，字词与情绪并不一定是一一对应的关系，精确判别情绪更需要对句子整体的语义判别。可以基于已有的情绪字典，从分好类的情绪文本中提取特征词，进一步扩充情绪词典。
- 情绪与消费欲望、工作积极性都有一定相关性。借助情绪的时空模式，管理者可以更好地安排员工的工作强度，或在适当时间予以激励；情绪不同时，消费者对于不同商品的需求也有所不同，商家可以据此在适当的时间推送广告等，刺激消费者的购买欲望。

