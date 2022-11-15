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


class Plotter(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def plot(self, data, *args, **kwargs):
        pass  
    

class PointPlotter:
    def __init__(self, data):
        self.x = [p[0] for p in data]
        self.y = [p[1] for p in data]
        
    def plot_point(self, *args):
        plt.scatter(self.x, self.y)
        plt.savefig(args[0])
        plt.close()
        
class PointAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_point(*args)
        
        
class ArrayPlotter:
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
    
class ArrayAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_array(*args)    

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

class TextAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_txt(*args)


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
   
class ImageAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_ima(*args) 


class GifPlotter:
    def __init__(self, data):
        self.pic = data
    
    def plot_gif(self, *args):
        imageio.mimsave(args[0], self.pic, fps = 10)

class GifAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj
    def plot(self, *args):
        self.obj.plot_gif(*args)

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
        
class MusicAdapter(Plotter):
    def __init__(self, obj):
        self.obj = obj

    def plot(self, *args):
        self.obj.plot_music(*args)


     
if __name__ == '__main__':

    points = PointPlotter([(1,2), (5,9), (3,2), (4,4)])
    object1 = PointAdapter(points)
    object1.plot('result/plotter/point.jpg')
    
    arrays = ArrayPlotter([[9,2,0,4], [9,1,7,6], [0,5,8,9]])
    object2 = ArrayAdapter(arrays)
    object2.plot('result/plotter/array.jpg')

    with open('Data/TextProcess/danmu.txt', 'r', encoding = 'utf-8') as infile:
        text = infile.read()
    with open('Data/TextProcess/stopwords_list.txt', 'r', encoding = 'utf-8') as infile:
        stopword_table = infile.readline()
    stopword_list = [line.strip('\n') for line in stopword_table]
    text = TextPlotter(text, stopword_list)
    object3 = TextAdapter(text)
    object3.plot('result/plotter/wordcloud.png', 30)
    
    
    pic_path = 'Data/Photo_filter'
    pic_list = []
    for path in os.listdir(pic_path):
        pic_list.append(Image.open(pic_path + '/' + path))
        
    images = ImagePlotter(pic_list)
    object4 = ImageAdapter(images)
    object4.plot('result/plotter/images.jpg', 2, 3)
    
    gifs = GifPlotter(pic_list)
    object5 = GifAdapter(gifs)
    object5.plot('result/plotter/planet.gif')
    
    
    music = MusicPlotter('Data/wrapper/ring_1.mp3')
    object6 = MusicAdapter(music)
    object6.plot('result/plotter/music.jpg')
    
    data = [[1,2,3,4,5], [2,3,4,5,6], [3,4,5,6,7], [4,5,6,7,8]]
    mutiarray = KeyFeaturePlotter(data)
    mutiarray.datapca()
    object7 = ArrayAdapter(mutiarray)
    object7.plot('result/plotter/mutiarray.jpg')
    
    video = VideoPlotter('Data/plotter/test.mp4')
    object8 = GifAdapter(video)
    object8.plot('result/plotter/video.gif')