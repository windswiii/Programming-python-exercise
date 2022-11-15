import os
import csv
import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = 'Data/PRSA_Data'
OUT_PATH = 'result/pollution/'

class NotNumError(ValueError):
    def __init__(self, filename, row, attribute):
        self.filename = filename
        self.row = row
        self.attribute = attribute
        self.message = '文件{}的第{}行{}属性为空'.format(self.filename, self.row, self.attribute)

class DataAnalyze:
    '''
    读入数据,统计时间及空间分布
    '''
    def __init__(self, data_path):
        self.data_path = data_path

    def load_data(self):
        data_path = self.data_path
        prsa_data = {}
        outfile = open(OUT_PATH + 'error_info.txt', 'w', encoding = 'utf-8')
        
        for path in os.listdir(data_path):
            print('Reading ' + path + '...')
            with open(data_path + '/' + path, 'r', encoding = 'utf-8') as infile:
                data = list(csv.DictReader(infile))
                
                washdata = []
                for i in range(len(data)):
                    row = data[i]
                    for key in row.keys():
                        try:
                            if (row[key] == '') or (row[key] == 'NA'):
                                raise NotNumError(path, i+2, key)
                        except NotNumError as nne:
                            print(nne.message, file = outfile)
                            row[key] = data[i - 1][key]          
                    washdata.append(row)
                
                zone = path.split('_')[2]
                prsa_data[zone] = washdata
                
        outfile.close()
        self.prsa_data = prsa_data
        
    def temporal_pattern(self, zone, *pollutant):
        temporal_data = {}
        for pol in pollutant:
            temporal_data[pol] = [0] * 48
        
        for row in self.prsa_data[zone]:
            month = (int(row['year']) - 2013) * 12 + int(row['month']) - 3
            for pol in pollutant:
                temporal_data[pol][month] += float(row[pol])
        
        with open(OUT_PATH + 'temporal_data_' + zone + '.txt', 'w', encoding = 'utf-8') as outfile:
            for pol in pollutant:
                print('%5s' % pol, ':', temporal_data[pol], file = outfile)
                
        return temporal_data
        
    def spatial_pattern(self, year, *pollutant, month = 0):
        spatial_data = {}
        for zone in self.prsa_data.keys():
            zone_data = {}
            for pol in pollutant:
                zone_data[pol] = 0
            for row in self.prsa_data[zone]:
                if (int(row['year']) == year) and ((month == 0) or (month == int(row['month']))):
                    for pol in pollutant:
                        zone_data[pol] += float(row[pol])
            spatial_data[zone] = zone_data
            
        with open(OUT_PATH + 'spatial_data_' + str(year) + str(month) + '.txt', 'w', encoding = 'utf-8') as outfile:
            print(pollutant, file = outfile)
            for zone in spatial_data.keys():
                print('%13s' % zone, ':', spatial_data[zone], file = outfile)

        return spatial_data


class DataVision:
    '''
    对统计结果进行可视化
    '''
    def __init__(self, temporal_data = {}, spatial_data = {}):
        self.temporal_data = temporal_data
        self.spatial_data = spatial_data
        
    def temporal_vision(self):
        temp_data = self.temporal_data
        pollutant = temp_data.keys()
        for pol in pollutant:
            x = list(range(48))
            y = temp_data[pol]
            # y_max = max(y)
            # y_min = min(y)
            # y = [(i - y_min)/(y_max - y_min) for i in y]
            plt.plot(x, y)
        
        x_loc = list(range(0, 48, 6))
        x_tick = [str(2013 + i//12) + '-' + str(3 + i%12) for i in x_loc]
        plt.xticks(x_loc, x_tick, rotation = 90)
        plt.xlabel('Time')
        plt.ylabel('Pollution')
        plt.legend(pollutant)
        
        plt.savefig(OUT_PATH + 'temporal_' + '_'.join(pollutant) + '.jpg', bbox_inches='tight')
        plt.close()
        
    def spatial_vision(self):
        spat_data = self.spatial_data
        zones = list(spat_data.keys())
        pollutant = list(spat_data[zones[0]].keys())
        
        n = len(pollutant)
        n_bar = len(zones)
        x_index = np.arange(n_bar)
        bar_width = 0.3
        
        for i in range(n):
            pol = pollutant[i]
            y = [spat_data[zone][pol] for zone in zones]
            plt.bar(x_index + (i - (n - 1) / 2) * bar_width, y, bar_width, label = pol)
            
        plt.xticks(x_index, zones, rotation = 90)
        plt.xlabel('Stations')
        plt.ylabel('Pollution')
        plt.legend(pollutant)
        
        plt.savefig(OUT_PATH + 'spatial_' + '_'.join(pollutant) + '.jpg', bbox_inches='tight')
        plt.close()

      
if __name__ == '__main__':
    pollution_data = DataAnalyze(DATA_PATH)
    pollution_data.load_data()
    temporal_data = pollution_data.temporal_pattern('Changping', 'PM2.5', 'PM10', 'SO2')
    spatial_data = pollution_data.spatial_pattern(2013, 'PM2.5', 'PM10', 'SO2', month = 3)
    vision1 = DataVision(temporal_data, spatial_data)
    vision1.temporal_vision()
    vision1.spatial_vision()