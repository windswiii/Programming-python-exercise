from PIL import Image
from PIL import ImageFilter
import matplotlib.pyplot as plt
import os

Image_Path = 'Data/Photo_filter'
Save_Path = 'result/photo_filter'

class Filter:
    '''
    Filter基类
    '''
    def __init__(self, image, *args):
        self.image = image
        self.args = args
        
class ContourF(Filter):
    '''
    边缘提取子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.CONTOUR)
    
class SharpenF(Filter):
    '''
    锐化处理子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.SHARPEN)
    
class BlurF(Filter):
    '''
    模糊处理子类
    '''
    def process(self):
        return self.image.filter(ImageFilter.BLUR())
    
class ZoomF(Filter):
    '''
    缩放处理子类
    '''
    def process(self):
        ratio = self.args[0]
        height = int(self.image.size[1] * ratio)
        width = int(self.image.size[0] * ratio)
        return self.image.resize((width, height))
     
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

class ImageShop:
    def __init__(self, image_type, path):
        self.image_type = image_type
        self.image_file = path
        
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
    
    def __batch_ps(self, image_list, filter_name, *args):
        image_list1 = []
        for image in image_list:
            image_list1.append(filter_name(image, *args).process())
        return image_list1

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
        
    def __display(self, image_list, row, column):
        for i in range(row * column):
            if i >= len(image_list):
                break
            plt.subplot(row, column, i + 1)
            plt.axis('off')
            plt.imshow(image_list[i])
        plt.show()
        
    def display_original(self, row = 2, column = 3):
        self.__display(self.original_images, row, column)
        
    def display_processed(self, row = 2, column = 3):
        self.__display(self.processed_images, row, column)
        
    def save_images(self, path):
        image_list = self.processed_images
        for i in range(len(image_list)):
            image_list[i].save(path + '/process1_' + str(i) + '.jpg')
        

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

class Similar_Calculate:
    '''
    图片相似度计算(直方图方法)
    '''
    def __init__(self, image_1, image_2):
        image_2 = image_2.resize(image_1.size)
        self.image_1 = image_1.convert('L')
        self.image_2 = image_2.convert('L')

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
    
    def similar_compare(self, filter_name, *args):
        print('-----')
        image_1 = self.image_1
        image_2 = self.image_2
        print('Original similarity:', self.__calculate(image_1, image_2))
        rimage_1 = filter_name(image_1, *args).process()
        rimage_2 = filter_name(image_2, *args).process()
        print('Processed similarity:', self.__calculate(rimage_1, rimage_2))
    
    
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
   
if __name__ == '__main__':
    # TestImageShop()
    TestSimilar()
    