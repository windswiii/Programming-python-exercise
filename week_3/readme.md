# Networks Graph

## 包结构

- **GraphStat**
    - node.py
    - graph.py
    - stat.py
    - visual.py

### node

实现基本的节点信息读取和打印。包括两个函数：

`init_node()`  从文件中读取节点信息。文件中节点信息是按ID排列的，因此选择列表方式存储，每个节点的索引值即为ID。

`print_node()`  打印对应节点的信息。

```python
import csv

def init_node(path):
    '''
    从数据文件中加载所有节点及其属性,返回一个列表
    '''
    nodes = []
    print('Reading ' + path + '...')
    in_file =  open(path, 'r', encoding = 'utf-8')
    node_table = list(csv.reader(in_file))
    for line in node_table[1:]:
        node = {
            'views'       : line[0],
            'mature'      : line[1],
            'life_time'   : line[2],
            'created_at'  : line[3],
            'updated_at'  : line[4],
            'dead_account': line[6],
            'language'    : line[7],
            'affiliate'   : line[8]
        }
        nodes.append(node)
    in_file.close()
    return nodes

def print_node(nodes, i):
    '''
    输出给定节点的属性
    '''
    node = nodes[i]
    print(
        'Node_ID     :', i,
        '\nviews       :', node['views'],
        '\nmature      :', node['mature'],
        '\nlife_time   :', node['life_time'],
        '\ncreated_at  :', node['created_at'],
        '\nupdated_at  :', node['updated_at'],
        '\ndead_account:', node['dead_account'],
        '\nlanguage    :', node['language'],
        '\naffiliate   :', node['affiliate']
    )
```

### graph

利用networkx库构建网络，并用邻接矩阵方法实现网络存储。包括三个函数：

`init_graph()`  用networkx库的`Graph()`方法构建网络，添加节点和边。

`save_graph()`  用二维邻接矩阵储存网络。

`load_graph()`  将邻接矩阵写入文件。实际测试中，发现写入内存速度极慢，因此只保存了10000个节点的网络所生成的邻接矩阵。

```python
import networkx as nx

def init_graph(n, edges):
    '''
    构建网络
    '''
    net = nx.Graph()
    print('Adding nodes...')
    net.add_nodes_from(list(range(n)))
    c = 1
    for edge in edges:
        if c % 50000 == 0: 
            print('\rAdding edges...%04.2f' % (c * 100 / len(edges)) + '%', end = '')
        c += 1
        if (int(edge[0]) < n) and (int(edge[1]) < n):
            net.add_edge(int(edge[0]), int(edge[1]))
    print('\rAdding edges...100.00%')
    return net

def save_graph(n, edges):
    '''
    序列化图信息
    '''
    matrix = [[0] * n for i in range(n)]

    c = 1
    for edge in edges:
        if c % 50000 == 0: 
            print('\rCreating matrix...%04.2f' % (c * 100 / len(edges)) + '%', end = '')
        c += 1
        u, v = int(edge[0]), int(edge[1])
        if (u < n) and (v < n):
            matrix[u][v] = 1
            matrix[v][u] = 1
    print('\rCreating matrix...100.00%')
    return matrix

def load_graph(matrix, path):
    '''
    将网络加载至内存
    '''
    out_file = open(path, 'w', encoding = 'utf-8')
    c = 1
    for line in matrix:
        if c % 1000 == 0: print('\r', c, end = '')
        c += 1
        print(''.join(str(i) for i in line), file = out_file)
    out_file.close()
    return 0
```

### stat

计算度分布及节点views属性的分布情况，将统计结果（包括平均值和区间分布）写入文件中。

```python
import networkx as nx

def cal_degree_distribution(graph):
    '''
    计算度分布
    '''
    degree_count = {}
    for i in range(nx.number_of_nodes(graph)):
        deg = graph.degree(i)
        if deg in degree_count: degree_count[deg] += 1
        else: degree_count[deg] = 1
    degree_count = sorted(degree_count.items())
    ave = nx.number_of_edges(graph) * 2 / nx.number_of_nodes(graph)
    
    with open('result/degree_distribution.txt', 'w', encoding = 'utf-8') as out_file:
        print('The average of degree:%.2f'%ave, file = out_file)
        for l in degree_count:
            print('%3d : %4d'% (l[0], l[1]), file = out_file)
   
def cal_views_distribution(node_info):
    '''
    计算views属性的分布
    ''' 
    views_count = {}
    total = 0
    for node in node_info:
        total += int(node['views'])
        views = int(node['views']) // 1000
        if views in views_count: views_count[views] += 1
        else: views_count[views] = 1
    ave = total / len(node_info)
    count_list = sorted(views_count.items())

    with open('result/views_distribution.txt', 'w', encoding = 'utf-8') as out_file:
        print('The average of views:%.2f'%ave, file = out_file)
        for l in count_list:
            print('%dK-%dK : %d' % (l[0], l[0] + 1,  l[1]), file = out_file)
```

### visual

绘制局部网络；实现节点属性的统计及可视化。包括两个函数：

##### plot_ego(graph, node)

绘制节点node及其邻居节点的局部网络。由于选择的所有节点都与node节点相连，节点数较少时，网络结构还算清晰；节点数过多时绘制出的网络结构几乎没有区别，都呈密集的中心放射状。

<img src="images\partnetwork2_1011.png" alt="partnetwork2_1011" style="zoom:50%;" /><img src="images\partnetwork2_6761.png" alt="partnetwork2_6761" style="zoom:50%;" />

为了使绘制出的网络结构更加均匀，将中心节点删去；同时为保证可读性，对节点的数量加以限制。

```python
part_nodes = list(nx.all_neighbors(graph, node))[:300] # + [node]
```

networkx提供了直接绘制局部节点图的方法，即`nodelist`和`edgelist`参数，但在实际使用中发现这种方法速度非常慢，猜测该方法可能是先构建整体网络再显示局部。

为提高效率，先根据选中的节点构建一个新的网络`part_graph`，再用`draw_networkx`方法直接绘制其图像。

用`edges()`方法从原网络中找出节点相邻的边，再筛选掉另一端不在局部图中的边。

```python
part_edges = []
    for edge in nx.edges(graph, part_nodes):
        if edge[1] in part_nodes:
            part_edges.append(edge)
```

将节点和边添加至局部网络中，然后进行绘制，最终函数如下：

```python
def plot_ego(graph, node):
    '''
    绘制节点的局部网络
    '''
    print('Creating part graph...')
    part_graph = nx.Graph()
    part_nodes = list(nx.all_neighbors(graph, node))[:300] # + [node]
    part_edges = []
    for edge in nx.edges(graph, part_nodes):
        if edge[1] in part_nodes:
            part_edges.append(edge)
    part_graph.add_nodes_from(part_nodes)
    part_graph.add_edges_from(part_edges)
    # 过滤掉孤立点
    for node in part_nodes:
        if len(nx.edges(part_graph, [node])) == 0:
            part_graph.remove_node(node)
            
    print('Drawing...')
    pos = nx.spring_layout(part_graph)
    plt.rcParams['figure.figsize']= (7.5, 7.5)
    colors = range(nx.number_of_edges(part_graph))
    nodesizes = [(1.5 + 0.1 * part_graph.degree(node)) for node in nx.nodes(part_graph)]
    nx.draw_networkx(
        part_graph, pos, 
        with_labels = False,
        node_size = nodesizes,
        node_color = 'navy',
        edge_color = colors,
        edge_cmap = plt.cm.RdBu,
        alpha = 0.5,
        width = 0.5
        )
    plt.axis('off')
    plt.xlim(-0.6, 0.6)
    plt.savefig('result/partnetwork2_'+ str(node) + '.png')
    plt.show()
```

##### 一些结构较清晰的局部网络

<img src="images\partnetwork2_48372.png" alt="partnetwork2_48372" style="zoom:50%;" /><img src="images\partnetwork2_66353.png" alt="partnetwork2_66353" style="zoom:50%;" />

<img src="images\partnetwork_138826.png" alt="partnetwork_138826" style="zoom:50%;" /><img src="images\partnetwork2_1155.png" alt="partnetwork2_1155" style="zoom:50%;" />

##### plot_nodes_attr(graph, node_info, attribute)

根据输入的参数，对所有节点的对应属性进行可视化分析。由于不同属性的数据特征不同，需要分别进行处理。

`mature` `affiliate`这两个属性为布尔值，只需统计0，1的频数，用柱形图表示统计结果。

```python
	if (attribute == 'mature') or (attribute == 'affiliate'):
        count = [0, 0]
        for node in node_info:
            count[int(node[attribute])] += 1
        plt.bar(range(2), count, width = 0.5, tick_label = ['False', 'True'], color = ['lightcoral', 'yellowgreen'])
```

<img src="images\affiliate.png" alt="affiliate" style="zoom:43%;" /><img src="images\mature.png" alt="mature" style="zoom:43%;" />

`language`用字典记录每种语言的频数，采用饼状图以更好地表现各语言的占比。

```python
if (attribute == 'language'):
        
        count_dict = {}
        for node in node_info:
            lan = node['language']
            if lan in count_dict: count_dict[lan] += 1
            else: count_dict[lan] = 1
        
        count_list = [[k, v] for k, v in sorted(count_dict.items(), key = lambda item: item[1], reverse = True)]
        count = [l[1] for l in count_list]
        languages = [l[0] for l in count_list]
        plt.pie(count,
            labels = languages,
            colors = plt.get_cmap('Spectral')(np.linspace(1, 0, len(languages))),
            textprops = {'color': 'w'}
        )
        
        plt.legend(loc = 'right', borderaxespad = 1.2, bbox_to_anchor=(1.25/1, 1/2)) 
```

![language](images\language.png)

`views` `degree` `life_time`三个属性比较相似，采用字典进行统计时，键和值均为数值。而在数据的具体特征上，这三个属性也有所不同，需要更进一步的处理。

`degree`数据的分布比较连续，根据前面stat模块的统计结果，1000以内度的分布几乎是连续的（即每个度的值都至少出现过一次），可以进行单独计数。另外该数据的数量级跨度较大，可以取对数使图像分布更均匀。根据数据画出散点图后，再用scipy库中的`make_interp_spline()`方法绘制拟合曲线，得到较为平滑的分布趋势。

```python
	if (attribute == 'degree'):
        
        count_dict = {}
        for node in graph.nodes():
            deg = graph.degree(node)
            if deg in count_dict: count_dict[deg] += 1
            else: count_dict[deg] = 1
        count_list = sorted(count_dict.items())
        
        count = [l[1] for l in count_list]
        degrees = [np.log10(l[0]+0.0001) for l in count_list]
        plt.scatter(degrees, count, s = 2, c = 'lightcoral')
        
        x_smooth = np.linspace(min(degrees), max(degrees), 60)
        y_smooth = make_interp_spline(degrees, count)(x_smooth)
        plt.plot(x_smooth, y_smooth, c = 'b')
        
        plt.xlim(0, 6)
        plt.xlabel('Log(degree)')
        plt.ylabel('Frequency')
```

![degree](images\degree.png)

`views` `life_time`的分布比较离散，可以划分区间统计其频数。对于`views`，以1000的步长划分区间；对于`life_time`，则以10的步长划分。`veiws`数据数量级跨度较大，可以对其取对数；`life_time`分布比较均匀，不用额外处理。

```python
	if (attribute == 'view'):
        
        count_dict = {}
        
        for node in node_info:
            
            views = int(node['views']) // 1000 + 0.5
            if views in count_dict: count_dict[views] += 1
            else: count_dict[views] = 1
        
        count_list = sorted(count_dict.items())
        
        count = [l[1] for l in count_list]
        view_value = [np.log10(l[0]) for l in count_list]
        plt.scatter(view_value, count, s = 2, c = 'lightcoral')
        
        
        x_smooth = np.linspace(min(view_value), max(view_value), 60)
        y_smooth = make_interp_spline(view_value, count)(x_smooth)
        plt.plot(x_smooth, y_smooth, c = 'b')
        
        plt.xlabel('Log(views)')
        plt.ylabel('Frequency')
```

![view](images\view.png)

```python
    if (attribute == 'life_time'):
        
        count_dict = {}
        for node in node_info:
            life = int(node['life_time']) // 10
            if life in count_dict: count_dict[life] += 1
            else: count_dict[life] = 1
        count_dict = sorted(count_dict.items())
        
        count = [l[1] for l in count_dict]
        lifetime = [l[0] for l in count_dict]
        plt.scatter(lifetime, count, s = 2, c = 'lightcoral')
        
        fit = np.polyfit(lifetime, count, 3)
        fit_func = np.poly1d(fit)
        fit_val = fit_func(lifetime)
        plt.plot(lifetime, fit_val, 'b')
        
        plt.xlabel('Life-time / 10')
        plt.ylabel('Frequency')
```

![life_time](images\life_time.png)

## 主函数调用

```python
import csv
import sys	#添加系统路径
sys.path.append('D:/HUAWEI/Documents/all_code/Python')

from GraphStat import *

NOD = 10000 #测试数据规模

Nodes_path = 'Data/twitch_gamer/large_twitch_features.csv'
Edge_path = 'Data/twitch_gamer/large_twitch_edges.csv'

def main():
    nodes_info = node.init_node(Nodes_path)[:]
    with open(Edge_path, 'r', encoding = 'utf-8') as in_file:
        print('Reading ' + Edge_path + '...')
        edges = list(csv.reader(in_file))[1:]
    net_graph = graph.init_graph(len(nodes_info), edges)
    net_matrix = graph.save_graph(len(nodes_info), edges)
    # graph.load_graph(net_matrix, 'Netmatrix.txt')
    stat.cal_views_distribution(nodes_info)
    stat.cal_degree_distribution(net_graph)
    
    visual.plot_nodes_attr(net_graph, nodes_info, 'view')
    visual.plot_nodes_attr(net_graph, nodes_info, 'mature')
    visual.plot_nodes_attr(net_graph, nodes_info, 'affiliate')
    visual.plot_nodes_attr(net_graph, nodes_info, 'life_time')
    visual.plot_nodes_attr(net_graph, nodes_info, 'language')
    visual.plot_nodes_attr(net_graph, nodes_info, 'degree')
    while 1: 
        print('Enter a center node:')
        visual.plot_ego(net_graph, int(input()))  #79382 10101 10110 589 830 6761 48372 #37811

main()
```

## 思考

观察节点的度分布及局部网络结构，可以找到一些邻居节点非常多，远高于平均值的节点。在网络中进行营销时，可以挑选此类节点，依托其大量的节点交流迅速扩大影响力。

衡量节点重要性的指标主要有**度中心性**、**介数中心性**、**接近中心性**、**特征向量中心性**等。其关键是分析从该节点出发向其他节点传播的难易程度。