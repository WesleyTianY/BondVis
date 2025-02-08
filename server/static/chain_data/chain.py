import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.manifold import TSNE

# 示例数据加载
data = {
    'date_dl': ['2020-06-01 14:28:19+08:00', '2020-06-01 13:52:37+08:00', '2020-06-01 14:24:08+08:00', 
                '2020-06-01 14:40:04+08:00', '2020-06-01 14:03:49+08:00'],
    'date': ['2020-06-01', '2020-06-01', '2020-06-01', '2020-06-01', '2020-06-01'],
    'seller': ['中信银行股份张勇', '中国光大银行张璇', '厦门银行股份赵颖', '山西证券股份赖颂怡', '广东华兴银行潘志煊'],
    'buyer': ['东方证券股份陈玉婷', '东方证券股份陈玉婷', '中国人民财产丁仪', '中国人民财产丁仪', '中国人民财产丁仪'],
    'volume': [20, 10, 20, 10, 10],
    'price': [99.9, 99.9, 99.9, 99.9, 99.9]
}
df = pd.DataFrame(data)

# 数据预处理
df['date_dl'] = pd.to_datetime(df['date_dl'])
df['date'] = pd.to_datetime(df['date'])
df['week'] = df['date_dl'].dt.isocalendar().week  # 提取周

# 交易频率分析
def calculate_trade_frequency(df, window='1D'):
    df['trade_count'] = df.groupby(pd.Grouper(key='date_dl', freq=window))['date_dl'].transform('count')
    trade_frequency = df['trade_count'].mean() + df['trade_count'].std() * 2
    return trade_frequency

# 价格差异分析
def calculate_price_difference(df):
    df['price_diff'] = df.groupby(['buyer', 'seller'])['price'].diff().abs()
    price_diff_threshold = df['price_diff'].mean() + df['price_diff'].std() * 2
    return price_diff_threshold

# 匹配交易比例分析
def calculate_match_ratio(df):
    df['match'] = df['price_diff'] < calculate_price_difference(df)
    match_ratio = df['match'].sum() / df['match'].count()
    return match_ratio

# 交易时间间隔分析
def calculate_time_interval(df):
    df = df.sort_values(by='date_dl')
    df['time_diff'] = df.groupby(['buyer', 'seller'])['date_dl'].diff().dt.total_seconds()
    time_interval_threshold = df['time_diff'].mean() + df['time_diff'].std() * 2
    return time_interval_threshold

# 交易量分析
def calculate_trade_volume(df):
    total_volume = df['volume'].sum()
    avg_volume = df['volume'].mean()
    volume_threshold = df['volume'].quantile(0.95)
    return total_volume, avg_volume, volume_threshold

# 特征计算
trade_frequency_threshold = calculate_trade_frequency(df)
price_difference_threshold = calculate_price_difference(df)
match_ratio_threshold = 0.9
time_interval_threshold = calculate_time_interval(df)
total_volume, avg_volume, volume_threshold = calculate_trade_volume(df)

# 打印结果
print("交易频率阈值:", trade_frequency_threshold)
print("价格差异阈值:", price_difference_threshold)
print("匹配交易比例阈值:", match_ratio_threshold)
print("交易时间间隔阈值:", time_interval_threshold)
print("总交易量:", total_volume)
print("平均交易量:", avg_volume)
print("交易量阈值:", volume_threshold)

# t-SNE降维
def apply_tsne(df):
    encoder = OneHotEncoder()
    encoded_data = encoder.fit_transform(df[['seller', 'buyer']]).toarray()
    tsne = TSNE(n_components=2, random_state=42)
    tsne_result = tsne.fit_transform(encoded_data)
    return tsne_result

tsne_result = apply_tsne(df)
print("t-SNE 结果:", tsne_result)
