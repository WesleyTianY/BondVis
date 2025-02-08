import pandas as pd
import numpy as np
import json
# from sklearn.cluster import DBSCAN
# from sklearn.preprocessing import StandardScaler
# from sklearn.impute import SimpleImputer
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import MinMaxScaler, StandardScaler
# from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import networkx as nx
from collections import Counter

def preprocession(df):
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)

    # 加载数据
    # 将交易时间列转换为 datetime 对象
    df['dl_tm'] = pd.to_datetime(df['dl_tm'])

    # 提取月份信息
    df['month'] = df['dl_tm'].dt.month
    df['year'] = df['dl_tm'].dt.year
    df['day'] = df['dl_tm'].dt.day
    df['hour'] = df['dl_tm'].dt.hour

    # 将年份、月份和日期连起来，并确保月份和日期值为两位数
    df['year_month_day'] = df['year'].astype(str) + '-' + df['month'].apply(lambda x: '{:02d}'.format(x)) + '-' + df['day'].apply(lambda x: '{:02d}'.format(x))+ '-' + df['hour'].apply(lambda x: '{:02d}'.format(x))

    # df['time'] = df['month'].cat(df['year'].str, sep=',')
    # 将字符串列转换为字符串类型
    df['byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].astype(str)
    df['slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].astype(str)
    df['byr_trdr_nm'] = df['byr_trdr_nm'].astype(str)
    df['slr_trdr_nm'] = df['slr_trdr_nm'].astype(str)

    # 将购买和销售机构合并为一个列
    df['instn'] = df['byr_instn_cn_full_nm'].str.cat(df['slr_instn_cn_full_nm'], sep=',')

    # 计算每个月每个机构的交易次数
    # result = df.groupby(['month', 'instn',"nmnl_vol","net_prc"]).size()
    df['byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].str[:6].str.cat(df['byr_trdr_nm'], sep='')
    df['slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].str[:6].str.cat(df['slr_trdr_nm'], sep='')
    df['byr_trdr_nm'] = df['byr_trdr_nm']
    df['slr_trdr_nm'] = df['slr_trdr_nm']
    df['nmnl_vol'] = np.int64(df["nmnl_vol"]/10000000)
    df['net_prc'] = (df["net_prc"]).round(2)

    # 计算每个月每个机构的交易次数
    # result = df.groupby(['year_month_day', 'byr_instn_cn_full_nm', 'slr_instn_cn_full_nm', 'nmnl_vol', 'net_prc', 'byr_trdr_nm', 'slr_trdr_nm']).size().reset_index(name='transaction_count')

    result = df[['dl_tm', 'stlmnt_dt', 'byr_instn_cn_full_nm', 'slr_instn_cn_full_nm', 'nmnl_vol', 'net_prc']]

    # 重命名列以使其更易读
    result = result.rename(columns={"stlmnt_dt" :'date','byr_instn_cn_full_nm':'buyer','slr_instn_cn_full_nm':"seller",  'instn': 'Institution', 'nmnl_vol': 'volume', 'net_prc': "price"})

    # 将结果导出为 CSV 文件
    # result.to_csv('transaction_summary.csv', index=False)
    return result

def merge_transactions(df, window=3):
    # 将日期转换为 datetime 对象
    df['date'] = pd.to_datetime(df['date'])

    # 根据日期和其他关键列对数据进行排序
    df = df.sort_values(by=['date', 'buyer', 'seller'])
    merged_transactions = []
    current_transaction = None
    
    for _, row in df.iterrows():
        if current_transaction is None:
            current_transaction = row
            continue
        
        if (row['date'] - current_transaction['date']).days <= window:
            if row['buyer'] == current_transaction['buyer'] and row['seller'] == current_transaction['seller'] and row['price'] == current_transaction['price']:
                current_transaction['volume'] += row['volume']
            else:
                merged_transactions.append(current_transaction)
                current_transaction = row
        else:
            merged_transactions.append(current_transaction)
            current_transaction = row
            
    if current_transaction is not None:
        merged_transactions.append(current_transaction)
    
    return pd.DataFrame(merged_transactions)

def calculate_prices_list(df):
    # 获取买家和卖家的价格列表
    buyer_prices = df.groupby('buyer')['price'].apply(list).to_dict()
    seller_prices = df.groupby('seller')['price'].apply(list).to_dict()

    # 合并买家和卖家的价格列表
    from collections import defaultdict
    institution_prices = defaultdict(list)

    for d in (buyer_prices, seller_prices):
        for key, value in d.items():
            institution_prices[key].extend(value)

    return dict(institution_prices)

def calculate_statistics(price_list):

    var = np.var(price_list) if len(price_list) > 1 else 0
    range_ = np.max(price_list) - np.min(price_list)

    return {
        "Variance": var,
        "Range": range_
    }

def determine_market_maker(name, market_makers_list):
    if name in market_makers_list:
        return True
    else:
        return False

def calculate_trader_stats(name, merged_df):
    offset_volume, offset_count = calculate_offset_trades(name, merged_df)
    offset_profit = calculate_offset_profit(name, merged_df)
    # 计算盈利百分比
    # print(offset_profit, offset_volume)
    profit_percentage = (offset_profit / offset_volume) * 100
    return {'offset_profit': offset_profit, 'profit_percentage': profit_percentage, 'offset_volume': int(offset_volume/offset_count), 'offset_count': offset_count}

def normalize_statistics(G):
    # 计算每个属性的最小值和范围
    stats_keys = next(iter(G.nodes.values()))['statistics'].keys()  # 获取统计信息的键
    min_values = {key: min(node['statistics'][key] for node in G.nodes.values()) for key in stats_keys}
    max_values = {key: max(node['statistics'][key] for node in G.nodes.values()) for key in stats_keys}

    # 初始化节点的归一化统计信息
    for node in G.nodes.values():
        node['normalized_statistics'] = {}

    # 归一化统计信息
    for node in G.nodes.values():
        for key in stats_keys:
            value = node['statistics'][key]
            min_value = min_values[key]
            max_value = max_values[key]
            normalized_value = (value - min_value) / (max_value - min_value) if max_value != min_value else 0
            node['normalized_statistics'][key] = normalized_value

def construct_graph(df):
    df = preprocession(df)
    # 执行合并逻辑
    merged_df = merge_transactions(df)
    institution_prices = calculate_prices_list(merged_df)
    market_makers_list = identify_market_makers(merged_df, time_window=1, max_price_difference=0.1, matching_ratio_threshold=0.9, trader_count_threshold=5)
    # 创建有向图
    G = nx.DiGraph()
    # 添加边到图中，并记录获利
    for _, row in merged_df.iterrows():
        G.add_edge(row['seller'], row['buyer'], volume=row['volume'], price=row['price'])
    # 计算每一个机构的价格列表的统计信息，作为节点的属性添加到图中
    for name, price_list in dict(institution_prices).items():
        stats = calculate_statistics(price_list)
        is_market_maker = determine_market_maker(name, market_makers_list)  # 判断是否是做市商
        stats['is_market_maker'] = is_market_maker
        G.nodes[name]['statistics'] = stats
    # 计算每个交易员的统计信息，并添加到图中
    trader_transactions = set(merged_df['buyer']).union(set(merged_df['seller']))
    for name in trader_transactions:
        trader_stats = calculate_trader_stats(name, merged_df)
        G.nodes[name]['trader_stats'] = trader_stats
    # 归一化统计信息
    normalize_statistics(G)
    graph_data = nx.json_graph.node_link_data(G)
    return graph_data

def calculate_degree(graph_data, node_id):
    # 初始化入度和出度计数器
    in_degree = 0
    out_degree = 0

    # 初始化存储出边和入边的列表
    out_edges = []
    in_edges = []

    # 遍历每条边，统计入度和出度，并记录出边和入边
    for link in graph_data["links"]:
        # print(link)
        if link["source"]["id"] == node_id:
            out_degree += 1
            out_edges.append((link["source"], link["target"]))
        if link["target"]["id"] == node_id:
            in_degree += 1
            in_edges.append((link["source"], link["target"]))

    # 返回结果
    return out_degree, in_degree, out_edges, in_edges

def identify_market_makers(transactions, time_window, max_price_difference, matching_ratio_threshold, trader_count_threshold):
    market_makers = set()

    trader_transactions = {}  # 存储每个交易者的所有交易

    # 根据交易者分组
    for index, transaction in transactions.iterrows():
        buyer = transaction['buyer']
        seller = transaction['seller']
        if buyer not in trader_transactions:
            trader_transactions[buyer] = []
        trader_transactions[buyer].append(transaction)
        if seller not in trader_transactions:
            trader_transactions[seller] = []
        trader_transactions[seller].append(transaction)

    # 统计每个交易者的交易次数
    trader_counts = Counter(transactions['buyer'])
    trader_counts.update(transactions['seller'])

    # 计算交易笔数排名的阈值
    trader_count_threshold = int(len(trader_counts) * 0.05)

    # 遍历每个交易者的所有交易
    for trader, transactions in trader_transactions.items():
        matching_count = 0
        total_count = len(transactions)
        large_price_difference = False  # 是否存在价格差异很大的交易

        # 检查交易者的交易次数是否超过阈值
        if trader_counts[trader] > trader_count_threshold:
            # 检查每笔交易是否有匹配的交易，并且价格差小于等于0.1
            for transaction1 in transactions:
                for transaction2 in transactions:
                    if abs((transaction2['date'] - transaction1['date']).days) <= time_window:
                        price_difference = abs(transaction1['price'] - transaction2['price'])
                        if price_difference > max_price_difference:
                            large_price_difference = True
                        elif transaction1['volume'] == transaction2['volume']:
                            matching_count += 1
                            break  # 匹配到一笔交易就跳出内层循环

            # 计算匹配比例
            matching_ratio = matching_count / total_count

            # 如果价格差异很大，或者匹配比例不满足条件，则排除该交易者
            if not large_price_difference and matching_ratio >= matching_ratio_threshold:
                market_makers.add(trader)

    return market_makers

def calculate_offset_profit(name, merged_df):
    transactions = merged_df[(merged_df['seller'] == name) | (merged_df['buyer'] == name)]
    buy_transactions = transactions[transactions['buyer'] == name].sort_values(by='date').reset_index(drop=True)
    sell_transactions = transactions[transactions['seller'] == name].sort_values(by='date').reset_index(drop=True)

    offset_profit = 0
    i = 0
    j = 0
    while i < len(buy_transactions) and j < len(sell_transactions):
        if abs((buy_transactions['date'][i] - sell_transactions['date'][j]).days) > 4:
            if buy_transactions['date'][i] > sell_transactions['date'][j]:
                j += 1
            else:
                i += 1
        elif buy_transactions['volume'][i] == sell_transactions['volume'][j]:
            offset_profit += (sell_transactions['price'][j] - buy_transactions['price'][i]) * buy_transactions['volume'][i]
            # print(sell_transactions['date'][j], sell_transactions['price'][j] - buy_transactions['price'][i])
            sell_transactions = sell_transactions.drop(j).reset_index(drop=True)
            i += 1
        elif buy_transactions['volume'][i] < sell_transactions['volume'][j]:
            offset_profit += (sell_transactions['price'][j] - buy_transactions['price'][i]) * buy_transactions['volume'][i]
            # print(sell_transactions['date'][j], sell_transactions['price'][j] - buy_transactions['price'][i])
            sell_transactions.at[j, 'volume'] -= buy_transactions['volume'][i]
            i += 1
        else:
            offset_profit += (sell_transactions['price'][j] - buy_transactions['price'][i]) * sell_transactions['volume'][j]
            # print(sell_transactions['date'][j], sell_transactions['price'][j] - buy_transactions['price'][i])
            buy_transactions.at[i, 'volume'] -= sell_transactions['volume'][j]
            j += 1

    return offset_profit

def calculate_offset_trades(name, merged_df):
    # 在函数内部计算全局的平均头寸
    total_volume = merged_df['volume'].sum()
    total_count = len(merged_df)
    global_average_position = total_volume / total_count

    transactions = merged_df[(merged_df['seller'] == name) | (merged_df['buyer'] == name)]
    buy_transactions = transactions[transactions['buyer'] == name].sort_values(by='date').reset_index(drop=True)
    sell_transactions = transactions[transactions['seller'] == name].sort_values(by='date').reset_index(drop=True)

    offset_volume = 0
    offset_count = 0  # 新增的相消计数器

    if len(buy_transactions) == 0 or len(sell_transactions) == 0:
        # 如果没有足够的交易数据进行对冲，将单笔头寸设置为全局的平均头寸，将对冲次数设置为1
        if len(buy_transactions) == 0:
            offset_volume = sell_transactions['volume'].mean() if not sell_transactions.empty else 0
        elif len(sell_transactions) == 0:
            offset_volume = buy_transactions['volume'].mean() if not buy_transactions.empty else 0
        offset_count = 1
        return offset_volume, offset_count  

    i = 0
    j = 0
    while i < len(buy_transactions) and j < len(sell_transactions):
        if abs((buy_transactions['date'][i] - sell_transactions['date'][j]).days) > 4:
            if buy_transactions['date'][i] > sell_transactions['date'][j]:
                j += 1
            else:
                i += 1
        elif buy_transactions['volume'][i] == sell_transactions['volume'][j]:
            offset_volume += buy_transactions['volume'][i]
            sell_transactions = sell_transactions.drop(j).reset_index(drop=True)
            offset_count += 1  # 相消发生时增加计数
            i += 1
        elif buy_transactions['volume'][i] < sell_transactions['volume'][j]:
            sell_transactions.at[j, 'volume'] -= buy_transactions['volume'][i]
            offset_volume += buy_transactions['volume'][i]
            offset_count += 1  # 相消发生时增加计数
            i += 1
        else:
            buy_transactions.at[i, 'volume'] -= sell_transactions['volume'][j]
            offset_volume += sell_transactions['volume'][j]
            offset_count += 1  # 相消发生时增加计数
            j += 1
    # 如果对冲交易额为零，将单笔头寸设置为该交易员买入或卖出volume的平均值
    if offset_volume < 0.01:
        mean_volume = merged_df[(merged_df['seller'] == name) | (merged_df['buyer'] == name)]['volume'].mean()
        offset_volume = mean_volume if not np.isnan(mean_volume) else 0
        offset_count = 1  # 避免除零错误
    return offset_volume, offset_count  # 返回相消总量和相消次数
