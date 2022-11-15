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