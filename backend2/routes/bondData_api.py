import os
import json
import numpy as np
import pandas as pd
from flask import Flask
from flask import Blueprint, current_app, jsonify, request
from backend.services.data_loader import load_data
from backend.services.data_processor import get_summary, iterrowsData, getSummaryByBondList

bondData_bp = Blueprint('bondData', __name__)

@bondData_bp.route('/bondData', methods=['POST','GET'])
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
