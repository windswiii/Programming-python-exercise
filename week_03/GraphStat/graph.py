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