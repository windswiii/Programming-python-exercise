from genericpath import isdir
from PIL import Image
import numpy as np
import os

def get_paths(dir):
    paths = []
    for path in os.listdir(dir):
        if os.path.isdir(dir + '/' + path):
            print('\rReading {} ...'.format(dir + '/' + path), end = '')
            paths += get_paths(dir + '/' + path)
        else:
            paths.append(dir + '/' + path)
    return paths
    

class FaceDataset:
    def __init__(self, path_list):
        self.path_list = path_list
        self.maxlen = len(path_list)
    
    def __iter__(self):
        self.count = 0
        return self
    
    def __next__(self):
        if (self.count >= self.maxlen):
            raise StopIteration
        else:
            path = self.path_list[self.count]
            img = Image.open(path)
            pix = np.asarray(img)
            self.count += 1
            return path, pix


path_list = get_paths('Data/pic_load')
print('\nThe number of pictures:', len(path_list))

facedataset = FaceDataset(path_list[:10])
for pic_path, face in facedataset:
    try:
        print(pic_path, face.shape)
    except StopIteration:
        break