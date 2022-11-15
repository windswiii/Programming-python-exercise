import jieba
import time
import os
import re
import matplotlib.pyplot as plt
from math import sin, asin, cos, radians, fabs, sqrt
import numpy as np

EARTH_RADIUS = 6371     # 地球平均半径大约6371km

emo_index = {
    'anger'  : 0,
    'disgust': 1,
    'fear'   : 2,
    'joy'    : 3,
    'sadness': 4
}

emo_color = {
    'anger'  : 'r',
    'disgust': 'm',
    'fear'   : 'k',
    'joy'    : 'y',
    'sadness': 'b'
}

city_coord = {
    'beijing'  : [39.92, 116.46],
    'shanghai' : [31.22, 121.48],
    'guangzhou': [23.16, 113.23],
    'chengdu'  : [30.67, 104.06]
}

def read_txt(path):
    '''
    输入txt文件路径,返回列表
    '''
    print('Reading ' + path)
    lst = [l.strip('\n') for l in open(path, 'r', encoding = "utf-8")]
    return lst

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
    start = time.time()
    x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    for line in read_txt(weibo_path)[1:]:
        
        if c % 1000 == 0: 
            print('\rWashing the Weibo data:%4.2f' % float(100 * c / 2352235), '%', sep = '', end = '')
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
    print('Cost time:', time.time() - start)
    return weibo_l
            
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
    plt.savefig(mode + name + '.png')
    plt.close()

def get_distance(coord1, coord2):
    # 用haversine公式计算球面两点间的距离
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

def spatial_pattern(weibos, city, *emos):
    
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
    x = list(np.arange(0, 30, 0.05))
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
    plt.savefig(city + name + '.png')
    plt.close()

def main():
    weibos = wash('emotion_lexicon', 'stopwords_list.txt', 'weibo.txt')  
    emo_count = count_emovector('emotion_lexicon')
    add_emovector(weibos, emo_count)
    temporal_pattern(weibos, 'week', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    temporal_pattern(weibos, 'day', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    spatial_pattern(weibos, 'beijing', 'anger', 'disgust', 'fear', 'joy', 'sadness')
    return 0

main()