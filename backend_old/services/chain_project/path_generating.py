# import pandas as pd
# import numpy as np
import networkx as nx
# import matplotlib.pyplot as plt
from collections import defaultdict

def create_directed_graph(data):
    """
    根据数据创建一个多重有向图。
    Args:
        data (DataFrame): 数据帧，包含交易信息。

    Returns:
        nx.MultiDiGraph: 多重有向图对象。
    """
    G = nx.MultiDiGraph()
    # 添加节点和边
    for _, transaction in data.iterrows():
        buyer = transaction["buyer"]
        seller = transaction["seller"]
        volume = transaction["volume"]
        price = transaction["price"]
        time = transaction["date"]
        time_dl = transaction["date_dl"]
        edge_attributes = {"buyer": buyer, "seller": seller, "volume": volume, "price": price, "time": time, "time_dl": time_dl}
        G.add_edge(seller, buyer, key=time_dl , **edge_attributes)
    return G

def validate_path(path):
    """
    验证路径的可行性
    Args:
        G (nx.MultiDiGraph): 多重有向图对象
        path (list): 要验证的路径，其中每个元素是一个三元组 (source, target, key)

    Returns:
        bool: 如果路径有效，则返回True；否则返回False。
    """
    # 如果路径为空，直接返回False
    if not path:
        return False

    prev_key = None
    for edge in path:
        _, _, key = edge
        if prev_key is not None and key <= prev_key:
            return False
        prev_key = key
    
    return True

def find_all_paths(G, cutoff=None):
    """
    查找图中所有节点对之间的路径。
    Args:
        G (nx.MultiDiGraph): 多重有向图对象。

    Returns:
        dict: 包含所有路径的字典，键为节点对，值为路径列表。
    """
    nodes = list(G.nodes())
    all_paths = defaultdict(list)
    for source_node in nodes:
        for target_node in nodes:
            if source_node == target_node:
                continue
            paths = list(nx.all_simple_edge_paths(G, source=source_node, target=target_node, cutoff=cutoff))
            valid_paths = [path for path in paths if validate_path(path)]
            all_paths[(source_node, target_node)] = valid_paths

    return dict(all_paths)

def print_paths_with_transaction_time(all_paths):
    # 遍历所有路径
    for node_pair, paths in all_paths.items():
        source, target = node_pair
        # 遍历每个路径
        for path in paths:
            # 检查路径是否为空
            if not path:
                continue
            # 输出路径
            print(f"从 {source} 到 {target} 的路径：{path}")

# def visualize_graph(G):
#     # 可视化有向图
#     plt.figure(figsize=(10, 6))
#     pos = nx.spring_layout(G)
#     nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, arrows=True)
#     plt.title('Directed Graph')
#     plt.show()

