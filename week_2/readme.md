# Word Frequency Statistics

完成以下数据分析任务： 

> 1. 使用danmuku.csv，读入文档并分词（使用jieba）。 
> 2. 过滤停用词（使用stopwords_list.txt）并统计词频，输出特定数目的高频词和低频词进行观察。
> 3. 根据词频进行特征词筛选，保留高频词，删除低频词，并得到特征词组成的特征集。
> 4. 利用特征集为每一条弹幕生成向量表示，可以是0，1表示（one-hot，即该特征词在弹幕中是否出现）也可以是出现次数的表示（该特征词在弹幕中出现了多少次）。注意，可能出现一些过短的弹幕，建议直接过滤掉。 
> 5. 利用该向量表示，随机找几条弹幕，计算不同弹幕间的语义相似度，采用欧几里得距离，并观察距离小的样本对和距离大的样本对是否在语义上确实存在明显的差别。请思考，这种方法有无可能帮助我们找到最有代表性的弹幕？
> 6. 对高频词（如top 50之类）进行可视化呈现（WordCloud包）

### 库管理

```python
import jieba					#分词
import csv						#读入文件
import time						#计时
import random					#随机抽取
from wordcloud import WordCloud	#生成词云图
```

### 主函数

```python
def main():
    danmakus = in_danmaku("works\\danmuku.csv")         #读取弹幕文件
    stopwords = in_stopword("works\\stopwords_list.txt")#读取停用词表
    seg_list = segmentation(danmakus, stopwords)        #分词
    freq_dict = frequency_statistics(seg_list)          #词频统计
    create_wordcloud(freq_dict)                         #生成词云图
    feature_set = create_feature_set(freq_dict)         #生成特征集
    vector_set = to_vector(feature_set, seg_list)       #生成向量表示
    test_similarity(danmakus, vector_set, 10)           #随机弹幕距离测试
    search_nf(danmakus, vector_set, 10)                 #最近最远弹幕测试
```

## 具体函数实现

### 读入文件

从danmuku.csv中读取弹幕，将第一列的弹幕内容并存入`danmaku_list`列表中，返回时用`Nod`变量控制数据规模，方便进行测试。

```python
def in_danmaku(path):
    '''
    读入弹幕文件,返回弹幕内容列表
    '''
    danmaku_file =  open(path, 'r', encoding = 'utf-8')
    print(">正在读入弹幕文件 --- ", end = '')
    danmaku_table = csv.reader(danmaku_file)
    danmaku_list = [line[0] for line in danmaku_table]
    danmaku_file.close()
    print("完成")
    return danmaku_list[1:Nod + 1]
```

从stopwords_list.txt中读取停用词，整理成`stopword_list`列表

```python
def in_stopword(path):
    '''
    读入停用词表,返回停用词列表
    '''
    stopword_file =  open(path, 'r', encoding = 'utf-8')
    print(">正在读入停用词表 --- ", end = '')
    stopword_table = stopword_file.readlines()
    stopword_list = [line.strip('\n') for line in stopword_table]
    stopword_file.close()
    print("完成")
    return stopword_list
```

### 分词

使用jieba库对每条弹幕进行分词，过滤掉停用词后，将结果存入二维列表`seg_list`中，列表中的每个元素即为对应弹幕的分词结果。

```python
def segmentation(docs, stopwords):
    '''
    输入文档和停用词表,进行分词
    '''
    seg_list = []
    i = 1
    start = time.time()
    
    print(">正在进行分词")
    for doc in docs:
        seg_list.append(list(word for word in jieba.lcut(doc) if word not in stopwords))
        print('\r', i, '/', Nod, sep = '', end = ''); i += 1
    print('\nCost', time.time() - start, 'seconds')
    
    return seg_list
```

### 词频统计

利用分词结果，统计词频，得到以词：频率为键值对的字典`freq_dict`，对该字典按频率降序排序，返回排好序的频数字典`freq_rdict`，方便后续操作。

```python
def frequency_statistics(seg_list):
    '''
    统计词频,返回按频数降序排列的字典(保留前500条)
    '''
    freq_dict = {}
    
    print(">正在统计词频 ---", end = ' ')
    for line in seg_list:
        for word in line:
            if word in freq_dict:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1
    print("完成")
             
    print(">正在对字典排序 ---", end = ' ')
    freq_rdict = {k: v for k, v in sorted(freq_dict.items(), key = lambda item: item[1], reverse = True)}
    print("完成")      
    return freq_rdict
```

### 绘制词云图

用wordcloud库中的`.generate_from_frequencies()`方法，根据频数字典的数据生成词云图。

```python
def create_wordcloud(freqs):
    '''
    输入频数字典,生成词云图
    '''
    start = time.time()
    print(">正在生成词云图 --- ", end = '')
    cloud0 = WordCloud(
        background_color = 'rgba(245,213,254,0)',
        mode = 'RGBA',
        colormap = 'Set2',
        font_path = 'C:/Windows/Font/simhei.ttf',
        max_words = 300,
        max_font_size = 400,
        min_font_size = 2,
        width = 1500,
        height = 1500,
    )
    cloud = cloud0.generate_from_frequencies(freqs)
    cloud.to_file('danmuCloud_1.png')
    print("完成")
    print('Cost', time.time() - start, 'seconds')
```

生成的词云图如下：

<img src="D:\HUAWEI\Documents\all_code\Python\danmuCloud.png" alt="danmuCloud" style="zoom: 20%;" />

### 创建特征集

选择出现频数最高的词生成特征集。由于频数字典已排好序，直接截取前面部分的键就能得到特征集。用变量`Fss`来控制特征集的大小。

```python
def create_feature_set(dic):
    '''
    输入频数字典,返回一个由频数最高的词组成的特征集
    '''
    
    feature_set = []
    i = 0
    for key in dic.keys():
        feature_set.append(key)
        i += 1
        if i > Fss : break
    feature_set = tuple(feature_set)
    f = open('Result_1.txt', 'w')
    print("提取到的特征集为:\n", feature_set, file = f)
    f.close()
    return feature_set
```

生成的特征集与词云图一致：

```python
 ('哈哈哈哈', '武汉', '吃', '加油', '藕', '蒜', '好吃', '真的', '萝卜', '热情', '想', '粉', '大哥', '啊啊啊', '独头', '喜欢', '牛杂', '考古', '真', '笑', '死', '户部', '爱', '感觉', '买', '街', '巷', '树梢', '大蒜', '可爱', '饿', '洛阳', '湖北', '猝不及防', '疫情', '大佬', '恰饭', '好好', '卤', '沐', '地方', '丑', '恰', '氛围', '米粉', '便宜', '辣', '希望', '长子', '四川', '牛肉', '广告', '走', '2020', '闻见', '哭', '视频', '痔疮', '江西', '邵阳', '好像', '嗦', '里', '这是', '岁', '味道', '馋', '牙膏', '超', '闻到', '恍恍惚惚', '老乡', '旁边', '弹幕', '棒', '常德', '吼吼', '闻', '香', '中国', 'h', '母上', '泪目', '气', '云南白药', '广西', '热', '2021', '跑', '去过', '红红火火')
```

### 生成向量表示

采用one-hot方法会遗漏部分信息，而根据特征词出现次数生成向量又会导致重复信息权重过高。

例如在后续的距离计算中，在“蒜蒜蒜蒜蒜蒜蒜蒜蒜蒜”这条弹幕中，特征词“蒜”出现了10次，导致其与正常弹幕的距离非常远。

```python
Test1
武汉藕霸
最近的弹幕为:武汉的藕好吃呀！
距离: 1.0
最远的弹幕为:蒜蒜蒜蒜蒜蒜蒜蒜蒜蒜
距离: 10.099504938362077

Test2
卤味真的超好吃
最近的弹幕为:藕真的超好吃
距离: 1.0
最远的弹幕为:蒜蒜蒜蒜蒜蒜蒜蒜蒜蒜
距离: 10.099504938362077
```

因此有必要对重复的特征词进行一定限制，多次测试后，发现将单个分量的值限制为0,1,2得到的效果最佳。当某一特征值在一个弹幕中出现的次数超过2时，将其设为2。

```
val = min(2, docs[i].count(feature_set[j]))
```

另外，一些过短的或者基本不包含特征词的弹幕对于后续的分析几乎无意义，因此将它们过滤掉。用`Filt`变量来控制筛选强度。`Filt = 1`即表示只保留包含2个以上特征词的弹幕。

最后，将每个向量列表存入二维列表`vector_set`中，由于过程中筛选掉了一部分数据，每个向量和弹幕文档不再一一对应，所以在每个向量的末尾加上其对应弹幕在弹幕列表`danmakus`中的索引值。

```python
def to_vector(feature_set, docs):
    '''
    生成弹幕的向量表示
    '''
    vector_set = []  
    print(">正在生成向量表示 --- ", end = '')
    for i in range(len(docs)):
        vector_doc = [0] * (Fss + 1)
        vector_doc[-1] = i                              #记录弹幕序号
        flag = 0
        #print('\r', i, '/', Nod, sep = '', end = '')
        for j in range(Fss):
            val = min(2, docs[i].count(feature_set[j]))
            vector_doc[j] = val
            flag += val 
        if flag > Filt:                                       #过滤掉无意义的向量
            vector_set.append(vector_doc)
    print("完成", end = '')
    
    return vector_set
```

### 语义相似度分析

计算欧几里得距离，比较弹幕之间的语义相似程度。

```python
def dist_calcuate(a, b):
    '''
    计算两条弹幕之间的相似度（欧几里得距离）
    '''
    distance = 0
    for i in range(Fss):
        distance += (a[i] - b[i]) ** 2
    return distance ** 0.5
```

随机选择n对弹幕，计算每一对之间的距离，并分析二者的语义相似程度。

```python
def test_similarity(docs, vectors, n):
    '''
    随机选择n对弹幕,计算其相似度
    '''  
    f = open('Result_1.txt', 'a')
    print("\n--随机选择n对弹幕,计算其相似度--", file = f)
    for i in range(n):
        print("\nTest", i + 1, sep = '', file = f)
        a = random.choice(vectors)
        b = random.choice(vectors)
        print(docs[a[Fss]], '\n', docs[b[Fss]], file = f)
        print("距离为:", dist_calcuate(a, b), file = f)
    f.close()
```

观察下列部分计算结果，可以发现距离与语义相似度之间存在一定关系。距离较小的一对弹幕更可能包含相同的特征词，而距离较远的弹幕几乎毫无联系。

```
Test1
这里旁边有家灌汤包，特别好吃 
 锅贴诶  我最喜欢吃的
距离为: 2.0

Test2
我买，我买，还不行吗 
 吃蛋糕都就蒜~
距离为: 2.449489742783178

Test3
户部巷别去啊啊啊  粮道街粮道街 
 哈哈哈哈哈哈哈哈
距离为: 3.1622776601683795

Test4
吉庆街没人吃的 
 今天还吃了藕夹
距离为: 1.4142135623730951
```

对于给定的一条弹幕，从所有弹幕中检索距其最近的和最远的弹幕，并分析这些弹幕之间的语义相似程度。

```python
def search_nf(docs, vectors, n):
    '''
    随机选择n条弹幕,并匹配距其最近的和最远的弹幕
    '''
    f = open('Result_1.txt', 'a')
    print("\n--随机选择n条弹幕,并匹配距其最近的和最远的弹幕--", file = f)
    for i in range(n):
        near = [0, float('inf')]
        far = [0, 0]
        print("\nTest", i + 1, sep = '', file = f)
        vec_a = random.choice(vectors)
        for vec_b in vectors:
            if vec_b[:-1] == vec_a[:-1]: continue
            dist = dist_calcuate(vec_a, vec_b)
            if dist > far[1]:
                far[1] = dist
                far[0] = vec_b[-1]
            if dist < near[1]:
                near[1] = dist
                near[0] = vec_b[-1]
        print(docs[vec_a[-1]], file = f)
        print("最近的弹幕为:", docs[near[0]], '\n', "距离: ", near[1], sep = '', file = f)
        print("最远的弹幕为:", docs[far[0]], '\n', "距离: ", far[1], sep = '', file = f)
    f.close()
```

观察下列部分计算结果，距离最近的弹幕有较多相似的特征词，语义都是相近的；而最远的弹幕几乎和该弹幕完全没有语义关联。

```
Test5
我们湖北的藕是真的好吃
最近的弹幕为:藕真的好吃
距离: 1.0
最远的弹幕为:一想到现在的疫情就想哭    明明是这么热情可爱的武汉人   一定要加油啊  武汉加油  中国加油！   
距离: 4.242640687119285

Test6
2020年9月盗月社再次光顾长堤街后，前来考古，武汉加油
最近的弹幕为:2020  1.27武汉加油！
距离: 1.0
最远的弹幕为:萝卜牛杂的妙处就是萝卜啊，牛杂固然好吃，但牛杂本来就好吃，萝卜换了其他做法可远出不来那个味
距离: 4.0

Test7
为邵阳米粉打call啊啊啊啊
最近的弹幕为:啊啊啊邵阳米粉超好吃的
距离: 1.4142135623730951
最远的弹幕为:武汉的卤藕超好吃，而且到了武汉才知道藕也可以卤
距离: 4.123105625617661

Test8
她真的好喜欢吃蒜OMG
最近的弹幕为:重庆也有这个  我不喜欢吃蒜
距离: 1.0
最远的弹幕为:武汉的卤藕超好吃，而且到了武汉才知道藕也可以卤
距离: 4.242640687119285
```

结合上面两个测试可以看出，弹幕向量之间的欧几里得距离和语义相似度存在明显相关性。

然而，这种方法只能用于判断两句话是否说的是同一个话题，而不能区分具体观点的差别。例如Test8中，“喜欢”“吃蒜”两个特征词就足以让两者距离非常相近，而考虑特征词之外的部分，这两条弹幕的表意完全不同。

更进一步的分析还应该考虑否定词、词的排列顺序等情况。
