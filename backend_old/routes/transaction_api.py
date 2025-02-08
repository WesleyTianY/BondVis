from flask import Blueprint, current_app, jsonify
# import time
from backend.services.data_loader import load_data
from backend.services.data_processor import preprocess_data_tsne, iterrowsData, get_tsne_data
# from backend.utils.helper_function import generate_workdays

transaction_bp = Blueprint('transaction', __name__)

'''
def get_or_load_data(query_date):
    cache = current_app.config['cache']
    
    # Check if data is cached
    cached_date = cache.get('date')
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')

    # If any of the data is not cached or the cached date doesn't match the query_date, load and cache new data
    if (cached_date != query_date or
        df_MarketPrice is None or df_transaction is None or instn_base_info is None or df_chain_data is None or instn_dict is None or
        df_MarketPrice.empty or df_transaction.empty or instn_base_info.empty or df_chain_data.empty or not instn_dict):
        
        # Load new data
        df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict = load_data(query_date)
        
        # Cache the new data along with the query_date
        cache.set('date', query_date)
        cache.set('df_MarketPrice', df_MarketPrice)
        cache.set('df_transaction', df_transaction)
        cache.set('instn_base_info', instn_base_info)
        cache.set('df_chain_data', df_chain_data)
        cache.set('instn_dict', instn_dict)
    
    return df_MarketPrice, df_transaction, instn_base_info, df_chain_data, instn_dict
'''

def get_or_load_data(query_date):
    cache = current_app.config['cache']
    
    # Check if data is cached
    cache_date = cache.get('date')
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    df_valuation = cache.get('df_valuation')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
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

@transaction_bp.route("/BasicData_transaction_tsne/<string:bond_cd>", methods=['POST','GET'])
def get_bond_data_transaction_tsne(bond_cd):
    # Load data
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)

    # Date range and filtering
    # start_date, end_date = '2023-7-5', '2023-7-5'
    # workday_list = [day.isoformat() for day in generate_workdays(start_date, end_date)]
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    # filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # Update transaction data with institution types
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']

    filtered_json_transaction.loc[:, 'byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction.loc[:, 'slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))

    # Start timing for preprocess_data_tsne
    df_feature = preprocess_data_tsne(filtered_json_transaction)

    # Select the feature list
    feature_list = ['seller', 'buyer', 'price']
    df_feature = df_feature[feature_list]

    # Start timing for get_tsne_data
    df_transaction_axis = get_tsne_data(df_feature, feature_list, n_components=1)

    # Assign x_pos to filtered_json_transaction
    filtered_json_transaction.loc[:, 'x_pos'] = df_transaction_axis.copy()

    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type_tsne')
    # Preprocess and transform data
    # df_feature = preprocess_data_tsne(filtered_json_transaction)
    # feature_list = ['seller', 'buyer', 'price']
    # df_feature = df_feature[feature_list]
    # df_transaction_axis = get_tsne_data(df_feature, feature_list, n_components=1)
    # filtered_json_transaction['x_pos'] = df_transaction_axis
    # json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type_tsne')
    return jsonify({'filtered_json_transaction': json_transaction})

@transaction_bp.route("/BasicData_yld_to_mrty_tsne/<string:bond_cd>", methods=['POST','GET'])
def get_bond_data_yld_to_mrty_tsne(bond_cd):
    # Load data
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)

    # Date range and filtering
    # start_date, end_date = '2023-7-5', '2023-7-5'
    # workday_list = [day.isoformat() for day in generate_workdays(start_date, end_date)]
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    # filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # df_transaction['date'] = df_transaction['txn_dt']
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]
    # Update transaction data with institution types
    byr_instn_cd_column = filtered_json_transaction['byr_instn_cd']
    slr_instn_cd_column = filtered_json_transaction['slr_instn_cd']

    filtered_json_transaction.loc[:, 'byr_instn_tp'] = byr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))
    filtered_json_transaction.loc[:, 'slr_instn_tp'] = slr_instn_cd_column.map(lambda code: instn_dict.get(code, {}).get('instn_tp'))

    # Start timing for preprocess_data_tsne
    df_feature = preprocess_data_tsne(filtered_json_transaction)

    # Select the feature list
    feature_list = ['seller', 'buyer', 'yld_to_mrty']
    df_feature = df_feature[feature_list]

    # Start timing for get_tsne_data
    df_transaction_axis = get_tsne_data(df_feature, feature_list, n_components=1)

    # Assign x_pos to filtered_json_transaction
    filtered_json_transaction.loc[:, 'x_pos'] = df_transaction_axis.copy()

    json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type_tsne')
    print(json_transaction)
    # Preprocess and transform data
    # df_feature = preprocess_data_tsne(filtered_json_transaction)
    # feature_list = ['seller', 'buyer', 'price']
    # df_feature = df_feature[feature_list]
    # df_transaction_axis = get_tsne_data(df_feature, feature_list, n_components=1)
    # filtered_json_transaction['x_pos'] = df_transaction_axis
    # json_transaction = iterrowsData(filtered_json_transaction, 'transaction_type_tsne')
    return jsonify({'filtered_json_transaction': json_transaction})
