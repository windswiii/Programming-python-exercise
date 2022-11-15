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