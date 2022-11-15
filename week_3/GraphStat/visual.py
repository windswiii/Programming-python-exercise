import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy.interpolate import make_interp_spline


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

def plot_nodes_attr(graph, node_info, attribute):
    '''
    绘制节点属性的统计结果
    '''
    plt.rcParams['figure.figsize']= (9, 6)
    
    # mature / affiliate
    if (attribute == 'mature') or (attribute == 'affiliate'):
        
        count = [0, 0]
        for node in node_info:
            count[int(node[attribute])] += 1
        plt.bar(range(2), count, width = 0.5, tick_label = ['False', 'True'], color = ['lightcoral', 'yellowgreen'])
    
    # views
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
    
    # life_time
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
    
    #language
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
        
    #degree
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
    
    plt.title(attribute.capitalize())
    plt.savefig('result/' + attribute + '.png')
    plt.show()