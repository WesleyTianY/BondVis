import json
import os
import numpy as np
import pandas as pd
from flask import Blueprint, current_app, jsonify, request
from backend.services.data_loader import load_data
from backend.services.data_processor import get_summary, iterrowsData, getSummaryByBondList
# from backend.services.sql import pg_select
bond_bp = Blueprint('bond', __name__)

def get_or_load_data(query_date):
    cache = current_app.config['cache']
    
    # 检查缓存中的数据和日期
    cache_date = cache.get('date')
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    df_valuation = cache.get('df_valuation')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')

    # 如果缓存数据不完整、为空，或者缓存日期与请求日期不一致，则重新加载数据
    if (cache_date != query_date or 
        df_MarketPrice is None or df_transaction is None or df_valuation is None or
        instn_base_info is None or df_chain_data is None or instn_dict is None or
        df_MarketPrice.empty or df_transaction.empty or df_valuation.empty or
        instn_base_info.empty or df_chain_data.empty or not instn_dict):
        
        df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = load_data(query_date)
        cache.set('date', query_date)
        cache.set('df_MarketPrice', df_MarketPrice)
        cache.set('df_transaction', df_transaction)
        cache.set('df_valuation', df_valuation)
        cache.set('instn_base_info', instn_base_info)
        cache.set('df_chain_data', df_chain_data)
        cache.set('instn_dict', instn_dict)

    return df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict


# 2024.11.8
def get_or_load_data_old(query_date):
    cache = current_app.config['cache']
    
    # Check if data is cached
    cache_date = cache.get('date')
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    df_valuation = cache.get('df_valuation')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')
    # query_date = '2023-7-5'
    # print(df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict)
    # Check if any of the DataFrames are not cached or empty
    if (df_MarketPrice is None or df_transaction is None or instn_base_info is None or df_chain_data is None or instn_dict is None or
        df_MarketPrice.empty or df_transaction.empty or df_valuation.empty or instn_base_info.empty or df_chain_data.empty or not instn_dict):
        df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = load_data(query_date)
        cache.set('df_MarketPrice', df_MarketPrice)
        cache.set('df_transaction', df_transaction)
        cache.set('df_valuation', df_valuation)
        cache.set('instn_base_info', instn_base_info)
        cache.set('df_chain_data', df_chain_data)
        cache.set('instn_dict', instn_dict)

    return df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict

# 2024.11.7
@bond_bp.route('/set_query_date', methods=['POST','GET'])
def set_query_date():
    data = request.get_json()
    if not data or 'query_date' not in data:
        return jsonify({"error": "Missing query_date parameter"}), 400
    query_date = data['query_date']
    if os.environ['FLASK_CONFIG'] == 'local':
        print("os.environ['FLASK_CONFIG']", os.environ['FLASK_CONFIG'] == 'local')
        query_date = "2023-7-5"
    cache = current_app.config['cache']
    cache.set('query_date', query_date)
    return jsonify({"message": "query_date set successfully"}), 200

@bond_bp.route('/bondSummaryData_ByBond_cd/<string:bond_cd>', methods=['POST','GET'])
def get_bond_summary_data_ByBond_cd(bond_cd):
    try:
        cache = current_app.config['cache']
        query_date = cache.get('query_date')
        if not query_date:
            return jsonify({"error": "Missing date parameter"}), 400
        df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
        bond_summary_data = getSummaryByBondList(bond_cd, df_transaction)
        
        print('bond_summary_data 93:', bond_cd, bond_summary_data)
        return jsonify({'bondSummaryData': bond_summary_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bond_bp.route('/bondSummaryData', methods=['POST','GET'])
def get_bond_summary_data():
    try:
        cache = current_app.config['cache']
        query_date = cache.get('query_date')
        if not query_date:
            return jsonify({"error": "Missing date parameter"}), 400
        max_bood_num = 5

        df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
        # df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
        # bond_summary_data = getSummaryByBondList(bond_cd_list, df_transaction)
        # if bond_cd_list == []:
        bond_summary_data = get_summary(max_bood_num, df_transaction)
        # print("getSummaryByBondList('240215'):",getSummaryByBondList('240215', df_transaction))
        return jsonify({'bondSummaryData': bond_summary_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bond_bp.route("/BasicData_valuation/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData_valuation(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    if df_MarketPrice.empty or df_transaction.empty:
        return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # Transaction data
    df_transaction['timeStamp'] = df_transaction['txn_dt']
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    # Update buyer and seller institution type
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    
    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type')
    return jsonify({ 'filtered_json_transaction': json_transaction })

@bond_bp.route("/BasicData_transaction/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData_transaction(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    if df_MarketPrice.empty or df_transaction.empty:
        return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # Transaction data
    df_transaction['timeStamp'] = df_transaction['txn_dt']
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    # Update buyer and seller institution type
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    
    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type')
    return jsonify({ 'filtered_json_transaction': json_transaction })

@bond_bp.route("/BasicData_transaction_rate/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData_transaction_rate(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    if df_MarketPrice.empty or df_transaction.empty:
        return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # Transaction data
    df_transaction['timeStamp'] = df_transaction['txn_dt']
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    # Update buyer and seller institution type
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    
    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type')
    return jsonify({ 'filtered_json_transaction': json_transaction })

@bond_bp.route("/BasicData_MarketPrice/<string:bond_cd>", methods=['POST','GET'])
def getTheBond_MarketPrice(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    if df_MarketPrice.empty or df_transaction.empty:
        return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # MarketPrice data
    df_MarketPrice['timeStamp'] = df_MarketPrice['dl_tm']
    # filtered_json_mkt = df_MarketPrice[df_MarketPrice['date'].isin(workday_list)]
    filtered_json_mkt = df_MarketPrice.copy()
    filtered_json_mkt = filtered_json_mkt[filtered_json_mkt['bond_cd'] == bond_cd]
    # 3. 计算 'dlt_prc' 列的均值和标准差
    mean_dlt_prc = filtered_json_mkt['dlt_prc'].mean()
    std_dlt_prc = filtered_json_mkt['dlt_prc'].std()


    filtered_json_mkt['dlt_prc'] = pd.to_numeric(filtered_json_mkt['dlt_prc'], errors='coerce')

    # 4. 剔除偏离均值10个标准差之外的数据
    filtered_json_mkt = filtered_json_mkt[np.abs(filtered_json_mkt['dlt_prc'] - mean_dlt_prc) <= 10 * std_dlt_prc]
    filtered_json = iterrowsData(filtered_json_mkt, 'marketPrice_broker')
    return jsonify({ 'filtered_json_mkt': filtered_json })

@bond_bp.route("/BasicData_Valuation/<string:bond_cd>", methods=['POST','GET'])
def getTheBond_Valuation(bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    if df_MarketPrice.empty or df_transaction.empty or df_valuation.empty:
        return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

    # MarketPrice data
    # df_valuation['timeStamp'] = df_valuation['vltn_dt']
    filtered_json_val = df_valuation.copy()
    filtered_json_val = filtered_json_val[filtered_json_val['bond_cd'] == bond_cd]
    # 3. 计算 'dlt_prc' 列的均值和标准差
    # filtered_json_val = filtered_json_val['yld_to_mrty']
    # print("filtered_json_val:", filtered_json_val)
    filtered_json_val = iterrowsData(filtered_json_val, 'valuation_type')
    return jsonify({ 'filtered_json_val': filtered_json_val })

@bond_bp.route('/bondData', methods=['POST','GET'])
def data():
    # 获取查询参数
    # bond_id = request.args.get('BondId')  # 获取 BondId 参数
    # selected_date = request.args.get('selectedDate')  # 获取 selectedDate 参数
    # print("Bond:", bond_id, selected_date)
    # 读取并筛选CSV文件中的债券数据
    df_mkt = pd.read_csv('static/bond_brk10_08.csv')

    # 筛选特定债券数据
    df_mkt_filtered_data = df_mkt[df_mkt['bond_shrt_nm'] == '24附息国债13']

    # 转换时间戳格式并去除时区信息
    df_mkt_filtered_data['timeStamp'] = pd.to_datetime(df_mkt_filtered_data['dl_tm']).dt.tz_localize(None)

    # 计算 'dlt_prc' 列的均值和标准差
    mean_dlt_prc = df_mkt_filtered_data['dlt_prc'].mean()
    std_dlt_prc = df_mkt_filtered_data['dlt_prc'].std()

    # 剔除偏离均值10个标准差之外的数据
    df_mkt_filtered_data = df_mkt_filtered_data[np.abs(df_mkt_filtered_data['dlt_prc'] - mean_dlt_prc) <= 10 * std_dlt_prc]

    # 排序数据
    df_mkt_filtered_data = df_mkt_filtered_data.sort_values(by='timeStamp', ascending=True)

    # 读取并筛选债券交易数据
    ndm_transaction_data = pd.read_csv('static/bond_dtl_10_08.csv')

    # 筛选特定债券数据
    ndm_transaction_filtered_data = ndm_transaction_data[ndm_transaction_data['bnds_nm'] == '24附息国债13']

    # 转换时间戳格式
    ndm_transaction_filtered_data['timeStamp'] = pd.to_datetime(ndm_transaction_filtered_data['dl_tm']).dt.tz_localize(None)
    ndm_transaction_filtered_data = ndm_transaction_filtered_data[ndm_transaction_filtered_data['timeStamp'].dt.date == pd.to_datetime('2024-10-08').date()]

    # 排序
    ndm_transaction_sorted_data = ndm_transaction_filtered_data.sort_values(by='timeStamp', ascending=True)

    # 创建数据字典
    data = {
        "line_chart": {
            "timeStamp": df_mkt_filtered_data['timeStamp'].astype(str).tolist(),
            "dlt_prc": df_mkt_filtered_data['dlt_prc'].tolist()
        },
        "scatter_chart": {
            "timeStamp": ndm_transaction_sorted_data['timeStamp'].astype(str).tolist(),
            "nmnl_vol": ndm_transaction_sorted_data['nmnl_vol'].tolist(),
            "yld_to_mrty": ndm_transaction_sorted_data['yld_to_mrty'].tolist()
        }
    }

    return jsonify(data)

# 原代码 mkt相关
# def getTheBond_MarketPrice(bond_cd):
#     query_date = '2023-7-5'
#     df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
#     if df_MarketPrice.empty or df_transaction.empty:
#         return jsonify({'error': 'MarketPrice or Transaction data is empty'}), 400

#     # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
#     # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
#     # workday_list = generate_workdays(start_date, end_date)
#     # workday_list = [day.isoformat() for day in workday_list]

#     # MarketPrice data
#     df_MarketPrice['date'] = df_MarketPrice['mkt_data_upd_tm'].str[:10]
#     # filtered_json_mkt = df_MarketPrice[df_MarketPrice['date'].isin(workday_list)]
#     filtered_json_mkt = df_MarketPrice.copy()
#     filtered_json_mkt = filtered_json_mkt[filtered_json_mkt['bond_cd'] == int(bond_cd)]
#     filtered_json = iterrowsData(filtered_json_mkt, 'marketPrice')
#     return jsonify({ 'filtered_json_mkt': filtered_json })

# def load_data(query_date):
#     engine = get_db_engine()

#     # 使用输入的日期动态生成 SQL 查询
#     sql_transaction = f"""
#                         SELECT *
#                         FROM dpa.cbt_dl_dtl
#                         WHERE txn_dt = '{query_date}' AND trdng_md_cd = 'NDM'
#                         LIMIT 30000
#                         """

#     query_instn_info = "SELECT * FROM InstitutionInfo"
#     query_chain_data = "SELECT * FROM ChainData"
#     query_instn_dict = "SELECT * FROM InstitutionDict"

#     # 从数据库加载数据，并转换为 Pandas DataFrame
#     df_transaction = pg_select(sql_transaction)
#     instn_base_info = pd.read_sql(query_instn_info, engine)
#     df_chain_data = pd.read_sql(query_chain_data, engine)
#     instn_dict = pd.read_sql(query_instn_dict, engine)

#     # 将字典转换为你需要的格式
#     instn_dict = {row['instn_cd']: row for _, row in instn_dict.iterrows()}

#     return df_transaction, instn_base_info, df_chain_data, instn_dict

# def load_data(start_date, end_date):
#     engine = get_db_engine()

#     # 使用时间区间动态生成 SQL 查询
#     sql_transaction = f"""
#                         SELECT *
#                         FROM dpa.cbt_dl_dtl
#                         WHERE txn_dt BETWEEN '{start_date}' AND '{end_date}'
#                         AND trdng_md_cd = 'NDM'
#                         LIMIT 30000
#                         """

#     query_instn_info = "SELECT * FROM InstitutionInfo"
#     query_chain_data = "SELECT * FROM ChainData"
#     query_instn_dict = "SELECT * FROM InstitutionDict"

#     # 从数据库加载数据，并转换为 Pandas DataFrame
#     df_transaction = pg_select(sql_transaction)
#     instn_base_info = pd.read_sql(query_instn_info, engine)
#     df_chain_data = pd.read_sql(query_chain_data, engine)
#     instn_dict = pd.read_sql(query_instn_dict, engine)

#     # 将字典转换为你需要的格式
#     instn_dict = {row['instn_cd']: row for _, row in instn_dict.iterrows()}

#     return df_transaction, instn_base_info, df_chain_data, instn_dict

# def load_data(query_date):
#     engine = get_db_engine()

#     # 使用 SQL 查询代替 CSV 文件读取
#     query_market_price = f"SELECT * FROM MarketPrice WHERE query_date = '{query_date}'"
#     query_transaction = f"SELECT * FROM Transactions WHERE query_date = '{query_date}'"
#     # 这里改成这样，然后我要把时间作为输入
#     squery_transactionql = """
#                             select *
#                             from  dpa.cbt_dl_dtl
#                             where txn_dt = '2023-07-05' and trdng_md_cd = 'NDM'
#                             limit 30000
#                             """
#     query_instn_info = "SELECT * FROM InstitutionInfo"
#     query_chain_data = "SELECT * FROM ChainData"
#     query_instn_dict = "SELECT * FROM InstitutionDict"

#     # 从数据库加载数据，并转换为 Pandas DataFrame
#     df_MarketPrice = pd.read_sql(query_market_price, engine)
#     # df_transaction = pd.read_sql(query_transaction, engine)
#     df_transaction = pg_select(sql)
#     instn_base_info = pd.read_sql(query_instn_info, engine)
#     df_chain_data = pd.read_sql(query_chain_data, engine)
#     instn_dict = pd.read_sql(query_instn_dict, engine)

#     # 将字典转换为你需要的格式
#     instn_dict = {row['instn_cd']: row for _, row in instn_dict.iterrows()}

#     return df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict
