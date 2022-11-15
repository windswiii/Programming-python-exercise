# Data Visualization

> 在使用python时，我们经常会用到许多工具库，它们提供了较为方便的函数调用。但是仍然会有一些情况，例如数据类型或格式不符合函数要求，参数存在差异等，使得调用前需要对数据进行额外处理。本次作业要求基于matplotlib，wordcloud，PIL, imageio等绘图库的绘制函数，设计并实现适配器抽象类和不同的适配类，以实现不同类型数据的多样化可视。具体要求如下：
>
> 1. 要求设计抽象类Plotter，至少包含抽象方法plot(data, *args, **kwargs)方法，以期通过不同子类的具体实现来支持多类型数据的绘制，至少包括数值型数据，文本，图片等。
>
> 2. 实现类PointPlotter, 实现数据点型数据的绘制，即输入数据为[(x,y)...]型，每个元素为一个Point类的实例。
>
> 3. 实现类ArrayPlotter, 实现多维数组型数据的绘制，即输入数据可能是[[x1,x2...],[y1,y2...]]或者[[x1,x2...],[y1,y2...],[z1,z2...]]。
>
> 4. 实现类TextPlotter，实现文本型数据的绘制，即输入数据为一段或多段文本，应进行切词，关键词选择（根据频率或tf-idf)，继而生成词云。
>
> 5. 实现类ImagePlotter，实现图片型数据的绘制，即输入数据为图片的路径或者图片内容（可以是多张图片），呈现图片并按某种布局组织（如2x2等)。
>
> 6. 实现类GifPlotter, 支持一组图片序列的可视化（通过文件路径或图片内容输入），但输出是gif格式的动态图。
> 7. 在3中，如果多维数组超过3维，可否支持pca等降维并绘制，实现类KeyFeaturePlooter？（了解pca或者TSNE）
> 8. 如果输入是一段音频（比如mp3文件），如何进行绘制，实现类MusickPlotter？（了解librosa里的display模块）
> 9. 在6中，如果输入是一段落视频的话，能否通过帧采样，将视频绘制为gif并输出为微信表情包，实现类VideoPlotter？（了解cv2)

## 库管理

```python
import abc
import os
import numpy as np
import jieba
from PIL import Image
import imageio
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import cv2
import librosa, librosa.display
from sklearn.decomposition import PCA
```

## 抽象类Plotter

```python
class Plotter(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def plot(self, data, *args, **kwargs):
        pass  
```

### PointPlotter类

根据输入的坐标数据绘制散点图。

```python
class PointPlotter():
    def __init__(self, data):
        self.x = [p[0] for p in data]
        self.y = [p[1] for p in data]
        
    def plot_point(self, *args):
        plt.scatter(self.x, self.y)
        plt.savefig(args[0])
        plt.close()
```

适配器：

```python
class PointAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_point(*args)
```

### ArrayPlotter类

根据输入的多维数组绘制散点图，每一维对应点在该维的坐标。

```python
class ArrayPlotter():
    def __init__(self, data):
        self.m = data
        
    def plot_array(self, *args):
        if len(self.m) == 3:
            fig = plt.figure()
            ax = fig.gca(projection = "3d")
            ax.scatter(self.m[0], self.m[1], self.m[2])
        elif len(self.m) == 2:
            plt.scatter(self.m[0], self.m[1])
            
        plt.savefig(args[0])
        plt.close()
```

适配器：

```python
class ArrayAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_array(*args)    
```

#### KeyFeaturePlotter子类

在`ArrayAdapter`类的基础上，添加`datapca`方法，用于对数据进行PCA降维。

```python
class KeyFeaturePlotter(ArrayPlotter):
    def datapca(self):
        if len(self.m) > 3:
            mat = np.array(self.m)
            mat = np.transpose(mat)
            pca = PCA(n_components = 3)
            mat = pca.fit_transform(mat)
            mat = np.transpose(mat)
            mat.tolist()
            self.m = mat
```

### TextPlotter类

根据输入的文本数据绘制词云图。

先统计词频，根据词频获取特征词，并据此绘制词云图。可通过参数设置特征集的大小。

```python
class TextPlotter:
    def __init__(self, data, stopwords):
        seg_list = list(word for word in jieba.lcut(data) if word not in stopwords)
        freq_dict = {}
        for word in seg_list:
            if word in freq_dict:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1
        freq_rdict = {k: v for k, v in sorted(freq_dict.items(), key = lambda item: item[1], reverse = True)}
        self.freq_dict = freq_rdict
        
    def plot_txt(self, *args):
        freqs = {}
        l = 0
        for key in list(self.freq_dict.keys()):
            freqs[key] = self.freq_dict[key]
            l += 1
            if l >= args[1]: break
        cloud0 = WordCloud(
            background_color = 'rgba(0,213,254,1)',
            mode = 'RGBA',
            colormap = 'Set2',
            font_path = 'C:/Windows/Font/simhei.ttf',
            max_font_size = 200,
            min_font_size = 2,
            width = 500,
            height = 500,
        )
        cloud = cloud0.generate_from_frequencies(freqs)
        cloud.to_file(args[0])
```

适配器：

```python
class TextAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_txt(*args)
```

### ImagePlotter类

对输入的多张图片布局显示。可通过参数设置具体布局。

```python
class ImagePlotter:
    def __init__(self, data):
        self.pic = data
        
    def plot_ima(self, *args):
        path, row, column = args
        for i in range(row * column):
            if i >= len(self.pic):
                break
            plt.subplot(row, column, i + 1)
            plt.axis('off')
            plt.imshow(self.pic[i])
        plt.savefig(path)
        plt.close()
```

适配器：

```python
class ImageAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_ima(*args) 
```

### GifPlotter类

根据输入的多张图片，用imageio库的`mimsave`方法生成gif图。

```python
class GifPlotter:
    def __init__(self, data):
        self.pic = data
    
    def plot_gif(self, *args):
        imageio.mimsave(args[0], self.pic, fps = 10)
```

适配器：

```python
class GifAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_gif(*args)
```

#### VideoPlotter子类

在`GifPlotter`类的基础上重新进行初始化。输入视频路径，进行帧采样并存储。

```python
class VideoPlotter(GifPlotter):
    def __init__(self, path):
        data = []
        cap = cv2.VideoCapture(path)
        for i in range(10):
            ret, frame = cap.read()
            if ret: 
                data.append(frame)
            else: 
                break
        self.pic = data
        cap.release()
```

### MusicPlotter类

利用librosa库，对输入的音频文件进行读取及可视化。

```python
class MusicPlotter:
    def __init__(self, path):
        signal, sr = librosa.load(path)
        self.signal = signal
        self.sr = sr

    def plot_music(self, *args):
        librosa.display.waveshow(self.signal, sr = self.sr)
        plt.xlabel('time')
        plt.ylabel('amplitude')
        plt.savefig(args[0])
```

适配器：

```python
class MusicAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj

    def plot(self, *args):
        self.obj.plot_music(*args)
```

## 测试

### 点型数据

```python
    points = PointPlotter([(1,2), (5,9), (3,2), (4,4)])
    object1 = PointAdapter(points)
    object1.plot('result/plotter/point.jpg')
```

![point](images\point.jpg)

### 数组型数据

```python
    arrays = ArrayPlotter([[9,2,0,4], [9,1,7,6], [0,5,8,9]])
    object2 = ArrayAdapter(arrays)
    object2.plot('result/plotter/array.jpg')
```

![array](images\array.jpg)

### 高维数组型数据

```python
    data = [[1,2,3,4,5], [2,3,4,5,6], [3,4,5,6,7], [4,5,6,7,8]]
    mutiarray = KeyFeaturePlotter(data)
    mutiarray.datapca()
    object7 = ArrayAdapter(mutiarray)
    object7.plot('result/plotter/mutiarray.jpg')
```

![mutiarray](images\mutiarray.jpg)

### 文本数据

```python
    with open('Data/TextProcess/danmu.txt', 'r', encoding = 'utf-8') as infile:
        text = infile.read()
    with open('Data/TextProcess/stopwords_list.txt', 'r', encoding = 'utf-8') as infile:
        stopword_table = infile.readline()
    stopword_list = [line.strip('\n') for line in stopword_table]
    text = TextPlotter(text, stopword_list)
    object3 = TextAdapter(text)
    object3.plot('result/plotter/wordcloud.png', 30)
```

![wordcloud](images\wordcloud.png)

### 图片数据

```python
    pic_path = 'Data/Photo_filter'
    pic_list = []
    for path in os.listdir(pic_path):
        pic_list.append(Image.open(pic_path + '/' + path))
    
    images = ImagePlotter(pic_list)
    object4 = ImageAdapter(images)
    object4.plot('result/plotter/images.jpg', 2, 3)
```

![images](images\images.jpg)

### 图片生成gif

```python
    gifs = GifPlotter(pic_list)
    object5 = GifAdapter(gifs)
    object5.plot('result/plotter/planet.gif')
```

### 视频转gif

```python
    video = VideoPlotter('Data/plotter/test.mp4')
    object8 = GifAdapter(video)
    object8.plot('result/plotter/video.gif')
```

### 音频数据

```python
    music = MusicPlotter('Data/wrapper/ring_1.mp3')
    object6 = MusicAdapter(music)
    object6.plot('result/plotter/music.jpg')
```

![music](images\music.jpg)