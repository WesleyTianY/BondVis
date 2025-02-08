# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from flask_pymongo import PyMongo
import json
from pydash import _
import numpy as np
import pandas as pd
import json
import math
from sklearn.preprocessing import OneHotEncoder
from sklearn.manifold import TSNE
from datetime import datetime
from chinese_calendar import is_workday, is_holiday
from dateutil.rrule import rrule, DAILY
import networkx as nx
from server.transaction_graph import construct_graph, calculate_degree, identify_market_makers
from server.bondNavigation import merge_and_label_others, classify_top_percent, select_specific_data
from server.instnRelationGraph import generateGraphData
STATIC_FOLDER = 'server'
TEMPLATE_FOLDER = '../client/dist'

app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config.from_object('config')
CORS(app)
# 读取 JSON 文件的函数

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def load_insitution_chains_data():
    """
    Get insitution chains data

    Returns:
    str: JSON formatted data.
    """
    data_chain = read_json_file('server/static/chain_data/data_chain.json')
    # print(data_chain)
    return data_chain

def load_data():
    """
    Load data from the CSV files.

    Returns:
    tuple: Tuple containing DataFrames for MarketPrice, transaction, and instn_base_info.
    """
    # Load the data from the CSV files
    df_MarketPrice = pd.read_csv('server/static/mkt_price_list_all_20230705.csv')
    df_transaction = pd.read_csv('server/static/ndm_transaction_list_all_20230705.csv')
    instn_base_info = pd.read_csv('server/static/20231030/rmb_hstry_actv_instn_base_info.csv')
    header_string = "dl_cd,txn_dt,dl_tm,bsns_tm,bond_cd,bnds_nm,net_prc,yld_to_mrty,nmnl_vol,amnt,acrd_intrst,totl_acrd_intrst,all_prc,stlmnt_amnt,stlmnt_dt,ttm_yrly,byr_qt_cd,byr_instn_cd,byr_cfets_instn_cd,byr_instn_cn_full_nm,byr_instn_cn_shrt_nm,byr_instn_en_shrt_nm,byr_trdr_nm,byr_adrs,byr_trdr_fax,byr_lgl_rprsntv,byr_trdr_tel,buy_side_trdng_acnt_cd,byr_cptl_bnk_nm,byr_cptl_acnt_no,byr_pymnt_sys_cd,byr_dpst_acnt_nm,buy_side_dpst_cd,byr_trd_acnt_cfets_cd,byr_trd_acnt_cn_full_nm,byr_trd_acnt_cn_shrt_nm,byr_trd_acnt_en_shrt_nm,byr_cptl_acnt_nm,byr_trd_acnt_en_full_nm,slr_qt_cd,slr_instn_cd,slr_cfets_instn_cd,slr_instn_cn_full_nm,slr_instn_cn_shrt_nm,slr_instn_en_shrt_nm,slr_trdr_cd,slr_trdr_nm,slr_adrs,slr_trdr_fax,slr_lgl_rprsntv,slr_trdr_tel,sell_side_trdng_acnt_cd,slr_cptl_bnk_nm,slr_cptl_acnt_no,slr_pymnt_sys_cd,slr_dpst_acnt_nm,sell_side_dpst_acnt,slr_trd_acnt_cfets_cd,slr_trd_acnt_cn_full_nm,slr_trd_acnt_cn_shrt_nm,slr_trd_acnt_en_shrt_nm,slr_cptl_acnt_nm,slr_trd_acnt_en_full_nm,crt_tm,upd_tm"
    header_list = header_string.split(',')
    df_chain_data = pd.read_csv('server/static/chain_data/bond_2005496_2006_2402.csv')[header_list]

    # Select desired columns from instn_base_info DataFrame
    selected_columns = ['instn_cd', 'instn_tp', 'instn_cn_full_nm']
    result_df = instn_base_info[selected_columns]

    # Convert DataFrame to dictionary
    instn_dict = result_df.set_index('instn_cd').to_dict(orient='index')

    # Replace nan with None before converting to JSON
    for key, value in instn_dict.items():
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, float) and math.isnan(sub_value):
                instn_dict[key][sub_key] = None

    return df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict

def generate_workdays(start_date, end_date):
    workdays = []
    for dt in rrule(DAILY, dtstart=start_date, until=end_date):
        # 检查日期是否是工作日且不是中国的节假日
        if is_workday(dt.date()) and not is_holiday(dt.date()):
            workdays.append(dt.date())
    return workdays

# STEP 1: Get the summary data
def get_summary(max_bood_num, df_transaction):
    # Group by 'bond_cd' and count transactions, then reset index
    df_transaction['nmnl_vol'] = df_transaction['nmnl_vol'] / 1000000
    bond_transactions = df_transaction.groupby('bond_cd').size().reset_index(name='Transaction num')

    # Group by 'bond_cd' and get the first 'bnds_nm' value for each group
    bonds_names = df_transaction.groupby('bond_cd')['bnds_nm'].first().reset_index()

    # Group by 'bond_cd' and sum 'nmnl_vol' for each group
    nmnl_vol_sum = df_transaction.groupby('bond_cd')['nmnl_vol'].sum().reset_index(name='Total nmnl_vol')

    # Merge the DataFrames based on 'bond_cd'
    result = pd.merge(bond_transactions, bonds_names, on='bond_cd')
    result = pd.merge(result, nmnl_vol_sum, on='bond_cd')

    # Sort by 'Transaction num' in descending order
    result = result.sort_values(by='Transaction num', ascending=False).head(max_bood_num)

    bondSummary_list = []

    for index, row in result.iterrows():
        item = {
            'Bond_cd': row['bond_cd'],
            'Transaction_num': row['Transaction num'],
            'Bond_name': row['bnds_nm'],
            'Transaction_volume': row['Total nmnl_vol']
        }
        bondSummary_list.append(item)
    return bondSummary_list

def iterrowsData(df, data_type):
    data_list = []
    if data_type == 'transaction':
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol']/10000000,
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                # 'yld_to_mrty': row['yld_to_mrty'],
                # 'amnt': row['amnt'],
                'date': row['dl_tm'][0:10],
                'timeStamp': row['dl_tm'],
                # 'timeStamp': str(date_time_string[:10] + ' ' + date_time_string[10:]),
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                # 'byr_instn_tp': row['byr_instn_tp'],
                # 'slr_instn_tp': row['slr_instn_tp']
            }
            data_list.append(item)
    elif data_type == 'transaction_type_tsne':
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol']/10000000,
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                # 'yld_to_mrty': row['yld_to_mrty'],
                # 'amnt': row['amnt'],
                # 'date': row['date'][0:10],
                'timeStamp': row['dl_tm'],
                # 'timeStamp': str(date_time_string[:10] + ' ' + date_time_string[10:]),
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                'byr_instn_tp': row['byr_instn_tp'],
                'slr_instn_tp': row['slr_instn_tp'],
                'x_pos': row['x_pos'],
                # 'byr_instn_tp': row['byr_instn_tp'],
                # 'slr_instn_tp': row['slr_instn_tp']
            }
            data_list.append(item)
    elif data_type == 'transaction_type':
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol']/10000000,
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                # 'yld_to_mrty': row['yld_to_mrty'],
                # 'amnt': row['amnt'],
                # 'date': row['dl_tm'][0:10],
                'timeStamp': row['dl_tm'],
                # 'timeStamp': str(date_time_string[:10] + ' ' + date_time_string[10:]),
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                'byr_instn_tp': row['byr_instn_tp'],
                'slr_instn_tp': row['slr_instn_tp']
            }
            data_list.append(item)
    elif data_type == 'marketPrice':
        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'netValue': row['wghtd_avg_net_prc'],
                # 'hghst_net_prc': row['hghst_net_prc'],
                # 'lwst_net_prc': row['lwst_net_prc'],
                # 'clsng_net_prc': row['clsng_net_prc'],
                # 'wghtd_avg_net_prc': row['wghtd_avg_net_prc'],
                'tradeVolume': row['trd_vol'],
                'date': row['txn_dt'],
                'timeStamp': row['mkt_data_upd_tm']
            }
            data_list.append(item)
    elif data_type == 'instn_type':
        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol'],
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                # 'yld_to_mrty': row['yld_to_mrty'],
                # 'amnt': row['amnt'],
                'date': row['dl_tm'][0:10],
                'timeStamp': row['dl_tm'],
                # 'timeStamp': str(date_time_string[:10] + ' ' + date_time_string[10:]),
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                'byr_instn_tp': row['byr_instn_tp'],
                'slr_instn_tp': row['slr_instn_tp'],
            }
            data_list.append(item)
    return data_list

# STEP 2: Get the transaction data
def get_details_data(df_MarketPrice, df_transaction):
    transaction_data = []
    MarketPrice_data = []
    # 遍历DataFrame的每一行, 将DataFrame转换为JSON
    transaction_data = iterrowsData(df_transaction, 'transaction')
    MarketPrice_data = iterrowsData(df_MarketPrice, 'marketPrice')
    json_transaction = json.dumps(transaction_data)
    # print('json_transaction:', json_transaction)
    json_mkt = json.dumps(MarketPrice_data)
    return json_transaction, json_mkt

def preprocess_data_tsne(df):
    # 设置 Pandas 显示选项
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)

    # 将交易时间列转换为 datetime 对象
    df['dl_tm'] = pd.to_datetime(df['dl_tm'])

    # 将字符串列转换为字符串类型
    df['byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].astype(str)
    df['slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].astype(str)
    df['byr_trdr_nm'] = df['byr_trdr_nm'].astype(str)
    df['slr_trdr_nm'] = df['slr_trdr_nm'].astype(str)

    # 将购买和销售机构合并为一个列
    df['instn'] = df['byr_instn_cn_full_nm'].str.cat(df['slr_instn_cn_full_nm'], sep=',')

    # 计算每个月每个机构的交易次数
    df['byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].str[:6].str.cat(df['byr_trdr_nm'], sep='')
    df['slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].str[:6].str.cat(df['slr_trdr_nm'], sep='')
    df['byr_trdr_nm'] = df['byr_trdr_nm'].str.ljust(4)
    df['slr_trdr_nm'] = df['slr_trdr_nm'].str.ljust(4)
    df['nmnl_vol'] = np.int64(df["nmnl_vol"])
    df['net_prc'] = (df["net_prc"]).round(2)
    # 提取需要的列
    result = df[['dl_tm', 'stlmnt_dt', 'slr_instn_cn_full_nm', 'byr_instn_cn_full_nm', 'nmnl_vol', 'net_prc', 'byr_trdr_nm', 'slr_trdr_nm', 'slr_instn_tp', 'byr_instn_tp']]
    # 重命名列以使其更易读
    result = result.rename(columns={"dl_tm" :'date_dl', "stlmnt_dt" :'date', 'byr_instn_cn_full_nm':'buyer', 'slr_instn_cn_full_nm':"seller",  'instn': 'Institution', 'nmnl_vol': 'volume', 'net_prc': "price", 'byr_cd':'byr_instn_cd', 'slr_cd':'slr_instn_cd'})
    result['date'] = pd.to_datetime(result['date'])
    result['year'] = result['date'].dt.year
    result['month'] = result['date'].dt.month
    result['day'] = result['date'].dt.day
    return result
    return merge_transactions(result)

def get_tsne_data(df, feature_list, n_components=1):
  # 对分类特征进行 one-hot 编码
  encoder = OneHotEncoder()
  encoded_features = encoder.fit_transform(df[feature_list])
  # 使用 t-SNE 进行降维
  tsne = TSNE(n_components, random_state=42, init="random")
  transformed_data = tsne.fit_transform(encoded_features)
  return transformed_data

# 调用函数加载数据
df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = load_data()
json_transaction, json_mkt = get_details_data(df_MarketPrice, df_transaction)

# preprocess_data_tsne(df_transaction)
# feature_list = ['volume', 'price', 'year', 'month', 'day']
# df_feature = df_processed[feature_list]

@app.route("/api/BasicData_transaction_tsne/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData_transaction_tsne(bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # 增加两列 buyer_type 和 seller_type
    # update the instm_cd of the transaction
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    # print(filtered_json_transaction)
    # update the byr or slr instn_tp
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    # 1. preprocess_data_tsne
    # df['byr_trdr_nm'] = df['slr_trdr_nm'].str.ljust(4)
    # df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = load_data() , 'year', 'month' 'seller', 'buyer', 'seller', 'buyer', 'volume', 
    df_feature = preprocess_data_tsne(filtered_json_transaction)
    feature_list = ['seller', 'buyer', 'price']
    df_feature = df_feature[feature_list]
    # print(df_feature)
    df_transaction_axis = get_tsne_data(df_feature, feature_list, n_components=1)
    filtered_json_transaction['x_pos'] = df_transaction_axis
    # print("df_transaction_axis shape", df_transaction_axis.shape)

    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type_tsne')

    return { 'filtered_json_transaction': json_transaction }
@app.route('/api/transaction', methods=['POST','GET'])
def get_all_mkt():
    json_transaction, json_mkt = get_details_data(df_MarketPrice, df_transaction)
    return { 'json_mkt': json_mkt, 'json_transaction': json_transaction }

@app.route('/api/bondSummaryData', methods=['POST','GET'])
def get_bondSummaryData():
    max_bood_num = 30
    df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = load_data()
    # print("df_transaction:", df_transaction)
    bondSummaryData = get_summary(max_bood_num, df_transaction)
    return { 'bondSummaryData': bondSummaryData }

@app.route("/api/BasicData/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData(bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 1. MarketPrice data
    # Filter the data for 'date'
    df_MarketPrice['date'] = df_MarketPrice['mkt_data_upd_tm'].str[:10]
    filtered_json_mkt = df_MarketPrice[df_MarketPrice['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_mkt = filtered_json_mkt[filtered_json_mkt['bond_cd'] == int(bond_cd)]
    filtered_json_mkt = iterrowsData(filtered_json_mkt, 'marketPrice')

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    filtered_json_transaction = iterrowsData(filtered_json_transaction, 'transaction')

    return jsonify({ 'filtered_json_mkt': filtered_json_mkt, 'filtered_json_transaction': filtered_json_transaction })

@app.route("/api/BasicData_transaction/<string:bond_cd>", methods=['POST','GET'])
def getTheBondData_transaction(bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # 增加两列 buyer_type 和 seller_type
    # update the instm_cd of the transaction
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    # print(filtered_json_transaction)
    # update the byr or slr instn_tp
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    
    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type')

    return { 'filtered_json_transaction': json_transaction }

@app.route("/api/BasicData_MarketPrice/<string:bond_cd>", methods=['POST','GET'])
def getTheBond_MarketPrice(bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 1. MarketPrice data
    # Filter the data for 'date'
    df_MarketPrice['date'] = df_MarketPrice['mkt_data_upd_tm'].str[:10]
    filtered_json_mkt = df_MarketPrice[df_MarketPrice['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_mkt = filtered_json_mkt[filtered_json_mkt['bond_cd'] == int(bond_cd)]
    filtered_json = iterrowsData(filtered_json_mkt, 'marketPrice')

    return jsonify({ 'filtered_json_mkt': filtered_json })

# Input: instn_dict, target_instn_cd
# Return: instn_info
@app.route("/api/BasicData_instn_dict/<string:instn_cd>", methods=['POST','GET'])
def get_instn_cd(instn_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串

    value = instn_dict[instn_cd]
    instn_tp = value["instn_tp"]
    instn_cn_full_nm = value["instn_cn_full_nm"]
    instn_cn_shrt_nm = value["instn_cn_shrt_nm"]

    return jsonify({ 'instn_tp': instn_tp, 'instn_cn_full_nm':instn_cn_full_nm, 'instn_cn_shrt_nm':instn_cn_shrt_nm})

# Input: instn_cd
# Return: the ndm history
@app.route("/api/transaction_history/<string:instn_cd>/<string:type>/<string:bond_cd>", methods=["GET", "POST"])
def get_instn_history(instn_cd, type, bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    # print("instn_cd", instn_cd)
    instn_cd_groups = filtered_json_transaction.groupby(type)
    instn_cd_data = instn_cd_groups.get_group(int(instn_cd))
    json_transaction = iterrowsData(instn_cd_data, 'transaction')
    return jsonify({'json_transaction': json_transaction})

@app.route("/api/institution_types", methods=["GET"])
def get_institution_types():
    json_data = json.dumps(instn_dict, ensure_ascii=False)
    return jsonify({"instn_dict": json_data})

@app.route("/api/type_detial/<string:type>/<string:bond_cd>", methods=["GET", "POST"])
def get_type_detial(type, bond_cd):
    
    # 获得不同机构的机构的交易频次信息热力图 主要是时间和价格以及体量
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_date_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond1'
    filtered_bond_transaction = filtered_date_transaction[filtered_date_transaction['bond_cd'] == int(bond_cd)]

    # update the instm_cd of the transaction
    byr_instn_cd_column = filtered_bond_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_bond_transaction['slr_instn_cd']

    # update the byr or slr instn_tp
    filtered_bond_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_bond_transaction['slr_instn_cd'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))

    byr_instn_type = filtered_bond_transaction['byr_instn_tp'].unique()
    slr_instn_type = filtered_bond_transaction['slr_instn_cd'].unique()

    byr_instn_cd_groups = filtered_bond_transaction.groupby(byr_instn_type)
    slr_instn_cd_groups = filtered_bond_transaction.groupby(slr_instn_type)

    for instn_type in byr_instn_type:
        byr_instn_cd_data = byr_instn_cd_groups.get_group(int(instn_type))
        byr_instn_type_collection = []
        for index, row in byr_instn_cd_data.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol'],
                'date': row['dl_tm'][0:10],
                'timeStamp': row['dl_tm'],
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                'instn_tp': row['byr_instn_tp']
            }
            byr_instn_type_collection.append(item)
    for instn_type in slr_instn_type:
        slr_instn_cd_data = slr_instn_cd_groups.get_group(int(instn_type))
        slr_instn_type_collection = []
        for index, row in slr_instn_cd_data.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol'],
                'date': row['dl_tm'][0:10],
                'timeStamp': row['dl_tm'],
                'byr_instn_cn_full_nm': row['byr_instn_cn_full_nm'],
                'slr_instn_cn_full_nm': row['slr_instn_cn_full_nm'],
                'byr_instn_cd': row['byr_instn_cd'],
                'slr_instn_cd': row['slr_instn_cd'],
                'instn_tp': row['slr_instn_tp']
            }
            slr_instn_type_collection.append(item)


    return jsonify({ 'byr_json_transaction': byr_instn_type_collection, 'slr_json_transaction': slr_instn_type_collection })

@app.route('/api/color_mapping', methods=['GET'])
def get_color_mapping():
    with open('server/static/20231030/instn_tp_color_mapping.json', 'r') as json_file:
        color_mapping = json.load(json_file)
    return jsonify(color_mapping)

def data_preprocessing(bond_cd):
    # Filter the data date list, market data、transaction data、valuation data
    # 使用datetime模块解析日期字符串
    start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    workday_list = generate_workdays(start_date, end_date)
    workday_list = [day.isoformat() for day in workday_list]

    # 2. Transaction data
    # Filter the data for 'date'
    df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]

    # Filter the data for 'bond'
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # 增加两列 buyer_type 和 seller_type
    # update the instm_cd of the transaction
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']
    filtered_json_transaction['amnt'] = filtered_json_transaction['net_prc']*filtered_json_transaction['nmnl_vol']
    filtered_json_transaction['totl_acrd_intrst'] = filtered_json_transaction['acrd_intrst']
    filtered_json_transaction['stlmnt_amnt'] = filtered_json_transaction['amnt'] + filtered_json_transaction['acrd_intrst']
    filtered_json_transaction['all_price'] = filtered_json_transaction['stlmnt_amnt']/filtered_json_transaction['nmnl_vol']
    # print(filtered_json_transaction)
    # update the byr or slr instn_tp
    filtered_json_transaction['byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction['slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    return filtered_json_transaction

@app.route('/api/graph_data/<string:bond_cd>/<string:the_instn_cd>', methods=['POST','GET'])
def get_graph_data(bond_cd, the_instn_cd):
    # Input: instn_id, bond_cd,
    # Output: bigraph, node:{ }, links:{ source, target }
    # 对于每一个机构来说，找到他们的买入和卖出的交易，进行导出，而这个list则为该交易list进行去重的结果。
    # 对于每一个机构来说，可以找到交易的时序先后关系
    filtered_json_transaction = data_preprocessing(bond_cd)
    # filter the transaction by Volume or number
    # volume
    volume_threshold = 50
    # min_transaction_count
    min_transaction_count = 2

    # 创建 nodes 列表
    unique_instn_cd = set()
    # unique_instn_cd = set(filtered_json_transaction['byr_instn_cd']).union(set(filtered_json_transaction['slr_instn_cd']))

    # 创建 links 列表
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
            # print("Instn_cd: ", instn_cd)
            value = instn_dict[int(instn_cd)]
            instn_cn_full_nm = value["instn_cn_full_nm"]
            instn_tp = value["instn_tp"]
            nodes.append({"id": instn_cd, "name": instn_cn_full_nm, "instn_tp": instn_tp})
    result_dict = {"nodes": nodes, "links": links, "bond_cd": bond_cd, "instn_cd": str(the_instn_cd)}
    # 删除与被筛选掉的节点相关的 links
    # links = [link for link in links if link["source"] in unique_instn_cd and link["target"] in unique_instn_cd]

    # save the global info of each node
    All_node_info = graph_nodes_info(bond_cd)
    for node in nodes:
        id = node["id"]
        node["node_global_info"] = All_node_info[id]

    # save the global info of each node
    result_dict["statistics_info"] = find_max_total_volume_by_type(All_node_info)
    return result_dict

def find_max_total_volume_by_type(node_info):
    max_total_volume_buyin = 0
    max_total_volume_sell = 0
    # 遍历节点信息
    for _, info in node_info.items():
        # 处理买入信息
        total_volume_buyin = info["buyin"]["total_volume"]
        if total_volume_buyin > max_total_volume_buyin:
            max_total_volume_buyin = total_volume_buyin
        # 处理卖出信息
        total_volume_sell = info["sell"]["total_volume"]
        if total_volume_sell > max_total_volume_sell:
            max_total_volume_sell = total_volume_sell
    return {
        "max_total_volume_buyin": max_total_volume_buyin,
        "max_total_volume_sell": max_total_volume_sell
    }

def graph_nodes_info(bond_cd):
    # TODO: creat a node info structure
    # 创建空字典用于存储节点信息
    node_info = {}
    filtered_json_transaction = data_preprocessing(bond_cd)
    # 遍历交易数据
    for _, row in filtered_json_transaction.iterrows():
        source = str(row['byr_instn_cd'])
        target = str(row['slr_instn_cd'])
        volume = row['nmnl_vol']
        price = row['net_prc']

        # 处理买入节点信息
        if source not in node_info:
            node_info[source] = {
                "buyin": {"total_volume": 0, "num_transactions": 0, "prices": []}, 
                "sell": {"total_volume": 0, "num_transactions": 0, "prices": []}
                }
        node_info[source]["buyin"]["total_volume"] += volume
        node_info[source]["buyin"]["num_transactions"] += 1
        node_info[source]["buyin"]["prices"].append(price)

        # 处理卖出节点信息
        if target not in node_info:
            node_info[target] = {
                "buyin": {"total_volume": 0, "num_transactions": 0, "prices": []},
                "sell": {"total_volume": 0, "num_transactions": 0, "prices": []}
                }
        node_info[target]["sell"]["total_volume"] += volume
        node_info[target]["sell"]["num_transactions"] += 1
        node_info[target]["sell"]["prices"].append(price)
    return node_info

def graph_links_info():
    # TODO: creat a link info structure
    pass

@app.route('/api/get_global_graph_data/<string:bond_cd>', methods=['POST','GET'])
def get_all_graph_data(bond_cd):
    the_bond_data = data_preprocessing(bond_cd)
    filtered_data = filterByTransactionNum(the_bond_data, min_transactions = 3)
    G = build_graph(filtered_data)
    # Get the list of cycles
    cycles = list(nx.simple_cycles(G))
    # Create a unique set of nodes from the cycles
    unique_nodes = set(node for cycle in cycles for node in cycle)
    # Create a subgraph containing only nodes in the cycles
    # subgraph = G.subgraph(unique_nodes)
    # Convert the subgraph to a JSON format for D3.js
    # graph_data = {
    #     "nodes": [{"id": node, "label": str(node)} for node in subgraph.nodes],
    #     "links": [{"source": source, "target": target} for source, target in subgraph.edges]
    # }
    # Convert to JSON string
    # json_data = json.dumps(graph_data, indent=2)
    # 对于所有的节点 遍历所有的节点的pd
    # 创建 links 列表
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
    json_data = json.dumps(result_dict, indent=2)

    return json_data

# 假设 df_transaction 是包含交易数据的 DataFrame
def build_graph(datadf):
    # 构建有向图
    G = nx.DiGraph()
    
    # 添加交易边
    for _, row in datadf.iterrows():
        buyer = row['byr_instn_cd']
        seller = row['slr_instn_cd']
        
        # 保证两个节点之间只有一条边
        if G.has_edge(buyer, seller):
            # 如果已经存在边，则更新交易信息（可根据实际情况进行处理）
            pass
        else:
            G.add_edge(buyer, seller, transaction_info={})  # 可以根据需要存储交易信息的字典
    
    return G

def filterByTransactionNum(df_transaction, min_transactions = 3):
    df_transaction.sort_values(['byr_instn_cd', 'slr_instn_cd', 'dl_tm'], inplace=True)

    # 计算每个机构每天的交易次数
    # daily_transaction_counts = df_transaction.groupby(['byr_instn_cd', 'dl_tm']).size().reset_index(name='transaction_count')
    df_buy_counts = df_transaction[df_transaction['byr_instn_cd'].notnull()].groupby(['byr_instn_cd', 'slr_instn_cd']).size().reset_index(name='buy_counts')
    df_sell_counts = df_transaction[df_transaction['slr_instn_cd'].notnull()].groupby(['slr_instn_cd', 'byr_instn_cd']).size().reset_index(name='sell_counts')

    # 根据交易次数筛选机构
    filtered_institutions_buy = df_buy_counts[(df_buy_counts['buy_counts'] >= min_transactions)]['byr_instn_cd'].tolist()
    filtered_institutions_sell = df_sell_counts[(df_sell_counts['sell_counts'] >= min_transactions)]['slr_instn_cd'].tolist()

    # 过滤掉不在筛选列表中的交易记录
    filtered_institutions = df_transaction[(df_transaction['byr_instn_cd'].isin(filtered_institutions_buy)) &
                                    (df_transaction['slr_instn_cd'].isin(filtered_institutions_sell))]

    # print('institutions number: \n', filtered_institutions.groupby(['byr_instn_cd']).size())
    return filtered_institutions

# @app.route('/api/get_transaction_chains/<string:bond_cd>', methods=['POST','GET'])
@app.route('/api/get_transaction_chains/<int:month>', methods=['POST','GET'])
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

@app.route('/api/get_transaction_chains_sample', methods=['POST','GET'])
def get_transaction_chains_sample():
    """
    Get sample transaction chains data.

    Returns:
    str: JSON formatted data.
    """
    _, _, _, df_chain_data, _ = load_data()
    # print(df_chain_data)
    graph_data = construct_graph(df_chain_data)
    data_json = json.dumps(graph_data)
    return data_json

@app.route('/api/process_hovered_node', methods=['POST','GET'])
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

with open('server/static/chain_data/data_chain.json', 'r') as file:
    data = json.load(file)
    # print(data)

@app.route('/api/the_transaction_chains_data', methods=['POST','GET'])
def get_the_transaction_chains_data():
    try:
        # 打开并读取 JSON 文件
        with open('server/static/chain_data/data_chain.json', 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        print("File not found.")
        return jsonify({"error": "File not found"})
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return jsonify({"error": "Error decoding JSON"})


@app.route('/api/transaction_sankey_data', methods=['POST','GET'])
def get_transaction_sankey_data():
    try:
        # 打开并读取 JSON 文件
        with open('server/static/chain_data/titanic-data.json', 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        print("File not found.")
        return jsonify({"error": "File not found"})
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return jsonify({"error": "Error decoding JSON"})


@app.route('/api/bond_pool_data', methods=['POST','GET'])
def get_bond_pool_data():
    try:
        # 打开并读取 JSON 文件
        with open('server/static/chain_data/flare.json', 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        print("File not found.")
        return jsonify({"error": "File not found"})
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return jsonify({"error": "Error decoding JSON"})

import csv
def csv_to_json(csv_file):
    json_data = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            json_data.append(row)
    return json_data

@app.route('/api/matrixSampleData', methods=['POST','GET'])
def get_matrixSampleData():
    try:
        # 打开并读取 JSON 文件
        json_data = csv_to_json('server/static/matrixSampleData.csv')
        return jsonify(json_data)
    except FileNotFoundError:
        print("File not found.")
        return jsonify({"error": "File not found"})
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return jsonify({"error": "Error decoding JSON"})


@app.route('/api/bond_navigation', methods=['POST','GET'])
def get_bond_navigation():
    df_bond_basic = pd.read_csv('server/static/bond_basic_info_sheet.csv')
    df_bond_basic = df_bond_basic.drop_duplicates(subset='bond_cd')
    feature = ['bond_cd', 'bond_cn_full_nm', 'bond_cn_shrt_nm', 'scrty_term', 'crcltn_size', 'bond_tp_nm', 'indstry_nm', 'indstry_sbcls_nm']
    df_bond_basic_filter = df_bond_basic[feature]
    df_bond_basic_filter = classify_top_percent(df_bond_basic_filter, 'scrty_term', 'new_scrty_term', '其他期限', percentile=0.95)

    # df_bond_basic_filter['crcltn_size'] = df_bond_basic_filter['crcltn_size']/100000000
    # df_bond_basic_filter['crcltn_size_sqrt'] = np.sqrt(df_bond_basic_filter['crcltn_size'])

    # df_bond_basic_filter['indstry_nm'].fillna('其他行业', inplace=True)
    # df_bond_basic_filter['indstry_sbcls_nm'].fillna('其他sbcls行业', inplace=True)
    scrty_term_order = ['1年', '3年', '5年', '7年', '10年', '30年', '其他期限']
    bond_sheet = merge_and_label_others(df_bond_basic_filter, 'bond_tp_nm', 'new_scrty_term', scrty_term_order, 15)

    matrix_data = bond_sheet.values.tolist()
    matrix_data = bond_sheet.reset_index().values.tolist()
    matrix_data.insert(0, [""] + bond_sheet.columns.tolist())
    json_matrix_data = jsonify(matrix_data)

    return json_matrix_data

@app.route('/api/bond_part_list/<int:bond_tp_nm_index>/<int:scrty_term_index>', methods=['POST', 'GET'])
def get_bond_part_list(scrty_term_index, bond_tp_nm_index):
    try:
        df_bond_basic = pd.read_csv('server/static/bond_basic_info_sheet.csv')
        df_bond_basic = df_bond_basic.drop_duplicates(subset='bond_cd')
    except Exception as e:
        return jsonify({"error": "Failed to read CSV file", "details": str(e)}), 500

    feature = ['bond_cd', 'bond_cn_full_nm', 'bond_cn_shrt_nm', 'scrty_term', 'crcltn_size', 'bond_tp_nm', 'indstry_nm', 'indstry_sbcls_nm']
    df_bond_basic_filter = df_bond_basic[feature]

    df_bond_basic_filter = classify_top_percent(df_bond_basic_filter, 'scrty_term', 'new_scrty_term', '其他期限', percentile=0.95)
    scrty_term_order = ['1年', '3年', '5年', '7年', '10年', '30年', '其他期限']
    df_bond_basic_filter = df_bond_basic_filter[['bond_cd', 'bond_cn_shrt_nm', 'scrty_term', 'crcltn_size', 'bond_tp_nm', 'new_scrty_term']]

    bond_sheet = merge_and_label_others(df_bond_basic_filter, 'bond_tp_nm', 'new_scrty_term', scrty_term_order, 16)
    print('bond_sheet:', bond_sheet)

    scrty_term = bond_sheet.columns.tolist()[scrty_term_index-1]
    bond_tp_nm = bond_sheet.index.tolist()[bond_tp_nm_index-1]

    selected_bond_sheet = select_specific_data(df_bond_basic_filter, scrty_term, bond_tp_nm)
    # df_bond_basic_unique = selected_bond_sheet.drop_duplicates(subset='bond_cd')
    result = selected_bond_sheet.to_dict(orient='records')
    return jsonify(result)


@app.route('/api/instnRelationGraph', methods=['POST', 'GET'])
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
