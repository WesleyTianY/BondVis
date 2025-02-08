import json
import os
import numpy as np
import pandas as pd
from flask import Blueprint, current_app, jsonify, request


# from backend.services.sql import pg_select
bond_bp = Blueprint('bond', __name__)

def load_data_data_center(query_date):
    """
    Load data from the data center (production environment).
    """
    from backend.services.data_center import get_transaction_data, get_valuation_data, get_broker_data
    # Assuming the `query_date` is formatted as a string 'YYYY-MM-DD'
    ndm_transaction_data = get_transaction_data(query_date)
    valuation_data = get_valuation_data(query_date)
    broker_data = get_broker_data(query_date)

    # Filter and process the data as needed
    # For example, filtering the data for a specific bond or date range

    return broker_data, ndm_transaction_data, valuation_data

def load_data_local(query_date):
    """
    Load data from local CSV files.
    """
    # Read local CSV files
    df_mkt = pd.read_csv('backend/services/static/bond_brk10_08.csv', low_memory=False, dtype={'bondcd': str})
    ndm_transaction_data = pd.read_csv('backend/services/static/bond_dtl_10_08.csv', low_memory=False, dtype={'bondcd': str})
    valuation_data = pd.read_csv('backend/services/static/bond_2024_10_09_valuation.csv', low_memory=False, dtype={'bondcd': str})

    # Add further filtering and processing here if necessary

    return df_mkt, ndm_transaction_data, valuation_data

def load_data(query_date):
    """
    Determine which data loader function to use based on the environment.
    """
    mode = os.getenv('FLASK_CONFIG', 'local')
    if mode == 'prod':
        return load_data_data_center(query_date)
    else:
        return load_data_local(query_date)

# @bond_bp.route('/bondData', methods=['POST','GET'])
# def data():
#     bond_id = request.args.get('BondId')  # Ensure the parameter name matches
#     selected_date = request.args.get('selectedDate')
#     print("BondId:", bond_id)
#     print("selectedDate:", selected_date)

#     # 读取并筛选债券市场数据，确保 bondcd 列为字符串类型
#     df_mkt = pd.read_csv('backend/services/static/bond_brk10_08.csv', low_memory=False, dtype={'bondcd': str})

#     # 读取并筛选债券交易数据，确保 bondcd 列为字符串类型
#     ndm_transaction_data = pd.read_csv('backend/services/static/bond_dtl_10_08.csv', low_memory=False, dtype={'bondcd': str})

#     # 读取估值数据，确保 bondcd 列为字符串类型
#     valuation_data = pd.read_csv('backend/services/static/bond_2024_10_09_valuation.csv', low_memory=False, dtype={'bondcd': str})

#     # 筛选特定债券数据
#     df_mkt_filtered_data = df_mkt[df_mkt['bond_cd'] == int(bond_id)].copy()

#     # 转换时间戳格式并去除时区信息
#     df_mkt_filtered_data.loc[:, 'timeStamp'] = pd.to_datetime(df_mkt_filtered_data['dl_tm']).dt.tz_localize(None)

#     # 计算 'dlt_prc' 列的均值和标准差
#     mean_dlt_prc = df_mkt_filtered_data['dlt_prc'].mean()
#     std_dlt_prc = df_mkt_filtered_data['dlt_prc'].std()

#     # 剔除偏离均值10个标准差之外的数据
#     df_mkt_filtered_data = df_mkt_filtered_data[np.abs(df_mkt_filtered_data['dlt_prc'] - mean_dlt_prc) <= 10 * std_dlt_prc]

#     # 排序数据
#     df_mkt_filtered_data = df_mkt_filtered_data.sort_values(by='timeStamp', ascending=True)

#     # 筛选特定债券数据
#     ndm_transaction_filtered_data = ndm_transaction_data[ndm_transaction_data['bond_cd'] == bond_id].copy()

#     # 转换时间戳格式
#     ndm_transaction_filtered_data.loc[:, 'timeStamp'] = pd.to_datetime(ndm_transaction_filtered_data['dl_tm']).dt.tz_localize(None)
#     ndm_transaction_filtered_data = ndm_transaction_filtered_data[ndm_transaction_filtered_data['timeStamp'].dt.date == pd.to_datetime('2024-10-08').date()]

#     # 排序
#     ndm_transaction_sorted_data = ndm_transaction_filtered_data.sort_values(by='timeStamp', ascending=True)

#     valuation_filtered_data = valuation_data[valuation_data['bond_cd'] == bond_id].copy()

#     # 获取债券名称
#     bnds_nm = ndm_transaction_filtered_data["bnds_nm"].unique()[0]

#     # Set random seed for reproducibility
#     np.random.seed(42)

#     # Create a random array with the same length as the data
#     transaction_types = np.random.choice(
#         ['NDM', 'RFQ', 'QDM'], 
#         size=len(ndm_transaction_sorted_data), 
#         p=[0.2, 0.5, 0.3]  # 20% NDM, 50% RFQ, 30% QDM
#     )
#     ndm_transaction_sorted_data['transaction_type'] = transaction_types
#     # 创建数据字典并按时间排序
#     data = {
#         "bond_cd": str(bond_id),  # bond_id 转换为字符串
#         "time": str(selected_date),  # selected_date 转换为字符串
#         "bnds_nm": str(bnds_nm), 
#         "broker_data": [
#             {
#                 "timeStamp": str(row['timeStamp']),  # timeStamp 转换为字符串
#                 "dlt_prc": str(row['dlt_prc'])  # dlt_prc 转换为字符串
#             }
#             for _, row in df_mkt_filtered_data.iterrows()
#         ],
#         "transaction_data": [
#             {
#                 "timeStamp": str(row['timeStamp']),  # timeStamp 转换为字符串
#                 "nmnl_vol": str(row['nmnl_vol']),  # nmnl_vol 转换为字符串
#                 "yld_to_mrty": str(row['yld_to_mrty']),  # yld_to_mrty 转换为字符串
#                 "bond_cd": str(row['bond_cd']),  # bond_cd 转换为字符串
#                 "transactionId": str(row['dl_cd']),  # dl_cd 转换为字符串
#                 "netPrice": str(row['net_prc']),  # net_prc 转换为字符串
#                 "transactionVolume": str(row['nmnl_vol']),  # nmnl_vol 转换为字符串
#                 "byr_instn_cn_full_nm": str(row['byr_instn_cn_full_nm']),  # byr_instn_cn_full_nm 转换为字符串
#                 "slr_instn_cn_full_nm": str(row['slr_instn_cn_full_nm']),  # slr_instn_cn_full_nm 转换为字符串
#                 "byr_instn_cd": str(row['byr_instn_cd']),  # byr_instn_cd 转换为字符串
#                 "slr_instn_cd": str(row['slr_instn_cd']),  # slr_instn_cd 转换为字符串
#                 "transaction_type": str(row['transaction_type']), # transaction_type
#             }
#             for _, row in ndm_transaction_sorted_data.iterrows()
#         ],
#         "val_data": [
#             {
#                 "timeStamp": str(row['vltn_dt']),  # timeStamp 转换为字符串
#                 "vltn_net_prc": str(row['vltn_net_prc']),  # vltn_net_prc 转换为字符串
#                 "yld_to_mrty": str(row['yld_to_mrty'])  # yld_to_mrty 转换为字符串
#             }
#             for _, row in valuation_filtered_data.iterrows()
#         ]
#     }

#     return jsonify(data)


@bond_bp.route('/bondData', methods=['POST', 'GET'])
# def data():
#     bond_id = request.args.get('BondId')  # 获取债券ID
#     selected_date = request.args.get('selectedDate')  # 获取选择的日期

#     print("BondId:", bond_id)
#     print("selectedDate:", selected_date)

#     # 从数据库读取数据
#     df_mkt, ndm_transaction_data, valuation_data = load_data(selected_date)

#     # 筛选特定债券数据
#     df_mkt_filtered_data = df_mkt[df_mkt['bond_cd'] == int(bond_id)].copy()

#     # 转换时间戳格式并去除时区信息
#     df_mkt_filtered_data['timeStamp'] = pd.to_datetime(df_mkt_filtered_data['dl_tm']).dt.tz_localize(None)

#     # 计算 'dlt_prc' 列的均值和标准差
#     mean_dlt_prc = df_mkt_filtered_data['dlt_prc'].mean()
#     std_dlt_prc = df_mkt_filtered_data['dlt_prc'].std()

#     # 剔除偏离均值10个标准差之外的数据
#     df_mkt_filtered_data = df_mkt_filtered_data[np.abs(df_mkt_filtered_data['dlt_prc'] - mean_dlt_prc) <= 10 * std_dlt_prc]

#     # 排序数据
#     df_mkt_filtered_data = df_mkt_filtered_data.sort_values(by='timeStamp', ascending=True)

#     # 筛选特定债券数据
#     ndm_transaction_filtered_data = ndm_transaction_data[ndm_transaction_data['bond_cd'] == bond_id].copy()

#     # 转换时间戳格式
#     ndm_transaction_filtered_data['timeStamp'] = pd.to_datetime(ndm_transaction_filtered_data['dl_tm']).dt.tz_localize(None)

#     # 排序
#     ndm_transaction_sorted_data = ndm_transaction_filtered_data.sort_values(by='timeStamp', ascending=True)

#     valuation_filtered_data = valuation_data[valuation_data['bond_cd'] == bond_id].copy()

#     # 获取债券名称
#     bnds_nm = ndm_transaction_filtered_data["bnds_nm"].unique()[0]

#     # 设置随机种子以便重现
#     np.random.seed(42)

#     # 随机分配交易类型
#     transaction_types = np.random.choice(
#         ['NDM', 'RFQ', 'QDM'], 
#         size=len(ndm_transaction_sorted_data), 
#         p=[0.2, 0.5, 0.3]  # 20% NDM, 50% RFQ, 30% QDM
#     )
#     ndm_transaction_sorted_data['transaction_type'] = transaction_types

#     # 构建响应数据
#     data = {
#         "bond_cd": str(bond_id),
#         "time": str(selected_date),
#         "bnds_nm": str(bnds_nm),
#         "broker_data": [
#             {
#                 "timeStamp": str(row['timeStamp']),
#                 "dlt_prc": str(row['dlt_prc'])
#             }
#             for _, row in df_mkt_filtered_data.iterrows()
#         ],
#         "transaction_data": [
#             {
#                 "timeStamp": str(row['timeStamp']),
#                 "nmnl_vol": str(row['nmnl_vol']),
#                 "yld_to_mrty": str(row['yld_to_mrty']),
#                 "bond_cd": str(row['bond_cd']),
#                 "transactionId": str(row['dl_cd']),
#                 "netPrice": str(row['net_prc']),
#                 "transactionVolume": str(row['nmnl_vol']),
#                 "byr_instn_cn_full_nm": str(row['byr_instn_cn_full_nm']),
#                 "slr_instn_cn_full_nm": str(row['slr_instn_cn_full_nm']),
#                 "byr_instn_cd": str(row['byr_instn_cd']),
#                 "slr_instn_cd": str(row['slr_instn_cd']),
#                 "transaction_type": str(row['transaction_type']),
#             }
#             for _, row in ndm_transaction_sorted_data.iterrows()
#         ],
#         "val_data": [
#             {
#                 "timeStamp": str(row['vltn_dt']),
#                 "vltn_net_prc": str(row['vltn_net_prc']),
#                 "yld_to_mrty": str(row['yld_to_mrty'])
#             }
#             for _, row in valuation_filtered_data.iterrows()
#         ]
#     }

#     return jsonify(data)
def data():
    bond_id = request.args.get('BondId')  # 获取债券ID
    selected_date = request.args.get('selectedDate')  # 获取选择的日期
    selected_date = '2024-10-08'
    print("BondId:", bond_id)
    print("selectedDate:", selected_date)

    # 从数据库读取数据
    df_mkt, ndm_transaction_data, valuation_data = load_data(selected_date)

    # 转换 selected_date 为日期类型
    selected_date = pd.to_datetime(selected_date)

    # 筛选特定债券数据
    df_mkt_filtered_data = df_mkt[(df_mkt['bond_cd'] == int(bond_id)) & 
                                  (pd.to_datetime(df_mkt['dl_tm']).dt.date == selected_date.date())].copy()

    # 转换时间戳格式并去除时区信息
    df_mkt_filtered_data['timeStamp'] = pd.to_datetime(df_mkt_filtered_data['dl_tm']).dt.tz_localize(None)

    # 计算 'dlt_prc' 列的均值和标准差
    mean_dlt_prc = df_mkt_filtered_data['dlt_prc'].mean()
    std_dlt_prc = df_mkt_filtered_data['dlt_prc'].std()

    # 剔除偏离均值10个标准差之外的数据
    df_mkt_filtered_data = df_mkt_filtered_data[np.abs(df_mkt_filtered_data['dlt_prc'] - mean_dlt_prc) <= 10 * std_dlt_prc]

    # 排序数据
    df_mkt_filtered_data = df_mkt_filtered_data.sort_values(by='timeStamp', ascending=True)

    # 筛选特定债券的交易数据
    ndm_transaction_filtered_data = ndm_transaction_data[(ndm_transaction_data['bond_cd'] == bond_id) & 
                                                         (pd.to_datetime(ndm_transaction_data['dl_tm']).dt.date == selected_date.date())].copy()

    # 转换时间戳格式
    ndm_transaction_filtered_data['timeStamp'] = pd.to_datetime(ndm_transaction_filtered_data['dl_tm']).dt.tz_localize(None)

    # 排序
    ndm_transaction_sorted_data = ndm_transaction_filtered_data.sort_values(by='timeStamp', ascending=True)

    # 筛选估值数据
    # valuation_filtered_data = valuation_data[(valuation_data['bond_cd'] == bond_id) & 
    #                                          (pd.to_datetime(valuation_data['vltn_dt']).dt.date == selected_date.date())].copy()
    valuation_filtered_data = valuation_data[(valuation_data['bond_cd'] == bond_id)].copy()

    # 获取债券名称
    bnds_nm = ndm_transaction_filtered_data["bnds_nm"].unique()

    # 设置随机种子以便重现
    np.random.seed(42)

    # 随机分配交易类型
    transaction_types = np.random.choice(
        ['NDM', 'RFQ', 'QDM'], 
        size=len(ndm_transaction_sorted_data), 
        p=[0.2, 0.5, 0.3]  # 20% NDM, 50% RFQ, 30% QDM
    )
    ndm_transaction_sorted_data['transaction_type'] = transaction_types

    # 构建响应数据
    data = {
        "bond_cd": str(bond_id),
        "time": str(selected_date.date()),
        "bnds_nm": str(bnds_nm),
        "broker_data": [
            {
                "timeStamp": str(row['timeStamp']),
                "dlt_prc": str(row['dlt_prc'])
            }
            for _, row in df_mkt_filtered_data.iterrows()
        ],
        "transaction_data": [
            {
                "timeStamp": str(row['timeStamp']),
                "nmnl_vol": str(row['nmnl_vol']),
                "yld_to_mrty": str(row['yld_to_mrty']),
                "bond_cd": str(row['bond_cd']),
                "transactionId": str(row['dl_cd']),
                "netPrice": str(row['net_prc']),
                "transactionVolume": str(row['nmnl_vol']),
                "byr_instn_cn_full_nm": str(row['byr_instn_cn_full_nm']),
                "slr_instn_cn_full_nm": str(row['slr_instn_cn_full_nm']),
                "byr_instn_cd": str(row['byr_instn_cd']),
                "slr_instn_cd": str(row['slr_instn_cd']),
                "transaction_type": str(row['transaction_type']),
            }
            for _, row in ndm_transaction_sorted_data.iterrows()
        ],
        "val_data": [
            {
                "timeStamp": str(row['vltn_dt']),
                "vltn_net_prc": str(row['vltn_net_prc']),
                "yld_to_mrty": str(row['yld_to_mrty'])
            }
            for _, row in valuation_filtered_data.iterrows()
        ]
    }

    return jsonify(data)
