import numpy as np
def convert_trades_to_chains(trades):
    chains = []
    current_seller = trades.path[0].seller
    inst_instance = {"name": current_seller, "time_dl": trades.path[0].time_dl, "volume": trades.path[0].volume, "price": trades.path[0].price}
    chains.append(inst_instance)
    for trade in trades.path:
        buyer = trade.buyer
        inst_instance = {"name": buyer, "time_dl": trade.time_dl, "volume": trade.volume, "price": trade.price}
        chains.append(inst_instance)
    return chains

def calculate_min_max_timestamp(sorted_paths):
    # 初始化最小和最大时间戳
    min_timestamp = None
    max_timestamp = None

    # 遍历所有路径
    for path in sorted_paths:
        # 遍历每个路径中的交易
        for trade in path.path:
            # 获取交易时间戳
            timestamp = trade.time_dl
            # 更新最小时间戳
            if min_timestamp is None or timestamp < min_timestamp:
                min_timestamp = timestamp
            # 更新最大时间戳
            if max_timestamp is None or timestamp > max_timestamp:
                max_timestamp = timestamp

    return min_timestamp, max_timestamp

def generate_node_name_feature(all_path_list, method='mean'):
    # 得到所有 institution 的 set
    all_institutions = set()
    for path in all_path_list:
        all_institutions.update(path)
    
    # 根据 institution 数量构造随机向量，每个向量代表一个 institution 的特征
    # 这里假设特征向量的维度是固定的，可以根据需要进行调整
    feature_dim = 100
    institution_features = {}
    for institution in all_institutions:
        institution_features[institution] = np.random.rand(feature_dim)
    
    # 生成每个节点的特征向量，并合并每条路径的特征向量为链路的嵌入向量
    all_path_embeddings = []
    for path in all_path_list:
        path_embeddings = []
        for institution in path:
            path_embeddings.append(institution_features[institution])
        if method == 'mean':
            path_embeddings_aggregated = np.mean(path_embeddings, axis=0)
        elif method == 'concat':
            path_embeddings_aggregated = np.concatenate(path_embeddings, axis=0)
        else:
            raise ValueError("Unsupported method. Please choose 'mean' or 'concat'.")
        all_path_embeddings.append(path_embeddings_aggregated)
    
    return all_path_embeddings

def generate_x_coordinates(trades_list, y_coord, min_timestamp, max_timestamp):
    # x轴坐标是按照时间来计算的
    # 这里的y轴坐标为初始化结果
    # 计算时间范围
    time_range_seconds = (max_timestamp - min_timestamp).total_seconds()
    # print(f"Time range: {time_range_seconds}")
    # 计算时间映射到0-500之间的比例
    time_scale = 1000 / (time_range_seconds + 1)
    
    # 生成坐标列表
    xy_coordinates = []
    prev_x_coordinate = None  # 前一个 x 坐标的初始值为 None
    for trade in trades_list:
        # 计算 x 坐标
        x_coordinate_seconds = (trade['time_dl'] - min_timestamp).total_seconds()
        x_coordinate = 50 + x_coordinate_seconds * time_scale
        
        # 确保 x 坐标之间的最小距离为 10
        if prev_x_coordinate is not None:
            if x_coordinate - prev_x_coordinate < 20:
                x_coordinate = prev_x_coordinate + 20
        
        # 添加到 xy_coordinates 列表中
        xy_coordinates.append({'x': x_coordinate, 'y': y_coord})
        
        # 更新前一个 x 坐标
        prev_x_coordinate = x_coordinate

    return xy_coordinates

def insert_xy_coordinates(trades_list, xy_coordinates_list):
    for trade_list, xy_coordinates in zip(trades_list, xy_coordinates_list):
        trade_list['xy_coordinates'] = xy_coordinates
    return trades_list

def process_paths_with_interval(sorted_paths, interval):
    all_paths_with_xy = []
    min_timestamp, max_timestamp = calculate_min_max_timestamp(sorted_paths)

    for i, path in enumerate(sorted_paths):
        path_list_info = convert_trades_to_chains(path)
        path_list_info_xy = generate_x_coordinates(path_list_info, interval * i, min_timestamp, max_timestamp)
        path_list_with_xy = insert_xy_coordinates(path_list_info, path_list_info_xy)

        all_paths_with_xy.append(path_list_with_xy)

    print("All Paths with XY Coordinates:")
    for i, path_with_xy in enumerate(all_paths_with_xy):
        print(f"Path {i+1}:")
        for j, trade_list_with_xy in enumerate(path_with_xy):
            print(f"  Trade List {j+1}: {trade_list_with_xy}")

    return all_paths_with_xy
