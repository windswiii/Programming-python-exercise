# Tokenizer

###### 薛扬帆 20377300

### 数据清洗

从文件中读入微博文本，整理成列表。由于文件中的每一条微博包括经纬度、时间、网页等无用信息，为了不影响后续Tokenizer类的实现，应先整理好文本格式。利用正则表达式将无用信息删去：

```python
        text = re.sub('\t[0-9]+\t[A-Za-z]+.+', '', line)    #去除时间等信息
        text = re.sub(r'(我在这里:|我在:)?http:\\/\\/t.cn\\/.*', "", text)  #去除网址
        text = re.sub('[\[][^\[\]]*[\]]', '', text) #去除方括号中的内容（地址/表情）
        text = re.sub('#[^#]+#', '', text)     		#去除话题/title
        text = re.sub('@[^\s]+', '', text)     		#去除@信息
        text = re.sub('分享图片', '', text)     
        text = re.sub('\s', '', text)           	#去除空白字符
```

处理完成后，过滤掉空字符串，最终函数为：

```python
def wash(path):
    '''
    输入对应路径,以列表形式返回整理好的文本
    '''
    text_list = []
    weibo_list = [l.strip('\n') for l in open(path, 'r', encoding = "utf-8")]
    
    for line in weibo_list[1:NOD + 1]:          
        text = re.sub('\t[0-9]+\t[A-Za-z]+.+', '', line)
        text = re.sub(r'(我在这里:|我在:)?http:\\/\\/t.cn\\/.*', "", text) 
        text = re.sub('[\[][^\[\]]*[\]]', '', text) 
        text = re.sub('#[^#]+#', '', text) 
        text = re.sub('@[^\s]+', '', text) 
        text = re.sub('分享图片', '', text)     
        text = re.sub('\s', '', text)
        if len(text) != 0: text_list.append(text)
    
    return text_list
```

### 文本长度分布

选择合适的`seq_len`可能有不同的标准，从效率最高的角度（即需要添补或删减的文本最少），可选择文本长度的众数。

```python
def seqlen_stat(weibo_list):
    '''
    计算文本的长度分布,以确定一个合适的seq_len
    '''
    c_count = [0] * 300
    w_count = [0] * 300

    for weibo in weibo_list:
        c_count[len(weibo)] += 1
        w_count[len(list(jieba.cut(weibo)))] += 1
        
    print('c:', c_count)
    print('w:', w_count)
    print('按字构建:', c_count.index(max(c_count)))
    print('按词构建:', w_count.index(max(w_count)))
```

统计得到的文本长度分布如下：

```python
按字统计长度: [0, 5466, 24041, 33705, 46998, 55353, 56038, 57663, 59806, 58199, 58144, 54784, 54511, 51242, 49992, 46393, 44479, 40841, 39096, 35945, 34632, 32333, 32014, 29043, 27645, 26202, 24705, 23874, 23312, 20832, 20912, 18734, 18520, 17033, 16091, 14869, 14564, 13712, 13098, 12376, 14646, 12972, 10777, 10369, 10293, 12792, 9131, 8489, 10356, 8256, 7998, 7691, 7225, 7562, 6720, 7886, 6011, 5840, 5871, 5419, 5242, 5069, 5218, 4876, 4784, 4467, 4743, 4556, 4579, 3908, 4131, 4770, 3753, 3607, 3544, 3704, 3547, 3383, 3334, 3304, 3087, 2976, 3059, 2841, 2841, 3099, 2745, 2781, 2833, 2644, 2595, 2606, 2410, 2416, 2541, 2374, 2469, 2500, 2308, 2218, 2252, 2220, 2265, 2170, 2150, 2125, 2151, 2177, 2347, 2354, 2257, 2219, 2235, 2289, 2359, 2436, 2536, 2580, 2686, 2856, 3173, 3495, 6302, 2596, 2361, 2065, 1863, 1960, 1855, 2199, 3624, 1120, 889, 732, 668, 535, 455, 376, 320, 300, 290, 196, 182, 169, 110, 98, 92, 89, 68, 80, 56, 46, 40, 34, 38, 26, 25, 30, 26, 32, 21, 23, 15, 26, 26, 21, 18, 18, 21, 15, 11, 15, 8, 11, 8, 11, 6, 8, 10, 14, 10, 9, 10, 6, 3, 9, 13, 10, 8, 10, 7, 15, 6, 8, 18, 6, 6, 8, 9, 7, 16, 9, 5, 11, 9, 6, 6, 4, 6, 4, 4, 6, 1, 6, 3, 3, 5, 5, 1, 1, 2, 2, 0, 0, 1, 2, 4, 5, 3, 4, 1, 6, 1, 1, 6, 0, 4, 4, 4, 9, 9, 3, 8, 38, 17, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 2]
按词统计长度: [0, 43842, 65146, 78251, 91162, 88795, 87682, 83314, 80400, 76016, 67954, 63181, 57640, 52625, 47843, 44425, 41439, 38280, 33741, 31185, 30236, 27439, 25915, 22485, 20610, 19044, 20133, 18545, 16053, 14513, 16900, 14122, 13205, 11713, 11215, 9690, 10200, 9324, 8649, 7995, 7910, 7351, 8105, 6617, 6371, 6417, 6170, 6107, 5466, 5465, 5082, 4654, 4657, 4630, 4279, 4353, 4203, 4093, 3904, 3826, 3825, 3725, 4119, 3737, 3605, 3476, 3467, 3479, 3544, 3503, 3478, 3756, 3642, 3636, 3649, 3784, 3745, 3621, 3649, 3404, 3301, 3130, 2797, 2423, 2198, 1828, 1610, 1393, 1072, 871, 732, 559, 438, 372, 253, 204, 140, 121, 97, 78, 44, 44, 32, 23, 15, 17, 23, 20, 8, 9, 9, 8, 7, 7, 4, 10, 6, 7, 5, 5, 11, 3, 8, 3, 2, 2, 1, 1, 2, 2, 2, 0, 0, 1, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1]
    
按字构建: 8
按词构建: 4
```

也可以从减少信息损失的角度出发，即保证一定比例的文本不需要截断。

```python
c_sum = sum(c_count)
c_total = 0
for i in range(len(c_count)):
    c_total += c_count[i]
    if c_total >= c_sum * 0.6:
        print('按字构建:', i)
        break
```

该比例取60%时，按字构建与按词构建的适宜长度分别为：

```python
按字构建: 24
按词构建: 15
```

### Tokenizer类

实现按字或按词（通过jieba分词）将文本编码成整数序列。

##### 初始化

根据传入的文本列表，按照`coding`变量给定的方式建立编码词典，`code_dict`用于记录从字/词到整数的映射，`word_dict`用于记录从整数到字/词的映射。规定填充码`PAD`，默认为0。

```python
	def __init__(self, chars, coding, PAD = 0):
        '''
        输入文本列表,按coding方式完成词典构建
        '''
        self.chars = chars
        self.coding = coding
        self.PAD = PAD
        word_list = []
        for each in chars:
            if self.coding == 'c': 
                word_list += list(each)
            elif self.coding == 'w': 
                word_list += jieba.cut(each)
        word_list = list(set(word_list))
        self.code_dict = {word_list[i]:i + PAD + 1 for i in range(len(word_list))}
        self.word_dict = {i + PAD + 1:word_list[i] for i in range(len(word_list))}
        self.word_dict[PAD] = '[PAD]'
```

##### 文本切分

根据编码方式，将文本字符串按字/词分成列表。

```python
    def tokenize(self, sentence):
        '''
        输入单句文本,返回其对应的字符列表
        '''
        if self.coding == 'c':
            return list(sentence)
        elif self.coding == 'w':
            return list(jieba.cut(sentence))
```

##### 编码

根据词典，将字符列表转换为整数序列。

```python
    def encode(self, list_of_chars):
        '''
        输入一个字符列表,返回转换后的数字列表
        '''
        tokens = [self.code_dict[w] for w in list_of_chars]
        return tokens
```

##### 长度整理

将一个整数序列整理为`seq_len`长度的列表，不足部分用`PAD`补齐，超出部分截断。

```python
    def trim(self, tokens, seq_len):
        '''
        整理数字列表的长度
        '''
        if len(tokens) < seq_len:
            tokens += [self.PAD] * (seq_len - len(tokens))
        else:
            tokens = tokens[:seq_len]
        return tokens
```

##### 解码

根据词典，将整数序列翻译为文本。

```python
    def decode(self, tokens):
        '''
        输入一个数字列表,返回其对应的句子
        '''
        chars = ''
        word_list = [self.word_dict[n] for n in tokens]
        for w in word_list:
            chars += w
        return chars
```

##### 整数序列列表

以列表形式返回所有文本的长度为`seq_len`的整数序列。

```python
    def encode_all(self, seq_len):
        '''
        返回所有文本的长度为seq_len的tokens
        '''
        list_of_tokens = []
        for each in self.chars:
            tokens = self.trim(self.encode(self.tokenize(each)), seq_len)
            list_of_tokens.append(tokens)
        return list_of_tokens
```

### 主函数

```python
if __name__ == '__main__':
    weibo_l = wash(FilePath)
    # for i in range(len(weibo_l)):
    #     print(i, weibo_l[i])
    # seqlen_stat(weibo_l)
    tokenizer_1 = Tokenizer(weibo_l, 'w')
    all_tokens = tokenizer_1.encode_all(15)
    for tokens in all_tokens:
        print(tokens, ':\n', tokenizer_1.decode(tokens))
```

部分整数序列与对应文本：

```python
[17522, 32419, 2132, 3950, 19165, 30790, 3950, 20883, 8237, 15229, 32351, 32581, 30397, 29911, 32645] :
 强推比小熊曲奇好吃的曲奇大家吃了都赞不绝口云顶小花名字
[24806, 16799, 20355, 14710, 8237, 23028, 15229, 0, 0, 0, 0, 0, 0, 0, 0] :
 补充一句就是想吃肉了[PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD]
[31997, 25531, 30790, 26354, 18594, 1234, 11361, 31997, 5736, 30790, 18594, 31997, 14550, 31765, 1234] :
 她追求的是钱你给她足够的钱她不会因为你
[17370, 8303, 3775, 18497, 30000, 15229, 21056, 79, 68, 0, 0, 0, 0, 0, 0] :
 无意间就，巴黎铁了个塔！[PAD][PAD][PAD][PAD][PAD][PAD]
[1907, 9099, 8316, 26036, 19334, 32549, 31528, 0, 0, 0, 0, 0, 0, 0, 0] :
 我在1933老场坊。察言观色[PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD]
[8292, 36168, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] :
 庆丰包子铺[PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD][PAD]
[18930, 9257, 14710, 8237, 20840, 4395, 30790, 23905, 3775, 2499, 0, 0, 0, 0, 0] :
 突然好想吃爱慕家的甜品，超赞欧[PAD][PAD][PAD][PAD][PAD]
[31624, 30790, 34352, 35344, 23273, 3775, 21240, 3775, 10389, 23161, 3775, 16346, 0, 0, 0] :
 遗憾的北京之行，拜拜，下次见，哈哈[PAD][PAD][PAD]
[24564, 15237, 1205, 17754, 23574, 3775, 1907, 29396, 24731, 3775, 10371, 27855, 18854, 33345, 1234] :
 今天心里真的很难受，我不想回家，也不愿意离开你
```

## 思考

用tokenizer方法与one-hot方法处理文本时，都建立了字/词与数字之间的对应关系。不同的是，tokenizer得到的编码是直接由字/词对应的数字组成的，而one-hot方法是用01序列中1的位置表示数字。

用one-hot方法对文本进行编码，每个字/词都对应特征空间里的一个维度，因此编码得到的数字序列非常大。而tokenizer方法可以用较短的数字序列表示文本，可读性更强。另一方面，one-hot方法构造了一个特征空间，从而可以很方便地进行距离计算。