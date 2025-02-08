import pandas as pd

def trace_trade_chains(linklist, savepath, allnodenames, targetinst, savedf, ratioresult, outratioresult, outthres, findthres):
    b = pd.DataFrame(linklist, columns=["from", "to", "value", "price", "day", "out", "deltaabs"])
    features = []

    for inst in targetinst:
        paths, days, truetargetnum = find_paths_for_institution(b, allnodenames[inst], outthres, findthres)
        if paths:
            feature = calculate_features(paths, savedf, ratioresult, outratioresult, inst, days, truetargetnum)
            features.append(feature)
            save_paths(paths, savepath, inst, outthres)
    
    features_df = pd.DataFrame(features, columns=["目标", "最长路径", "交易总量", "交易偏离", "重复机构", "重复目标", "重复机构比例", "重复目标比例", "重复目标节点", "当天买入比例", "当天异常买入比例", "整体价格偏离度"])
    features_df.to_csv(f"{savepath}/features.csv", encoding="GBK")

def find_paths_for_institution(b, points, outthres, findthres):
    paths = []
    days = set()
    truetargetnum = 0

    for point in reversed(points):
        a = b.copy()
        initial_edges = a[(a["to"] == point) & (a["out"] > outthres)]
        if initial_edges.empty:
            continue

        days.update(initial_edges["day"].unique())
        truetargetnum += 1

        stack = list(initial_edges.index)
        while stack:
            current = stack.pop()
            path = [current]
            current_value = a.loc[current, "value"]
            previous_nodes = find_previous_nodes(a, a.loc[current], findthres)

            for prev in previous_nodes:
                if prev not in path:
                    stack.append(prev)
                    path.append(prev)
                    current_value = min(current_value, a.loc[prev, "value"])
            
            if current_value > 0:
                paths.append({"path": path, "value": current_value})
                a.loc[path, "value"] -= current_value
                a = a[a["value"] > 0]
    
    return paths, days, truetargetnum

def find_previous_nodes(a, current_edge, findthres):
    price = current_edge["price"]
    snode = current_edge["from"]
    possible_edges = a[(a["to"] == snode) & (abs(a["price"] - price) <= findthres)]
    return possible_edges.index.tolist()

def calculate_features(paths, savedf, ratioresult, outratioresult, inst, days, truetargetnum):
    total_amount = sum([p["value"] for p in paths])
    max_length = max([len(p["path"]) for p in paths])
    unique_nodes = set()
    for p in paths:
        edges = savedf.loc[p["path"]]
        unique_nodes.update(edges["from"])
        unique_nodes.update(edges["to"])
    
    duplicate_institutions = len(unique_nodes) - truetargetnum
    duplicate_ratio = duplicate_institutions / len(unique_nodes) if unique_nodes else 0

    ratio_data = ratioresult[(ratioresult["inst"] == inst) & (ratioresult["day"].isin(days))]
    intraday_buy_ratio = ratio_data["in"].sum() / (ratio_data["in"] + ratio_data["out"]).sum() if not ratio_data.empty else 0

    out_ratio_data = outratioresult[(outratioresult["inst"] == inst) & (outratioresult["day"].isin(days))]
    abnormal_buy_ratio = out_ratio_data["in"].sum() / (out_ratio_data["in"] + out_ratio_data["out"]).sum() if not out_ratio_data.empty else 0

    # 此处可以添加更多特征计算

    return [inst, max_length, total_amount, 0, duplicate_institutions, 0, duplicate_ratio, 0, 0, intraday_buy_ratio, abnormal_buy_ratio, 0]

def save_paths(paths, savepath, inst, outthres):
    path_records = []
    for p in paths:
        for edge_idx in p["path"]:
            path_records.append(savedf.loc[edge_idx])
    
    path_df = pd.DataFrame(path_records)
    path_df.to_csv(f"{savepath}/{inst}_{outthres}_paths.csv", encoding="GBK", index=False)
