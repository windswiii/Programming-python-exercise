from multiprocessing import Process, Pipe
import jieba
import os
import time
import logging

# 关闭jieba log输出
jieba.setLogLevel(logging.INFO)

PCS = 3        #the number of process
DATA_PATH = 'Data/multidocs'
STOP_PATH = 'Data/TextProcess/stopwords_list.txt'

def freq_statistic(data, stopwords):
    seg_list = list(word for word in jieba.lcut(data) if word not in stopwords)
    freq_dict = {}
    for word in seg_list:
        if word in freq_dict:
            freq_dict[word] += 1
        else:
            freq_dict[word] = 1
    return freq_dict 

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


def dispatch(to_map, data_path):
    path_list = os.listdir(data_path)
    for path in path_list[:10000]:
        to_map.send(data_path + '/' + path)
    

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
            with open('result/mapreduce/stat_result_0.txt', 'w', encoding='utf-8') as outfile:
                for key in freq_stat.keys():
                    print(key, ':', freq_stat[key], file=outfile)    
            break
        


if __name__ == '__main__':
    start = time.time()
    
    with open(STOP_PATH, 'r', encoding='utf-8') as infile:
        stopwords_0 = list(infile.readlines())
        stopwords = [word.strip('\n') for word in stopwords_0]
        stopwords.append('\n')
    
    # Create processes
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
    
    # Close the pipe after the child process finished 
    dispatcher.join()
    send_dptm.close()
    for amap in maps: amap.join()
    send_mtrd.close()
    reducer.join()
    print('\nFinished!')
    
    # Record running information
    T = time.time() - start
    with open('result/mapreduce/log.txt', 'a', encoding='utf-8') as outfile:
        print('The number of process:%2d Runtime:%4.2f'%(PCS, T), file=outfile)