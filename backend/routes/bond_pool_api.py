import pandas as pd
from flask import Blueprint, current_app,jsonify
from backend.services.data_loader import load_data
from backend.services.bondNavigation import merge_and_label_others, classify_top_percent, select_specific_data

bond_pool_bp = Blueprint('bond_pool', __name__)

def get_or_load_data(query_date):
    cache = current_app.config['cache']
    
    # Check if data is cached
    df_MarketPrice = cache.get('df_MarketPrice')
    df_transaction = cache.get('df_transaction')
    instn_base_info = cache.get('instn_base_info')
    df_chain_data = cache.get('df_chain_data')
    instn_dict = cache.get('instn_dict')
    query_date = '2023-7-5'
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


@bond_pool_bp.route('/bond_navigation', methods=['POST','GET'])
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

@bond_pool_bp.route('/bond_part_list/<int:bond_tp_nm_index>/<int:scrty_term_index>', methods=['POST', 'GET'])
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
