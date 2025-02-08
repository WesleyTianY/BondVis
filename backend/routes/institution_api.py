import json
from datetime import datetime
from flask import Blueprint, current_app, jsonify, request
# from backend.utils.helper_function import generate_workdays
from backend.services.data_loader import load_data
from backend.services.data_processor import iterrowsData

institution_bp = Blueprint('institution', __name__)


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


@institution_bp.route("/BasicData_instn_dict/<string:instn_cd>", methods=['POST','GET'])
def get_instn_cd(instn_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)

    value = instn_dict[instn_cd]
    instn_tp = value["instn_tp"]
    instn_cn_full_nm = value["instn_cn_full_nm"]
    instn_cn_shrt_nm = value["instn_cn_shrt_nm"]

    return jsonify({ 'instn_tp': instn_tp, 'instn_cn_full_nm': instn_cn_full_nm, 'instn_cn_shrt_nm': instn_cn_shrt_nm})

@institution_bp.route("/transaction_history/<string:instn_cd>/<string:type>/<string:bond_cd>", methods=["GET", "POST"])
def get_instn_history(instn_cd, type, bond_cd):
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)

    # start_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # end_date = datetime.strptime('2023-7-5', '%Y-%m-%d')
    # workday_list = generate_workdays(start_date, end_date)
    # workday_list = [day.isoformat() for day in workday_list]

    # Transaction data
    df_transaction['date'] = df_transaction['txn_dt']
    # filtered_json_transaction = df_transaction[df_transaction['date'].isin(workday_list)]
    filtered_json_transaction = df_transaction.copy()
    filtered_json_transaction = filtered_json_transaction[filtered_json_transaction['bond_cd'] == int(bond_cd)]

    instn_cd_groups = filtered_json_transaction.groupby(type)
    instn_cd_data = instn_cd_groups.get_group(int(instn_cd))
    json_transaction = iterrowsData(instn_cd_data, 'transaction')

    return jsonify({'json_transaction': json_transaction})

@institution_bp.route("/institution_types", methods=['POST',"GET"])
def get_institution_types():
    cache = current_app.config['cache']
    query_date = cache.get('query_date')
    df_MarketPrice, df_transaction, df_valuation, instn_base_info, df_chain_data, instn_dict = get_or_load_data(query_date)
    json_data = json.dumps(instn_dict, ensure_ascii=False)
    return jsonify({"instn_dict": json_data})

@institution_bp.route('/color_mapping', methods=['GET'])
def get_color_mapping():
    with open('backend/services/static/instn_tp_color_mapping.json', 'r') as json_file:
        color_mapping = json.load(json_file)
    return jsonify(color_mapping)
