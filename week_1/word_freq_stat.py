import jieba
import csv
import time
import random
from wordcloud import WordCloud

Fss = 90        #特征集大小
Nod = 10000     #测试数据量(0-2798999)
Filt = 1        #筛选力度:接受的最低特征词数量

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

def dist_calcuate(a, b):
    '''
    计算两条弹幕之间的相似度（欧几里得距离）
    '''
    distance = 0
    for i in range(Fss):
        distance += (a[i] - b[i]) ** 2
    return distance ** 0.5

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

def create_wordcloud(freqs):
    '''
    输入频数字典,生成词云图
    '''
    start = time.time()
    print(">正在生成词云图 --- ", end = '')
    cloud0 = WordCloud(
        background_color = 'rgba(0,213,254,1)',
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
    
def main():
    danmakus = in_danmaku("danmuku.csv")         #读取弹幕文件
    stopwords = in_stopword("stopwords_list.txt")#读取停用词表
    seg_list = segmentation(danmakus, stopwords)        #分词
    freq_dict = frequency_statistics(seg_list)          #词频统计
    create_wordcloud(freq_dict)                         #生成词云图
    feature_set = create_feature_set(freq_dict)         #生成特征集
    vector_set = to_vector(feature_set, seg_list)       #生成向量表示
    test_similarity(danmakus, vector_set, 10)           #随机弹幕距离测试
    search_nf(danmakus, vector_set, 10)                 #最近最远弹幕测试

main()