import networkx as nx

def data_preprocessing(bond_cd, df_transaction, instn_dict):
    # Filter the data date list, market data、transaction data、valuation data
    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    df_transaction['date'] = df_transaction['txn_dt']
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    by_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    sl_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    filtered_json_transaction['amnt'] = filtered_json_transaction['net_prc'] * filtered_json_transaction['nmnl_vol']
    filtered_json_transaction['totl_acrd_intrst'] = filtered_json_transaction['acrd_intrst']
    filtered_json_transaction['stlmnt_amnt'] = filtered_json_transaction['amnt'] + filtered_json_transaction['acrd_intrst']
    filtered_json_transaction['all_price'] = filtered_json_transaction['stlmnt_amnt'] / filtered_json_transaction['nmnl_vol']
    filtered_json_transaction['byr_instn_tp'] = by_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = sl_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))

    return filtered_json_transaction

def build_graph(datadf):
    # 构建有向图
    G = nx.DiGraph()
    for _, row in datadf.iterrows():
        buyer = row['byr_instn_cd']
        seller = row['slr_instn_cd']
        if not G.has_edge(buyer, seller):
            G.add_edge(buyer, seller, transaction_info={})
    return G

def filterByTransactionNum(df_transaction, min_transactions=3):
    df_transaction.sort_values(['byr_instn_cd', 'slr_instn_cd', 'dl_tm'], inplace=True)
    df_buy_counts = df_transaction[df_transaction['byr_instn_cd'].notnull()].groupby(['byr_instn_cd', 'slr_instn_cd']).size().reset_index(name='buy_counts')
    df_sell_counts = df_transaction[df_transaction['slr_instn_cd'].notnull()].groupby(['slr_instn_cd', 'byr_instn_cd']).size().reset_index(name='sell_counts')

    filtered_institutions_buy = df_buy_counts[(df_buy_counts['buy_counts'] >= min_transactions)]['byr_instn_cd'].tolist()
    filtered_institutions_sell = df_sell_counts[(df_sell_counts['sell_counts'] >= min_transactions)]['slr_instn_cd'].tolist()

    filtered_institutions = df_transaction[(df_transaction['byr_instn_cd'].isin(filtered_institutions_buy)) &
                                           (df_transaction['slr_instn_cd'].isin(filtered_institutions_sell))]

    return filtered_institutions

def graph_nodes_info(bond_cd, df_transaction, instn_dict):
    node_info = {}
    filtered_json_transaction = data_preprocessing(bond_cd, df_transaction, instn_dict)
    for _, row in filtered_json_transaction.iterrows():
        source = str(row['byr_instn_cd'])
        target = str(row['slr_instn_cd'])
        volume = row['nmnl_vol']
        price = row['net_prc']
        if source not in node_info:
            node_info[source] = {
                "buyin": {"total_volume": 0, "num_transactions": 0, "prices": []}, 
                "sell": {"total_volume": 0, "num_transactions": 0, "prices": []}
            }
        node_info[source]["buyin"]["total_volume"] += volume
        node_info[source]["buyin"]["num_transactions"] += 1
        node_info[source]["buyin"]["prices"].append(price)
        if target not in node_info:
            node_info[target] = {
                "buyin": {"total_volume": 0, "num_transactions": 0, "prices": []},
                "sell": {"total_volume": 0, "num_transactions": 0, "prices": []}
            }
        node_info[target]["sell"]["total_volume"] += volume
        node_info[target]["sell"]["num_transactions"] += 1
        node_info[target]["sell"]["prices"].append(price)
    return node_info

def find_max_total_volume_by_type(node_info):
    max_total_volume_buyin = 0
    max_total_volume_sell = 0
    for _, info in node_info.items():
        total_volume_buyin = info["buyin"]["total_volume"]
        if total_volume_buyin > max_total_volume_buyin:
            max_total_volume_buyin = total_volume_buyin
        total_volume_sell = info["sell"]["total_volume"]
        if total_volume_sell > max_total_volume_sell:
            max_total_volume_sell = total_volume_sell
    return {
        "max_total_volume_buyin": max_total_volume_buyin,
        "max_total_volume_sell": max_total_volume_sell
    }
