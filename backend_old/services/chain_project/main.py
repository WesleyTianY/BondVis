from chain_project.chain_preprocess import preprocess_data, load_data_test, transactions_filter
from chain_project.path_generating import create_directed_graph, find_all_paths
from chain_project.path_linking import process_all_paths
from chain_project.path_filtering import filter_subsets

def process_transactions(file_path, inst_list):
    """
    处理交易数据并返回过滤后的路径。

    Args:
    - file_path (str): 交易数据文件路径
    - inst_list (list): 机构名称列表

    Returns:
    - sorted_paths (list): 过滤后的路径列表
    """
    # 加载并预处理数据
    df = load_data_test(file_path)
    merged_df = preprocess_data(df)
    
    # 筛选并排序交易数据
    sorted_data = transactions_filter(merged_df, inst_list).sort_values(by='date_dl')

    # 创建有向图
    G_sorted_data = create_directed_graph(sorted_data)

    # 查找所有通路
    all_paths = find_all_paths(G_sorted_data, cutoff=10)

    # 处理路径组合
    the_connected_paths = process_all_paths(G_sorted_data, all_paths)

    # 过滤路径
    sorted_paths = filter_subsets(the_connected_paths)

    return sorted_paths
