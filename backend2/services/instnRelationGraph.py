import networkx as nx
import pandas as pd

def load_data(csvdata):
    #将传来的json转为dataframe
    df = pd.DataFrame(csvdata)
    df = df.rename(columns={'byr_instn_cn_full_nm':'buyer','slr_instn_cn_full_nm':"seller", 'transactionVolume': 'volume', 'netPrice': "price", 'timeStamp': "date"})
    return df

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
        transaction_id = transaction["transactionId"]
        edge_attributes = {"buyer": buyer, "seller": seller, "volume": volume, "price": price, "time": time}
        G.add_edge(seller, buyer, key=transaction_id , **edge_attributes)
    return G

def calculate_position_and_trades(name, merged_df):
    transactions = merged_df[(merged_df['seller'] == name) | (merged_df['buyer'] == name)]
    # print(transactions)
    buy_transactions = transactions[transactions['buyer'] == name].sort_values(by='date').reset_index(drop=True)
    sell_transactions = transactions[transactions['seller'] == name].sort_values(by='date').reset_index(drop=True)

    # 记录交易次数的计数器
    trade_count = buy_transactions.shape[0] + sell_transactions.shape[0]
    # print(buy_transactions.shape[0], sell_transactions.shape[0])
    # print(sum(buy_transactions['volume']), sum(sell_transactions['volume']))

    def dp(buy_idx, sell_idx, remaining_buy, remaining_sell):
        nonlocal trade_count  # 使用nonlocal关键字引用外部的trade_count变量
        if buy_idx >= len(buy_transactions) or sell_idx >= len(sell_transactions):
            return remaining_buy - remaining_sell

        # 计算当前买入和卖出交易的抵消量
        offset = min(buy_transactions.loc[buy_idx]['volume'], sell_transactions.loc[sell_idx]['volume'])

        # 更新剩余买入和卖出交易量
        remaining_buy -= offset
        remaining_sell -= offset

        # 更新买入和卖出交易的索引
        next_buy_idx = buy_idx + (buy_transactions.loc[buy_idx]['volume'] == offset)
        next_sell_idx = sell_idx + (sell_transactions.loc[sell_idx]['volume'] == offset)

        # 统计交易次数
        trade_count += 1

        # 继续递归
        return dp(next_buy_idx, next_sell_idx, remaining_buy, remaining_sell)

    # 调用动态规划函数
    position = dp(0, 0, buy_transactions['volume'].sum(), sell_transactions['volume'].sum())
    transactions_info = {'buy_sum': sum(buy_transactions['volume']), 'sell_sum': sum(sell_transactions['volume']), 'buy_num': buy_transactions['volume'].shape[0], 'sell_num': sell_transactions['volume'].shape[0]}
    # 返回头寸和交易次数
    return position, transactions_info

def calculate_offset_profit(name, merged_df):
    transactions = merged_df[(merged_df['seller'] == name) | (merged_df['buyer'] == name)]
    buy_transactions = transactions[transactions['buyer'] == name].sort_values(by='date').reset_index(drop=True)
    sell_transactions = transactions[transactions['seller'] == name].sort_values(by='date').reset_index(drop=True)

    offset_profit = 0
    i = 0
    j = 0
    while i < len(buy_transactions) and j < len(sell_transactions):
        if buy_transactions['volume'][i] == sell_transactions['volume'][j]:
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

def generateGraphData(csvdata):
  # 假设 df 是你的 DataFrame，包含交易数据
  df = load_data(csvdata)
  # G = create_directed_graph(df)
  buyer_seller_names = set(df['buyer']).union(set(df['seller']))
  trader_transactions = list(buyer_seller_names)

  nodes = []
  links = []

  for name in trader_transactions:
      position, transactions_info = calculate_position_and_trades(name, df)
      profit = calculate_offset_profit(name, df)
      # 添加节点信息
      nodes.append({
          "id": name,
          "position": int(position),
          "transactions_info": transactions_info,
          "profit": float(profit)
      })

  # 构建边（链接）
  for index, row in df.iterrows():
      links.append({
          "source": row['buyer'],
          "target": row['seller'],
          # "value": row['transaction_value']  # 假设有交易值字段
      })

  # 创建图数据
  graph_data = {
      "nodes": nodes,
      "links": links
  }
  return graph_data
