# Filter

###### 薛扬帆 20377300

## 库管理及初始化

```python
from PIL import Image			#读取图片
from PIL import ImageFilter		#处理图片
import matplotlib.pyplot as plt	#并列显示图片
import os						#从文件夹中读取图片

Image_Path = 'Data/Photo_filter'	#读取图片路径
Save_Path = 'result/photo_filter'	#保存图片路径
```

## Filter类及其子类

### Filter基类

仅包括两个数据：图片实例`image`和参数列表`args`。 

```python
class Filter:
    '''
    Filter基类
    '''
    def __init__(self, image, *args):
        self.image = image
        self.args = args
```

### ContourF

对图像进行边缘提取。

```python
class ContourF(Filter):
    '''
    边缘提取子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.CONTOUR)
```

### SharpenF

对图像进行锐化处理。

```python
class SharpenF(Filter):
    '''
    锐化处理子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.SHARPEN)
```

### BlurF

对图像进行模糊处理。

```python
class BlurF(Filter):
    '''
    模糊处理子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.BLUR())
```

### ZoomF

对图像进行缩放处理。利用该类进行图片处理时，应在图像参数后再添加一个浮点数，表示图片缩放的比例。

```python
class ZoomF(Filter):
    '''
    缩放处理子类
    '''
    def process(self):
        ratio = self.args[0]
        height = int(self.image.size[1] * ratio)
        width = int(self.image.size[0] * ratio)
        return self.image.resize((width, height))
```

### CropF

对图像进行裁剪。利用该类进行图片处理时，应在图像参数后再添加四个浮点数（0-1），依次表示左、上、右、下四个边界的相对位置。

```python
class CropF(Filter):
    '''
    裁剪处理子类
    '''
    def process(self):
        box = list(self.args[:4])
        height = self.image.size[1]
        width = self.image.size[0]
        box[0] *= width
        box[2] *= width
        box[1] *= height
        box[3] *= height
        return self.image.crop(box)
```

### Filter处理效果

用不同的滤波器对同一张图片进行处理，结果如下：

（依次为contour、原图、sharpen、blur、crop、zoom）

<img src="images\contour.jpg" alt="contour" style="zoom:36.5%;" /><img src="images\moon.jpg" alt="moon" style="zoom:36.5%;" /><img src="D:\HUAWEI\Documents\all_code\Python\result\photo_filter\sharpen.jpg" alt="sharpen" style="zoom:36.5%;" /><img src="images\blur.jpg" alt="blur" style="zoom:36.5%;" /><img src="images\crop.jpg" alt="crop" style="zoom:36.5%;" /><img src="images\zoom_out.jpg" alt="zoom_out" style="zoom:36.5%;" />

## ImageShop类

用于对图片进行批处理。包括读入图片、调用`Filter`子类进行处理、展示及保存处理后的图片。

#### 初始化函数

初始化图片类型及需要处理的图片路径。

```python
	def __init__(self, image_type, path):
        self.image_type = image_type
        self.image_file = path
```

#### 图片加载

用PIL.Image中的`open()`读取路径中的图片，将image实例存入原始图片列表`original_images`中。

输入的路径有两种类型，一种是图片的直接路径，另一种是包含图片的文件夹路径。对于前者，直接将读取该路径的图片存入列表；后者则需要通过`os.listdir()`获取该路径下所有对应格式的图片。

由于后续保存处理后的图片时默认格式为JPG，加载时用`convert('RGB')`方法直接将图片转为RGB三通道模式。

```python
    def load_images(self):
        image_type = self.image_type
        image_file = self.image_file
        image_list = []
        if os.path.isdir(image_file):
            for file in os.listdir(image_file):
                if file.split('.')[-1] == image_type:
                    image_list.append(Image.open(image_file+'/'+file).convert('RGB'))
        else:
            image_list.append(Image.open(image_file).convert('RGB'))
        self.original_images = image_list
```

#### 图片处理（内部方法）

传入图片列表、`Filter`子类及对应参数，对列表中的所有图片进行处理，返回处理好的列表。

```python
    def __batch_ps(self, image_list, filter_name, *args):
        image_list1 = []
        for image in image_list:
            image_list1.append(filter_name(image, *args).process())
        return image_list1
```

#### 图片处理（对外方法）

依次输入需要进行的处理（`Filter`子类）及其所需参数。

为实现一次进行若干操作，可以将所有参数读入一个不定长参数元组`args`中，依次检索该元组中的元素，若为类，则增加一个新的处理步骤；若为其他类型，则添加到到前一个处理步骤的参数中。

```python
	filters = []
    for arg in args:
    	if type(arg) == type:
    		filter = [arg]
    		filters.append(filter)
    	else:
    		filters[-1].append(arg)
```

调用时输入参数的形式如下：

```python
	imageshop_0.batch_ps(SharpenF,
                     	ContourF,
                     	CropF, 0, 0.2, 1, 0.8,
                     	BlurF, 
                     	ZoomF, 2)
```

之后从步骤列表`filters`中读取参数，依次调用`__batch_ps()`对图片进行批处理。最终函数如下：

```python
    def batch_ps(self, *args):
        filters = []
        for arg in args:
            if type(arg) == type:
                filter = [arg]
                filters.append(filter)
            else:
                filters[-1].append(arg)
        image_list = self.original_images
        for filter in filters:
            image_list = self.__batch_ps(image_list, *filter)
        self.processed_images = image_list
```

#### 处理效果显示

利用matplotlib的`subplot()`函数展示图片的处理效果。可输入`row`和`column`参数改变排列格式，默认为3*2。

定义一个进行图片显示的内部方法，根据输入的图片列表进行显示。

```python
    def __display(self, image_list, row, column):
        for i in range(row * column):
            if i >= len(image_list):
                break
            plt.subplot(row, column, i + 1)
            plt.axis('off')
            plt.imshow(image_list[i])
        plt.show()
```

在此基础上，分别定义显示原图和处理后图像的函数，便于比较处理结果。

```python
    def display_original(self, row = 2, column = 3):
        self.__display(self.original_images, row, column)
        
    def display_processed(self, row = 2, column = 3):
        self.__display(self.processed_images, row, column)
```

#### 保存图片

将处理后的图片保存到本地。

```python
    def save_images(self, path):
        image_list = self.processed_images
        for i in range(len(image_list)):
            image_list[i].save(path + '/process1_' + str(i) + '.jpg')
```

## TestImageShop类

测试`ImageShop`类的批处理效果。

```python
class TestImageShop:
    '''
    测试类
    '''
    def __init__(self):
        imageshop_0 = ImageShop('jpg', Image_Path)
        imageshop_0.load_images()
        imageshop_0.batch_ps(SharpenF,
                             ContourF,
                             CropF, 0, 0.2, 1, 0.8,
                             BlurF, 
                             ZoomF, 2)
        imageshop_0.display_original()
        imageshop_0.display_processed()
        imageshop_0.save_images(Save_Path)
```

##### 处理结果

原图：

![Figure_0](images\Figure_0.png)

处理后：

![Figure_1](images\Figure_1.png)

## 图片相似度分析

观察部分过滤器的处理结果，可以发现不同的过滤器都强调或减弱了图像的某些特征：边缘提取过滤了原始图片的色块信息，只保留轮廓；锐化处理提高了图片的清晰度，使色彩更鲜明，边缘更突出，同时也使得噪点更加明显；模糊处理则相反，减弱了噪点，也使得图片边缘更模糊。

在图片相似度计算中，由于边缘提取和模糊处理丢失了部分信息，一般会使得图片的相似度更高；而锐化处理会强调图片之间的差异，降低相似度。对图片进行此类预处理可以突出重点信息，减少数据量，使得下游机器学习模型的计算量大为减少，效率更高。

简单采用直方图计算图像相似度，验证以上猜想。

### Similar_Calculate类

#### 初始化函数

包含两个参数，即需要进行相似度分析的两张图片。首先将两张图片缩放为相同大小，再用`convert('L')`方法将图片转为灰度图，方便后续处理。

```python
    def __init__(self, image_1, image_2):
        image_2 = image_2.resize(image_1.size)
        self.image_1 = image_1.convert('L')
        self.image_2 = image_2.convert('L')
```

#### 相似度计算

定义一个计算图片相似度的内部函数。用`getdata()`方法得到图像的直方图，通过对比每个像素值的差异，计算两个图像的相似度。

```python
    def __calculate(self, image_1, image_2):
        hist_1 = list(image_1.getdata())
        hist_2 = list(image_2.getdata())
        simi_sum = 0
        for i in range(len(hist_1)):
            if hist_1[i] == hist_2[i]:
                simi_sum += 1
            else:
                simi_sum += 1 - float(abs(hist_1[i] - hist_2[i])) / max(hist_1[i], hist_2[i])
        return simi_sum / len(hist_1)
```

#### 相似度比较

输入一个处理方法（`Filter`子类），用该过滤器对图片进行处理，分别计算处理前后的相似度，进行比较。

```python
    def similar_compare(self, filter_name, *args):
        print('-----')
        image_1 = self.image_1
        image_2 = self.image_2
        print('Original similarity:', self.__calculate(image_1, image_2))
        rimage_1 = filter_name(image_1, *args).process()
        rimage_2 = filter_name(image_2, *args).process()
        print('Processed similarity:', self.__calculate(rimage_1, rimage_2))
```

### TestSimilar类

对`Similar_Canculate`类进行测试。

```python
class TestSimilar:
    '''
    测试类
    '''
    def __init__(self):
        images = ImageShop('jpg', Image_Path)
        images.load_images()
        similar_0 = Similar_Calculate(images.original_images[0], images.original_images[1])
        similar_0.similar_compare(ContourF)
        similar_0.similar_compare(BlurF)
        similar_0.similar_compare(ZoomF, 0.5)
        similar_0.similar_compare(ZoomF, 2)
        similar_0.similar_compare(SharpenF)
```

结果如下：

```python
--ContourF--
Original similarity: 0.4481021143292421
Processed similarity: 0.8338541870394443
--BlurF--
Original similarity: 0.4481021143292421
Processed similarity: 0.4701540575195021
--ZoomF, 0.5--
Original similarity: 0.4481021143292421
Processed similarity: 0.4637006865295752
--ZoomF, 2--
Original similarity: 0.4481021143292421
Processed similarity: 0.45301738434690336
--SharpenF--
Original similarity: 0.4481021143292421
Processed similarity: 0.4049437760926613
```

结果与预测基本符合。边缘处理显著提高了图片之间的相似度，而模糊与缩放都略微提高了图片的相似度，锐化处理则使相似度降低。
