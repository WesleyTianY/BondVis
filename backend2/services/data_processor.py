import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import OneHotEncoder
import numpy as np

def getSummaryByBondList(bond_cd, df_transaction):
    # 只保留 bond_cd 在 bond_cd_list 中的交易记录
    df_transaction['bond_cd'] = df_transaction['bond_cd'].astype(str)
    df_filtered = df_transaction[df_transaction['bond_cd'] == str(bond_cd)]

    # 确保 bond_cd 格式一致
    df_filtered['bond_cd'] = df_filtered['bond_cd'].astype(str)
    df_filtered['nmnl_vol'] = df_filtered['nmnl_vol'] / 1000000

    # 按 bond_cd 统计交易次数
    bond_transactions = df_filtered.groupby('bond_cd').size().reset_index(name='Transaction num')

    # 获取每个 bond_cd 的第一个债券名称
    bonds_names = df_filtered.groupby('bond_cd')['bnds_nm'].first().reset_index()

    # 计算每个 bond_cd 的交易总量
    nmnl_vol_sum = df_filtered.groupby('bond_cd')['nmnl_vol'].sum().reset_index(name='Total nmnl_vol')

    # 合并结果
    result = pd.merge(bond_transactions, bonds_names, on='bond_cd')
    result = pd.merge(result, nmnl_vol_sum, on='bond_cd')
    bondSummary_list = []
    seen_bonds = set()  # 用于追踪已添加的bond_cd
    for index, row in result.iterrows():
        if row['bond_cd'] not in seen_bonds:
            item = {
                'Bond_cd': row['bond_cd'],
                'Transaction_num': row['Transaction num'],
                'Bond_name': row['bnds_nm'],
                'Transaction_volume': row['Total nmnl_vol']
            }
            bondSummary_list.append(item)
            seen_bonds.add(row['bond_cd'])  # 添加到已处理集合中

    # # 使用 bond_cd 作为键构建字典
    # bondSummary_dict = {}
    # for index, row in result.iterrows():
    #     bond_cd = row['bond_cd']
    #     bondSummary_dict[bond_cd] = {
    #         'Transaction_num': row['Transaction num'],
    #         'Bond_name': row['bnds_nm'],
    #         'Transaction_volume': row['Total nmnl_vol']
    #     }

    return bondSummary_list

def get_summary(max_bood_num, df_transaction):
    # Group by 'bond_cd' and count transactions, then reset index
    df_transaction['nmnl_vol'] = df_transaction['nmnl_vol'] / 1000000

    # Convert 'bond_cd' to string type to ensure consistency
    df_transaction['bond_cd'] = df_transaction['bond_cd'].astype(str)

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
    seen_bonds = set()  # 用于追踪已添加的bond_cd
    for index, row in result.iterrows():
        if row['bond_cd'] not in seen_bonds:
            item = {
                'Bond_cd': row['bond_cd'],
                'Transaction_num': row['Transaction num'],
                'Bond_name': row['bnds_nm'],
                'Transaction_volume': row['Total nmnl_vol']
            }
            bondSummary_list.append(item)
            seen_bonds.add(row['bond_cd'])  # 添加到已处理集合中

    # 使用字典代替列表，用于 bond_cd 索引
    # bondSummary_dict = {}
    # for index, row in result.iterrows():
    #     bond_cd = row['bond_cd']
    #     if bond_cd not in bondSummary_dict:
    #         bondSummary_dict[bond_cd] = {
    #             'Transaction_num': row['Transaction num'],
    #             'Bond_name': row['bnds_nm'],
    #             'Transaction_volume': row['Total nmnl_vol']
    #         }
    # print(bondSummary_dict)
    # return bondSummary_list
    return bondSummary_list

def preprocess_data_tsne(df):
    # 设置 Pandas 显示选项
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    # 转换数据类型
    df = df.copy()
    df.loc[:, 'nmnl_vol'] = df['nmnl_vol'].astype(np.int64)
    df.loc[:, 'byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].astype(str)
    df.loc[:, 'slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].astype(str)
    df.loc[:, 'byr_trdr_nm'] = df['byr_trdr_nm'].astype(str)
    df.loc[:, 'slr_trdr_nm'] = df['slr_trdr_nm'].astype(str)

    # 合并字符串列
    df.loc[:, 'instn'] = df['byr_instn_cn_full_nm'] + ',' + df['slr_instn_cn_full_nm']

    # 更新买方和卖方名称列
    df.loc[:, 'byr_instn_cn_full_nm'] = df['byr_instn_cn_full_nm'].str[:6] + df['byr_trdr_nm']
    df.loc[:, 'slr_instn_cn_full_nm'] = df['slr_instn_cn_full_nm'].str[:6] + df['slr_trdr_nm']

    # 再次确认 nmnl_vol 的类型
    df.loc[:, 'nmnl_vol'] = df['nmnl_vol'].astype(np.int64)

    # 四舍五入 net_prc 列
    df.loc[:, 'net_prc'] = df['net_prc'].round(2)
    df.loc[:, 'yld_to_mrty'] = df['yld_to_mrty'].round(2)

    result = df[['dl_tm', 'stlmnt_dt', 'slr_instn_cn_full_nm', 'byr_instn_cn_full_nm', 'nmnl_vol', 'net_prc', 'yld_to_mrty', 'byr_trdr_nm', 'slr_trdr_nm', 'slr_instn_tp', 'byr_instn_tp']]
    result = result.rename(columns={"dl_tm" :'date_dl', "stlmnt_dt" :'date', 'byr_instn_cn_full_nm':'buyer', 'slr_instn_cn_full_nm':"seller",  'instn': 'Institution', 'nmnl_vol': 'volume', 'net_prc': "price", 'yld_to_mrty':'yld_to_mrty'})
    result['date'] = pd.to_datetime(result['date'])
    result['year'] = result['date'].dt.year
    result['month'] = result['date'].dt.month
    result['day'] = result['date'].dt.day
    return result

def get_tsne_data(df, feature_list, n_components=1):
  # 对分类特征进行 one-hot 编码
  encoder = OneHotEncoder()
  encoded_features = encoder.fit_transform(df[feature_list])
  # 使用 t-SNE 进行降维
  tsne = TSNE(n_components, random_state=42, init="random")
  transformed_data = tsne.fit_transform(encoded_features)
  return transformed_data

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
                'yld_to_mrty': row['yld_to_mrty'],
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
                'yld_to_mrty': row['yld_to_mrty'],
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
        df['nmnl_vol'] = pd.to_numeric(df['nmnl_vol'], errors='coerce')
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol']/10000000,
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                'yld_to_mrty': row['yld_to_mrty'],
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
    elif data_type == 'valuation_type':
        for index, row in df.iterrows():
            item = {
                'bnds_nm': row['bnds_nm'],
                'bond_cd': row['bond_cd'],
                'vltn_dt': row['vltn_dt'],
                'netPrice': row['vltn_net_prc'],
                'yld_to_mrty': row['yld_to_mrty'],
            }
            data_list.append(item)
    elif data_type == 'transaction_type_net':
        for index, row in df.iterrows():
            item = {
                'bond_cd': row['bond_cd'],
                'transactionId': row['dl_cd'],
                'netPrice': row['net_prc'],
                'transactionVolume': row['nmnl_vol']/10000000,
                # 'trdng_md_cd': row['trdng_md_cd'],
                # 'trdng_mthd_cd': row['trdng_mthd_cd'],
                # 'bnds_nm': row['bnds_nm'],
                'yld_to_mrty': row['yld_to_mrty'],
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
                # 'netValue11': row['net_prc'],
                # 'hghst_net_prc': row['hghst_net_prc'],
                # 'lwst_net_prc': row['lwst_net_prc'],
                # 'clsng_net_prc': row['clsng_net_prc'],
                # 'wghtd_avg_net_prc': row['wghtd_avg_net_prc'],
                'tradeVolume': row['trd_vol'],
                'date': row['txn_dt'],
                'timeStamp': row['mkt_data_upd_tm']
            }
            data_list.append(item)
    elif data_type == 'marketPrice_broker':
        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            item = {
                'bond_cd': str(row['bond_cd']),
                'netValue': row['dlt_prc'],
                # 'netValue11': row['net_prc'],
                # 'hghst_net_prc': row['hghst_net_prc'],
                # 'lwst_net_prc': row['lwst_net_prc'],
                # 'clsng_net_prc': row['clsng_net_prc'],
                # 'wghtd_avg_net_prc': row['wghtd_avg_net_prc'],
                # 'tradeVolume': row['trd_vol'],
                'timeStamp': row['dl_tm'],
                # 'timeStamp': row['dl_tm']
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
