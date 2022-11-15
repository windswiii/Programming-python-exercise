# Generator and Iterator

> 生成器和迭代器有两种常见的使用场景。
>
>  一. 后项需要前项导出，且无法通过列表推导式生成。
>
> 例如，时间序列中的“随机游走”便是一种满足上述条件的序列数据。其公式为$$X_t = \mu + X_{t-1} + w_t$$ ，其中$\mu$为漂移量，$w_t$是满足某种条件的独立同分布的随机变量，这里假设其服从正态分布$N(0, \sigma^2)$。本题要求写出实现该功能的迭代器函数。具体要求如下： 
>
> 1. 实现`random_walk`生成器，输入参数$\mu$, $X_0$, $\sigma^2$，$N$，函数将迭代返回N个随机游走生成的变量。 
> 2. 利用zip，实现拼合多个`random_walk`的生成器，以生成一组时间上对齐的多维随机游走序列。 
>
> 二. 需要迭代的内容数据量过大，无法一次性加载。
>
> 例如，在图像相关的深度学习任务中，由于数据总量过大，一次性加载全部数据耗时过长、内存占用过大，因此一般会采用批量加载数据的方法。（注：实际应用中由于需要进行采样等操作，通常数据加载类的实现原理更接近字典，例如pytorch中的`Dataset`类。）
>
> 现提供文件FaceImages.zip(http://vis-www.cs.umass.edu/fddb/originalPics.tar.gz)，其中包含5000余张人脸图片。要求设计`FaceDataset`类，实现图片数据的加载。具体要求：
>
>  	1. 类接收图片路径列表 
>  	2. 类支持将一张图片数据以ndarray的形式返回（可以利用PIL库实现）。 
>  	3. 实现`__iter__`方法。 
>  	4. 实现`__next__`方法，根据类内的图片路径列表，迭代地加载并以ndarray形式返回图片数据。 
>
> 请实现上述生成器和迭代器并进行测试。

## 随机游走

### random_work生成器

```python
def random_walk(mu, x_0, sigmas, N):
    for i in range(N):
        x = mu + x_0 + np.random.normal(0, math.sqrt(sigmas), 1).item()
        yield x
        x_0 = x
```

```python
walk_1 = random_walk(1, 0, 4, 10)
for step in walk_1: print(step)
```

结果如下：

```python
3.7703442299641226
8.767664232184178
10.470612356894152
9.497545827998163
7.318915598601361
7.563171967456009
9.664225053934171
10.08994751252541
```

### zip拼合多个生成器

```python
walk_1 = random_walk(1, 0, 4, 10)
walk_2 = random_walk(2, 1, 1, 10)
walk_3 = random_walk(2, 0, 2, 10)
walk_4 = random_walk(1, 1, 2, 10) 
walk_zipped = zip(walk_1, walk_2, walk_3, walk_4)
for step in walk_zipped:
    print(step)
```

结果如下：

```python
(1.1599376965711146, 3.3757610389440065, 3.442859962421819, 0.8944215748974631)
(0.13175716423495443, 5.459115934548574, 3.6606302998994815, 2.906006604674988)
(2.9058959824345165, 7.1485279472615, 3.880736657462858, 4.20870356992972)
(1.6604261733340082, 9.026359394944517, 6.688861643866451, 5.531413072739449)
(0.20824069304634696, 10.867959409367048, 8.080899922002734, 8.626833792241369)
(0.502744429521787, 14.091241514726391, 9.810638355531818, 7.506720681044827)
(1.5289560303001886, 14.837782754758825, 12.246205575863833, 9.925599689330207)
(4.226727713597665, 16.497801281294812, 12.99035569479406, 14.024290364386385)
(2.835870799540706, 18.569392523099562, 14.880753376935687, 14.872394477232232)
(3.545583750715296, 17.90711929041322, 15.469198311562057, 15.171930296326789)
```

## 批量加载

### 获取文件路径

数据集包含多级文件夹，为了方便迭代器加载文件，需要将所有路径整理为一个列表。

采用递归方法获取所有文件。判断每个路径是否为文件，若是则将该路径添加到路径列表`paths`中，否则对该路径再次调用函数，将其返回的路径全部添加到`paths`中。

```python
def get_paths(dir):
    paths = []
    for path in os.listdir(dir):
        if os.path.isdir(dir + '/' + path):
            paths += get_paths(dir + '/' + path)
        else:
            paths.append(dir + '/' + path)
    return paths
```

对该函数进行测试：

```python
path_list = get_paths('Data/pic_load')
print('\nThe number of pictures:', len(path_list))
```

```python
The number of pictures: 28204
```

### 迭代器：FaceDataset类

#### 初始化

读入文件路径列表。

```python
    def __init__(self, path_list):
        self.path_list = path_list
        self.maxlen = len(path_list)
```

#### \_\_iter__()方法

设置迭代的起点，`self.count = 0`即表示从头开始。

```python
    def __iter__(self):
        self.count = 0
        return self
```

#### \_\_next__()方法

读取图片文件并转为ndarray格式，遍历完所有文件时终止迭代。

```python
    def __next__(self):
        if (self.count >= self.maxlen):
            raise StopIteration
        else:
            path = self.path_list[self.count]
            img = Image.open(path)
            pix = np.asarray(img)
            self.count += 1
            return path, pix
```

对该迭代器进行测试：

```python
facedataset = FaceDataset(path_list[:10])
for pic_path, face in facedataset:
    try:
        print(pic_path, face.shape)
    except StopIteration:
        break
```

结果如下：

```
Data/pic_load/2002/07/19/big/img_130.jpg (450, 363, 3)
Data/pic_load/2002/07/19/big/img_135.jpg (450, 335, 3)
Data/pic_load/2002/07/19/big/img_140.jpg (450, 335, 3)
Data/pic_load/2002/07/19/big/img_141.jpg (450, 351, 3)
Data/pic_load/2002/07/19/big/img_158.jpg (321, 450, 3)
Data/pic_load/2002/07/19/big/img_160.jpg (362, 450, 3)
Data/pic_load/2002/07/19/big/img_163.jpg (362, 450, 3)
Data/pic_load/2002/07/19/big/img_18.jpg (450, 348, 3)
Data/pic_load/2002/07/19/big/img_197.jpg (450, 335, 3)
Data/pic_load/2002/07/19/big/img_198.jpg (450, 319, 3)
```

