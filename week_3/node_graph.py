import csv
import sys
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