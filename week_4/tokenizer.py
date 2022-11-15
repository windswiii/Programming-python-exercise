import jieba
import re
import time

NOD = 18000
FilePath = 'Data/Tokenizer/final_none_duplicate.txt'

class Tokenizer:
    def __init__(self, chars, coding, PAD = 0):
        '''
        输入文本列表,按coding方式完成词典构建
        '''
        self.chars = chars
        self.coding = coding
        self.PAD = PAD
        
        length = len(chars)
        c = 0
        word_list = []
        
        for each in chars:
            
            if c % 1000 == 0:
                print('\rCreating dictionary:%4.2f' % (c * 100 / length) + '%', end = '')
            c += 1
            
            if self.coding == 'c': 
                word_list += list(each)
            elif self.coding == 'w': 
                word_list += jieba.cut(each)
                
        print('\rGreating dictionary:100.00%')
        word_list = list(set(word_list))
        self.code_dict = {word_list[i]:i + PAD + 1 for i in range(len(word_list))}
        self.word_dict = {i + PAD + 1:word_list[i] for i in range(len(word_list))}
        self.word_dict[PAD] = '[PAD]'

    def tokenize(self, sentence):
        '''
        输入单句文本,返回其对应的字符列表
        '''
        if self.coding == 'c':
            return list(sentence)
        elif self.coding == 'w':
            return list(jieba.cut(sentence))
        
    def encode(self, list_of_chars):
        '''
        输入一个字符列表,返回转换后的数字列表
        '''
        tokens = [self.code_dict[w] for w in list_of_chars]
        return tokens
    
    def trim(self, tokens, seq_len):
        '''
        整理数字列表的长度
        '''
        if len(tokens) < seq_len:
            tokens += [self.PAD] * (seq_len - len(tokens))
        else:
            tokens = tokens[:seq_len]
        return tokens

    def decode(self, tokens):
        '''
        输入一个数字列表,返回其对应的句子
        '''
        chars = ''
        word_list = [self.word_dict[n] for n in tokens]
        for w in word_list:
            chars += w
        return chars

    def encode_all(self, seq_len):
        '''
        返回所有文本的长度为seq_len的tokens
        '''
        list_of_tokens = []
        length = len(self.chars)
        c = 0
        
        for each in self.chars:
            
            if c % 1000 == 0:
                print('\rEncoding texts:%4.2f' % (c * 100 / length) + '%', end = '')
            c += 1
            
            tokens = self.trim(self.encode(self.tokenize(each)), seq_len)
            list_of_tokens.append(tokens)
            
        print('\rEncoding texts:100.00%')
        return list_of_tokens

def wash(path):
    '''
    输入对应路径,以列表形式返回整理好的文本
    '''
    c = 1
    start = time.time()
    
    text_list = []
    print('Reading ' + path)
    weibo_list = [l.strip('\n') for l in open(path, 'r', encoding = "utf-8")]
    
    for line in weibo_list[1:NOD + 1]:
        
        if c % 1000 == 0: 
            print('\rWashing the Weibo data:%4.2f' % float(100 * c / NOD), '%', sep = '', end = '')
        c += 1
                        
        #读取正文内容
        text = re.sub('\t[0-9]+\t[A-Za-z]+.+', '', line)    #去除时间等信息
        text = re.sub(r'(我在这里:|我在:)?http:\\/\\/t.cn\\/.*', "", text)  #去除网址
        text = re.sub('[\[][^\[\]]*[\]]', '', text) #去除方括号中的内容
        text = re.sub('#[^#]+#', '', text)     #去除话题/title
        text = re.sub('@[^\s]+', '', text)     #去除@信息
        text = re.sub('分享图片', '', text)     
        text = re.sub('\s', '', text)           #去除空白字符
        if len(text) != 0: text_list.append(text)
    
    print('\rWashing the Weibo data:100.00%')
    print('Cost time:', time.time() - start)
    return text_list

def seqlen_stat(weibo_list):
    '''
    计算文本的长度分布,以确定一个合适的seq_len
    '''
    c_count = [0] * 300
    w_count = [0] * 300
    length = len(weibo_list)
    c = 0
    
    for weibo in weibo_list:
        
        if c % 1000 == 0:
            print('\rCalculating the distribution of length:%4.2f' % (c * 100 / length) + '%', end = '')
        c += 1
        
        c_count[len(weibo)] += 1
        w_count[len(list(jieba.cut(weibo)))] += 1
        
    print('\rCalculating the distribution of length:100.00%')
        
    print('c:', c_count)
    print('w:', w_count)
    
    print('众数方法:')
    print('按字构建:', c_count.index(max(c_count)))
    print('按词构建:', w_count.index(max(w_count)))
    
    print('至少保证60%的信息完整:')
    c_sum = sum(c_count)
    w_sum = sum(w_count)
    c_total = 0
    w_total = 0
    for i in range(len(c_count)):
        c_total += c_count[i]
        if c_total >= c_sum * 0.6:
            print('按字构建:', i)
            break
    for i in range(len(w_count)):
        w_total += w_count[i]
        if w_total >= w_sum * 0.6:
            print('按词构建:', i)
            break
    

if __name__ == '__main__':
    weibo_l = wash(FilePath)
    # for i in range(len(weibo_l)):
    #     print(i, weibo_l[i])
    # seqlen_stat(weibo_l)
    tokenizer_1 = Tokenizer(weibo_l, 'w')
    all_tokens = tokenizer_1.encode_all(15)
    for tokens in all_tokens:
        print(tokens, ':\n', tokenizer_1.decode(tokens))