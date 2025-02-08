import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import networkx as nx

def load_data_test(file_path='bond_2005496_2006_2402.csv'):
    """
    读取 CSV 文件并返回指定列的数据框。
    """
    header_string = "dl_cd,txn_dt,stlmnt_dt,dl_tm,bsns_tm,bond_cd,bnds_nm,net_prc,yld_to_mrty,nmnl_vol,amnt,acrd_intrst,totl_acrd_intrst,all_prc,stlmnt_amnt,ttm_yrly,byr_qt_cd,byr_instn_cd,byr_cfets_instn_cd,byr_instn_cn_full_nm,byr_instn_cn_shrt_nm,byr_instn_en_shrt_nm,byr_trdr_nm,byr_adrs,byr_trdr_fax,byr_lgl_rprsntv,byr_trdr_tel,buy_side_trdng_acnt_cd,byr_cptl_bnk_nm,byr_cptl_acnt_no,byr_pymnt_sys_cd,byr_dpst_acnt_nm,buy_side_dpst_cd,byr_trd_acnt_cfets_cd,byr_trd_acnt_cn_full_nm,byr_trd_acnt_cn_shrt_nm,byr_trd_acnt_en_shrt_nm,byr_cptl_acnt_nm,byr_trd_acnt_en_full_nm,slr_qt_cd,slr_instn_cd,slr_cfets_instn_cd,slr_instn_cn_full_nm,slr_instn_cn_shrt_nm,slr_instn_en_shrt_nm,slr_trdr_cd,slr_trdr_nm,slr_adrs,slr_trdr_fax,slr_lgl_rprsntv,slr_trdr_tel,sell_side_trdng_acnt_cd,slr_cptl_bnk_nm,slr_cptl_acnt_no,slr_pymnt_sys_cd,slr_dpst_acnt_nm,sell_side_dpst_acnt,slr_trd_acnt_cfets_cd,slr_trd_acnt_cn_full_nm,slr_trd_acnt_cn_shrt_nm,slr_trd_acnt_en_shrt_nm,slr_cptl_acnt_nm,slr_trd_acnt_en_full_nm,crt_tm,upd_tm"
    header_list = header_string.split(',')
    df = pd.read_csv(file_path)
    return df[header_list]

def merge_transactions(df, window=3):
    """
    合并交易记录，基于买方、卖方和价格，并且在指定时间窗口内合并交易量。
    """
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date', 'buyer', 'seller'])

    merged_transactions = []
    current_transaction = None

    for _, row in df.iterrows():
        if current_transaction is None:
            current_transaction = row
        elif (row['date'] - current_transaction['date']).days <= window:
            if (row['buyer'] == current_transaction['buyer'] and
                row['seller'] == current_transaction['seller'] and
                row['price'] == current_transaction['price']):
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

def preprocess_data(df):
    """
    数据预处理，包括时间转换、列合并和选择所需的列。
    """
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
    df['nmnl_vol'] = np.int64(df["nmnl_vol"]/10000000)
    df['net_prc'] = (df["net_prc"]).round(2)

    # 提取需要的列
    result = df[['dl_tm', 'stlmnt_dt', 'slr_instn_cn_full_nm', 'byr_instn_cn_full_nm', 'nmnl_vol', 'net_prc']]

    # 重命名列以使其更易读
    result = result.rename(columns={
        'dl_tm': 'date_dl',
        'stlmnt_dt': 'date',
        'byr_instn_cn_full_nm': 'buyer',
        'slr_instn_cn_full_nm': 'seller',
        'nmnl_vol': 'volume',
        'net_prc': 'price'
    })
    return merge_transactions(result)

def transactions_filter(df, inst_list):
    """
    筛选出买方或卖方在给定机构列表中的交易记录。
    
    Parameters:
    - df: 输入的 DataFrame。
    - inst_list: 机构名称列表。

    Returns:
    - 筛选后的 DataFrame。
    """
    selected_transactions = df[
        (df['buyer'].isin(inst_list)) |
        (df['seller'].isin(inst_list))
    ]
    return selected_transactions
