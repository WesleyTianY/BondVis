def getdaichiinfo(tradedf, minprice, maxprice, savepath):
    # Filter the dataframe
    tradedf = tradedf[(tradedf[pricestr] < maxprice) & (tradedf[pricestr] > minprice)]
    tradedf = tradedf[tradedf[dlmthdstr] != matchingmthdstr]
    tradedf = tradedf[tradedf["out"] > outthres]
    if tradedf.empty:
        return pd.DataFrame([]), 0, 0, 0, 0

    # Calculate delta amounts
    tradedf["deltamnt"] = tradedf[amtstr] * tradedf["delta"]
    tradedf["deltaabsmnt"] = tradedf[amtstr] * tradedf["deltaabs"]

    # Group by 'from' and 'to'
    df_grouped = tradedf.groupby([fromstr, tostr], as_index=False)[amtstr].sum()
    graph_df = df_grouped.rename(columns={amtstr: 'weight', fromstr: 'start', tostr: 'end'})
    graph_df = graph_df[graph_df['weight'] > 0]

    # Generate graph nodes and edges
    nodes = list(set(graph_df['start']) | set(graph_df['end']))
    edges = [(row['start'], row['end'], row['weight']) for _, row in graph_df.iterrows()]
    reverse_edges = [(end, start, weight) for start, end, weight in edges]
    inv_weight_edges = [(start, end, 1 / weight) for start, end, weight in reverse_edges]

    # Build network graphs
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(reverse_edges)
    
    Gm = igraph.Graph.TupleList(reverse_edges, directed=True, edge_attrs='weight')
    Gm_pagerank = igraph.Graph.TupleList(edges, directed=True, edge_attrs='weight')
    Gm_closeness = igraph.Graph.TupleList(inv_weight_edges, directed=True, edge_attrs='weight')

    # Initialize dataframes
    curdate = tradedf[datestr].min()
    duration = (tradedf[datestr].max() - curdate) / np.timedelta64(1, 'D') + 1
    owndf, trademntdf, lendmntdf = (pd.DataFrame(index=nodes) for _ in range(3))
    trademntpricedf, trademntprice_abs_df = (pd.DataFrame(index=nodes) for _ in range(2))
    trademntprice_abs_sum = np.zeros(len(nodes))

    # Process daily data
    for i in range(int(duration)):
        tradedaydf = tradedf[tradedf[datestr] == curdate]
        group_from = tradedaydf.groupby(fromstr)
        group_to = tradedaydf.groupby(tostr)

        owndf[curdate] = group_from[amtstr].sum() - group_to[amtstr].sum()
        trademntdf[curdate] = group_from[amtstr].sum() + group_to[amtstr].sum()
        trademntpricedf[curdate] = group_from["deltamnt"].sum() / (trademntdf[curdate] + 1e-7)
        trademntprice_abs_df[curdate] = group_from["deltaabsmnt"].sum() / (trademntdf[curdate] + 1e-7)
        lendmntdf[curdate] = group_from[amtstr].sum()

        trademntprice_abs_sum += trademntprice_abs_df[curdate].values
        owndf[curdate + np.timedelta64(1, 'D')] = owndf[curdate]
        curdate += np.timedelta64(1, 'D')

    # Final calculations
    owndf[curdate] = owndf.iloc[:, -1]
    trademntdf[curdate] = trademntdf.sum(axis=1)
    trademntpricedf[curdate] = trademntpricedf.mean(axis=1)
    trademntprice_abs_df[curdate] = trademntprice_abs_sum / trademntdf[curdate]

    # Metrics calculation
    result, result_in = calculate_metrics(Gm, Gm_pagerank, Gm_closeness, owndf, trademntdf, lendmntdf, trademntpricedf, trademntprice_abs_df)

    # Save results
    save_results(savepath, result, result_in, owndf, trademntdf, trademntprice_abs_df, lendmntdf)

    return result, result_in, owndf, trademntpricedf, (owndf.abs() + 1e-4) / trademntdf

def calculate_metrics(Gm, Gm_pagerank, Gm_closeness, owndf, trademntdf, lendmntdf, trademntpricedf, trademntprice_abs_df):
    result = pd.DataFrame()
    result_in = pd.DataFrame(index=Gm.vs["name"])

    result["density"] = [Gm.density()]
    result["assortativity"] = [Gm.assortativity_degree()]
    result["avgdegree"] = [np.mean(Gm.degree())]
    result["transitivity"] = [Gm.transitivity_undirected()]

    result_in["degree"] = Gm.degree()
    result_in["pagerank"] = Gm_pagerank.pagerank()
    result_in["indegree"] = Gm.degree(mode="in")
    result_in["outdegree"] = Gm.degree(mode="out")
    result_in["betweenness"] = Gm_closeness.betweenness(weights="weight")
    result_in["eff"] = get_eff_aps(graph_df)["eff"]
    result_in["closenessin"] = Gm_closeness.closeness(weights="weight", mode="IN")
    result_in["closenessout"] = Gm_closeness.closeness(weights="weight", mode="OUT")
    result_in["localtrans"] = Gm.transitivity_local_undirected()
    result_in["leadrate"] = lendmntdf.iloc[:, -1] / trademntdf.iloc[:, -1]
    result_in["delta"] = trademntpricedf.iloc[:, -1]
    result_in["deltaabs"] = trademntprice_abs_df.iloc[:, -1]
    result_in["ownmnt"] = owndf.iloc[:, -1]
    result_in["owntraderatio"] = (owndf.abs().iloc[:, -1] + 1e-4) / trademntdf.iloc[:, -1]
    result_in["trademnt"] = trademntdf.iloc[:, -1]

    result["avgownmnt"] = result_in["ownmnt"].mean()
    result["avgleadrate"] = result_in["leadrate"].mean()
    result["avgdelta"] = result_in["delta"].mean()
    result["mnt"] = tradedf[amtstr].sum()
    result["avgdeltaabs"] = (tradedf[amtstr] * tradedf["deltaabs"]).sum() / tradedf[amtstr].sum()

    return result, result_in

def save_results(savepath, result, result_in, owndf, trademntdf, trademntprice_abs_df, lendmntdf):
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    result.to_csv(f"{savepath}/网络指标.csv", encoding="GBK")
    result_in.to_csv(f"{savepath}/机构指标.csv", encoding="GBK")
    owndf.to_csv(f"{savepath}/机构持有量.csv", encoding="GBK")
    trademntdf.to_csv(f"{savepath}/机构交易量.csv", encoding="GBK")
    trademntprice_abs_df.to_csv(f"{savepath}/日均成交偏差.csv", encoding="GBK")
    lendmntdf.to_csv(f"{savepath}/机构借出量.csv", encoding="GBK")
