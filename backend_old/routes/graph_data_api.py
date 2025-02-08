from flask import Blueprint, current_app, jsonify, request
import json
import pandas as pd
import networkx as nx
from backend.services.data_loader import load_data
from backend.services.instnRelationGraph import generateGraphData
from backend.services.transaction_graph import construct_graph, calculate_degree, construct_graph
from backend.services.graph_data import data_preprocessing, find_max_total_volume_by_type, graph_nodes_info, \
    build_graph, filterByTransactionNum

graph_data_bp = Blueprint('graph_data', __name__)

def get_or_load_data(query_date):
    cache = current_app.config['cache']
    
    # Check if data is cached
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    # If any of the data is not cached, load it and cache it
    if (df_MarketPrice is None or df_transaction is None or instn_base_info is None or df_chain_data is None or instn_dict is None or
        df_MarketPrice.empty or df_transaction.empty or instn_base_info.empty or df_chain_data.empty or not instn_dict):
        df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = load_data(query_date)
        cache.set('df_MarketPrice', df_MarketPrice)
        cache.set('df_transaction', df_transaction)
        cache.set('instn_base_info', instn_base_info)
        cache.set('df_chain_data', df_chain_data)
        cache.set('instn_dict', instn_dict)
    
    return df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict

@graph_data_bp.route('/graph_data/<string:bond_cd>/<string:the_instn_cd>', methods=['POST','GET'])
def get_graph_data(bond_cd, the_instn_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)

    filtered_json_transaction = data_preprocessing(bond_cd, df_transaction, instn_dict)
    volume_threshold = 50
    unique_instn_cd = set()
    links = []

    for index, row in filtered_json_transaction.iterrows():
        source = str(row['byr_instn_cd'])
        target = str(row['slr_instn_cd'])
        volume = row['nmnl_vol']
        price = row['net_prc']
        if source == str(the_instn_cd) or target == str(the_instn_cd):
            if volume > volume_threshold:
                links.append({"source": source, "target": target, "volume": volume, "price": price})
                unique_instn_cd.add(source)
                unique_instn_cd.add(target)

    nodes = []
    for instn_cd in unique_instn_cd:
        transaction_count = sum(1 for link in links if link["source"] == instn_cd or link["target"] == instn_cd)
        if transaction_count >= 0:
            value = instn_dict[int(instn_cd)]
            instn_cn_full_nm = value["instn_cn_full_nm"]
            instn_tp = value["instn_tp"]
            nodes.append({"id": instn_cd, "name": instn_cn_full_nm, "instn_tp": instn_tp})
    
    result_dict = {"nodes": nodes, "links": links, "bond_cd": bond_cd, "instn_cd": str(the_instn_cd)}
    All_node_info = graph_nodes_info(bond_cd, df_transaction, instn_dict)
    for node in nodes:
        id = node["id"]
        node["node_global_info"] = All_node_info[id]

    result_dict["statistics_info"] = find_max_total_volume_by_type(All_node_info)
    return jsonify(result_dict)

@graph_data_bp.route('/get_global_graph_data/<string:bond_cd>', methods=['POST','GET'])
def get_all_graph_data(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    
    the_bond_data = data_preprocessing(bond_cd, df_transaction, instn_dict)
    filtered_data = filterByTransactionNum(the_bond_data, min_transactions=3)
    G = build_graph(filtered_data)
    cycles = list(nx.simple_cycles(G))
    unique_nodes = set(node for cycle in cycles for node in cycle)

    links = []
    for _, row in the_bond_data.iterrows():
        source = row['byr_instn_cd']
        target = row['slr_instn_cd']
        volume = row['nmnl_vol']
        price = row['net_prc']
        time = row['dl_tm']
        if (source in unique_nodes) and (target in unique_nodes):
            links.append({"source": source, "target": target, "volume": volume, "price": price, "time": time})

    nodes = []
    for instn_cd in unique_nodes:
        value = instn_dict[int(instn_cd)]
        instn_cn_full_nm = value["instn_cn_full_nm"]
        instn_tp = value["instn_tp"]
        nodes.append({"id": instn_cd, "name": instn_cn_full_nm, "instn_tp": instn_tp})

    result_dict = {"nodes": nodes, "links": links, "bond_cd": bond_cd}
    return jsonify(result_dict)

@graph_data_bp.route('/get_transaction_chains/<int:month>', methods=['POST','GET'])
def get_transaction_chains(month):
    df = pd.read_csv('server/static/chain_data/bond_2005496_2006_2402.csv')
    header_string = "dl_cd,txn_dt,dl_tm,bsns_tm,bond_cd,bnds_nm,net_prc,yld_to_mrty,nmnl_vol,amnt,acrd_intrst,totl_acrd_intrst,all_prc,stlmnt_amnt,stlmnt_dt,ttm_yrly,byr_qt_cd,byr_instn_cd,byr_cfets_instn_cd,byr_instn_cn_full_nm,byr_instn_cn_shrt_nm,byr_instn_en_shrt_nm,byr_trdr_nm,byr_adrs,byr_trdr_fax,byr_lgl_rprsntv,byr_trdr_tel,buy_side_trdng_acnt_cd,byr_cptl_bnk_nm,byr_cptl_acnt_no,byr_pymnt_sys_cd,byr_dpst_acnt_nm,buy_side_dpst_cd,byr_trd_acnt_cfets_cd,byr_trd_acnt_cn_full_nm,byr_trd_acnt_cn_shrt_nm,byr_trd_acnt_en_shrt_nm,byr_cptl_acnt_nm,byr_trd_acnt_en_full_nm,slr_qt_cd,slr_instn_cd,slr_cfets_instn_cd,slr_instn_cn_full_nm,slr_instn_cn_shrt_nm,slr_instn_en_shrt_nm,slr_trdr_cd,slr_trdr_nm,slr_adrs,slr_trdr_fax,slr_lgl_rprsntv,slr_trdr_tel,sell_side_trdng_acnt_cd,slr_cptl_bnk_nm,slr_cptl_acnt_no,slr_pymnt_sys_cd,slr_dpst_acnt_nm,sell_side_dpst_acnt,slr_trd_acnt_cfets_cd,slr_trd_acnt_cn_full_nm,slr_trd_acnt_cn_shrt_nm,slr_trd_acnt_en_shrt_nm,slr_cptl_acnt_nm,slr_trd_acnt_en_full_nm,crt_tm,upd_tm"
    # 使用split()方法将字符串转换为列表
    header_list = header_string.split(',')
    df = df[header_list]
    df['dl_tm'] = pd.to_datetime(df['dl_tm'])
    df['month'] = df['dl_tm'].dt.month

    # 根据不同的月份进行筛选
    def filter_by_month(data, month):
        return data[data['month'] == month]

    target_month = month  # 选择三月份的数据
    df = filter_by_month(df, target_month)

    # 构建节点列表
    nodes = list(set(df['byr_instn_cn_full_nm']).union(set(df['slr_instn_cn_full_nm'])))

    # 创建链接列表
    links = []
    for index, row in df.iterrows():
        source = row['byr_instn_cn_full_nm']
        target = row['slr_instn_cn_full_nm']
        nmnl_vol = row['nmnl_vol']
        links.append({
            'source': source,
            'target': target,
            'nmnl_vol': nmnl_vol
        })
    # 生成最后的数据字典
    data_dict = {"nodes": [{"id": node} for node in nodes], "links": links}

    # 将 Python 对象转化为 JSON 字符串
    data_json = json.dumps(data_dict)
    return data_json

@graph_data_bp.route('/get_transaction_chains1', methods=['POST','GET'])
def get_transaction_chains_sample():
    """
    Get sample transaction chains data.

    Returns:
    str: JSON formatted data.
    """
    _, _, _, df_chain_data, _ = get_or_load_data()
    # print(df_chain_data)
    graph_data = construct_graph(df_chain_data)
    data_json = json.dumps(graph_data)
    return data_json

@graph_data_bp.route('/process_hovered_node', methods=['POST','GET'])
def process_hovered_node():
    # 获取前端发送的数据
    data = request.json
    graph_data = data['graph']
    hovered_node = data['hoveredNode']

    # 调用函数计算指定节点的出度和入度
    out_degree, in_degree, out_edges, in_edges = calculate_degree(graph_data, hovered_node)
    # 在这里进行相应的处理，比如根据悬浮节点进行分析或其他操作

    # 处理完成后，将处理结果返回给前端
    # 这里只是一个示例，实际情况根据具体需求进行处理
    processed_data = {
        'message': '处理成功',
        'out_degree': out_edges,
        'in_degree': in_edges,
        'graph_data': graph_data,
        'hovered_node': hovered_node
    }

    # 将处理结果以 JSON 格式返回给前端
    return jsonify(processed_data)

@graph_data_bp.route('/instnRelationGraph', methods=['POST', 'GET'])
def get_instnRelationGraph():
    if request.method == 'POST':
        try:
            # 从请求中获取JSON数据
            dataToSend = request.get_json()
            # print('Received data:', dataToSend)
            graph_data = generateGraphData(dataToSend['graph'])

            # 处理数据（这里只是一个示例，实际处理逻辑取决于你的需求）
            response_data = {
                'message': 'Data received successfully',
                'received_data': graph_data
            }

            # 返回JSON响应
            return jsonify(response_data), 200

        except Exception as e:
            print('Error:', e)
            return jsonify({'error': 'Failed to process the request'}), 400

    return jsonify({'message': 'This endpoint only supports POST requests'}), 405
