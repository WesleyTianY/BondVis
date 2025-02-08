import pandas as pd
import numpy as np

def classify_top_percent(df, column_name, new_column_name, new_name, percentile=0.8):
    """
    将指定列的计数分布按照指定的百分比阈值分类，创建一个新列，并根据条件填充值。
    
    参数：
    df (DataFrame)：输入的 DataFrame。
    column_name (str)：要进行计数分布的列名。
    new_column_name (str)：新列的列名。
    new_name (str)：新列中用于表示符合条件的值的名称。
    percentile (float)：百分比阈值，默认为0.8。
    
    返回：
    DataFrame：修改后的 DataFrame。
    """
    # 计算指定列的计数分布
    counts = df.groupby(column_name).size()
    
    # 找到前百分之80的计数
    top_percent_counts = counts.quantile(percentile)
    
    # 选择前百分之80的值
    top_values = counts[counts >= top_percent_counts].index.tolist()
    
    # 创建新列，根据条件填充值
    df[new_column_name] = df[column_name].apply(lambda x: x if x in top_values else new_name)
    
    return df

def merge_and_label_others(df, index_column, column_column, order_list, other_rows):
    # 创建交叉表
    pivot_table = pd.pivot_table(df, index=index_column, columns=column_column, aggfunc='size', fill_value=0)

    # 重新排序索引和列标签
    pivot_table = pivot_table.reindex(columns=order_list, fill_value=0)
    
    # 计算每行的总和
    row_sums = pivot_table.sum(axis=1)

    # 按行总和排序
    pivot_table_sorted = pivot_table.loc[row_sums.sort_values(ascending=False).index]

    # 获取后N行
    other_bonds = pivot_table_sorted.iloc[-other_rows:]

    # 将这些行合并为一行并取列和
    other_bonds_combined = pd.DataFrame(other_bonds.sum(axis=0)).T

    # 重命名索引为“其他类型债券”
    other_bonds_combined.index = ['其他类型债券']

    # 删除原表中的这些行
    pivot_table_sorted.drop(other_bonds.index, inplace=True)

    # 将合并的行添加到表的末尾
    pivot_table_sorted = pd.concat([pivot_table_sorted, other_bonds_combined])

    return pivot_table_sorted

def select_specific_data(df_bond_basic_filter, scrty_term, bond_tp_nm):
    # bond_tp_nm = pivot_table_sorted.index.tolist()[bond_tp_nm_index]
    # scrty_term = pivot_table_sorted.columns.tolist()[scrty_term_index]
    # print(scrty_term, bond_tp_nm)
    selected_data = df_bond_basic_filter[(df_bond_basic_filter['new_scrty_term'] == scrty_term) & 
                                         (df_bond_basic_filter['bond_tp_nm'] == bond_tp_nm)]
    print(selected_data)
    return selected_data
