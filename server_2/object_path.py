from datetime import timedelta
from collections import defaultdict

class Trade:
    def __init__(self, buyer, seller, volume, price, time, time_dl):
        self.buyer = buyer  # 买方
        self.seller = seller  # 卖方
        self.volume = volume  # 交易量
        self.price = price  # 价格
        self.time = time  # 交易时间
        self.time_dl = time_dl  # 交易时间

class Path:
    def __init__(self, source, target, start_time, end_time, path):
        self.source = source
        self.target = target
        self.start_time = start_time
        self.end_time = end_time
        self.path = path  # 路径属性
        self.length = self.calculate_length()  # 路径长度

        self.profit = self.calculate_profit_rate()  # 路径盈利情况
        self.institution_counts = self.count_institution_repeats()  # 机构重复次数
        self.price_std_dev = self.calculate_price_std_dev()  # 价格标准差
        self.price_changes = self.calculate_price_change_rate()  # 价格变化率

        self.profit_anomaly_score = self.calculate_profit_anomaly_score()*self.length  # 路径盈利异常分数
        self.institution_counts_anomaly_score = self.calculate_institution_counts_anomaly_score()
        self.price_std_dev_anomaly_score = self.calculate_price_std_dev_anomaly_score()
        self.price_change_anomaly_score = self.calculate_price_change_anomaly_score()

    def calculate_price_change_rate(self):
        price_changes = []
        for i in range(1, len(self.path)):
            price_change_rate = (self.path[i].price - self.path[i-1].price) / self.path[i-1].price
            price_changes.append(price_change_rate)
        return price_changes

    def count_institution_repeats(self):
        institution_counts = {}
        for trade in self.path:
            if trade.seller in institution_counts:
                institution_counts[trade.seller] += 1
            else:
                institution_counts[trade.seller] = 1
            if trade.buyer in institution_counts:
                institution_counts[trade.buyer] += 1
            else:
                institution_counts[trade.buyer] = 1
        return institution_counts

    def calculate_price_std_dev(self):
        prices = [trade.price for trade in self.path]
        return np.std(prices)

    def calculate_profit_rate(self):
        profit_dict = {}
        for trade in self.path:
            institutions = [trade.buyer, trade.seller]
            for institution in institutions:
                if institution not in profit_dict:
                    profit_dict[institution] = {'profit': 0, 'loss': 0}

        # 计算盈利和亏损
        for i in range(self.length - 1):
            trade = self.path[i]
            next_trade = self.path[i + 1]

            profit = trade.volume * (next_trade.price - trade.price)
            if trade.buyer in profit_dict:
                profit_dict[trade.buyer]['profit'] += max(profit, 0)
                profit_dict[trade.buyer]['loss'] += min(profit, 0)

        return profit_dict

    def calculate_length(self):
        # 计算路径长度
        return len(self.path)

    def can_connect_to(self, other):
        # 检查是否可以连接到另一个路径
        time_difference = abs((other.start_time - self.end_time).total_seconds())
        one_day = timedelta(days=1).total_seconds()
        if self.target == other.source and time_difference < one_day:
            # 获取上一条链路的最后一笔交易的量
            last_trade_volume = self.path[-1].volume
            # 获取下一个链路的第一笔交易的量
            next_trade_volume = other.path[0].volume
            # 确保上一条链路的最后一笔交易的量大于下一个链路第一笔交易的量
            return last_trade_volume >= next_trade_volume
        return False

    def connect_to(self, other):
        # 将当前路径连接到另一个路径
        if self.can_connect_to(other):
            new_path = self.path + other.path  # 合并路径
            source = self.source
            target = other.target
            start_time = self.start_time
            end_time = other.end_time
            # new_length = self.length + other.length  # 更新长度
            # new_profit = self.profit + other.profit  # 更新盈利情况
            # new_trade_volume = self.trade_volume + other.trade_volume  # 合并交易量
            # new_price_match = self.price_match + other.price_match  # 合并价格匹配度
            return Path(source, target, start_time, end_time, new_path)
        else:
            return False

    def calculate_profit_anomaly_score(self):
        # 计算路径的盈利总和
        # total_profit = sum(sum(institution['profit'] for institution in profit_info.values()) for profit_info in self.profit.values())
        # sum(institution['profit'] for institution in profit_info.values()) 
        profit_info_list = [profit_info for profit_info in self.profit.values()]
        all_profit = [item["profit"] for item in profit_info_list]
        all_loss = [item["loss"] for item in profit_info_list]

        # 计算盈利总和与平均盈利的差异
        average_profit = sum(all_profit) / len(self.profit)
        average_loss = sum(all_loss) / len(self.profit)

        anomaly_score_profit = max(all_profit) - average_profit
        anomaly_score_loss = max(all_loss) - average_loss

        return anomaly_score_profit + anomaly_score_loss

    def calculate_price_change_anomaly_score(self):
        suspicious_pattern_score = 0
        consecutive_small_changes = 0
        significant_changes = 0
        for i in range(len(self.price_changes) - 1):
            current_change = self.price_changes[i]
            next_change = self.price_changes[i + 1]
            if abs(current_change) < 0.05:  # 假设小于0.05的变化被认为是连续小变化
                consecutive_small_changes += 1
            elif abs(current_change) >= 0.05 and abs(next_change) >= 0.05:  # 假设大于等于0.05的变化并连续出现两次以上认为是显著变化
                significant_changes += 1
        if consecutive_small_changes >= 3 and significant_changes >= 2:
            suspicious_pattern_score += 1  # 认为出现了可疑的价格变化模式

        return suspicious_pattern_score

    def calculate_institution_counts_anomaly_score(self):
        total_counts = sum(self.institution_counts.values())
        average_count = total_counts / len(self.institution_counts)
        max_count = max(self.institution_counts.values())
        anomaly_score = max_count - average_count
        return anomaly_score

    def calculate_price_std_dev_anomaly_score(self):
        # 假设异常度是与路径上价格的标准差的相对差异
        # average_std_dev = np.mean([path.price_std_dev for path in self.path])
        # relative_diff = abs(self.price_std_dev - average_std_dev) / average_std_dev
        return 0

    def __str__(self):
        # 打印路径信息
        path_info = f"Path from {self.source} to {self.target}:\n"
        path_info += f"Start Time: {self.start_time}\n"
        path_info += f"End Time: {self.end_time}\n"
        path_info += "Path Trades:\n"
        for i, trade in enumerate(self.path):
            path_info += f"  Trade {i + 1}:\n"
            path_info += f"    Seller: {trade.seller} Buyer: {trade.buyer} \n"
            path_info += f"    Volume: {trade.volume}\n"
            path_info += f"    Price: {trade.price}\n"
            path_info += f"    Time_dl: {trade.time_dl}\n"
        path_info += f"Profit Anomaly Score: {self.profit_anomaly_score}\n"
        path_info += f"Institution Counts Anomaly Score: {self.institution_counts_anomaly_score}\n"
        path_info += f"Price Standard Deviation Anomaly Score: {self.price_std_dev_anomaly_score}\n"
        path_info += f"Price Change Anomaly Score: {self.price_change_anomaly_score}\n"
        return path_info

    def __lt__(self, other):
        # 调节不同异常度分数的比例
        # 假设赋予不同分数的权重
        profit_weight = 0.4*100
        institution_counts_weight = 0.2*200
        price_std_dev_weight = 0.2*100
        price_change_weight = 0.2*100
        length_weight = 0.2*300

        # 综合考虑各项异常度分数
        self_total_score = (
            profit_weight * self.profit_anomaly_score +
            institution_counts_weight * self.institution_counts_anomaly_score +
            price_std_dev_weight * self.price_std_dev_anomaly_score +
            price_change_weight * self.price_change_anomaly_score +
            length_weight * self.length
        )
        other_total_score = (
            profit_weight * other.profit_anomaly_score +
            institution_counts_weight * other.institution_counts_anomaly_score +
            price_std_dev_weight * other.price_std_dev_anomaly_score +
            price_change_weight * other.price_change_anomaly_score +
            length_weight * self.length
        )
        return self_total_score > other_total_score

def create_path_from_trade_list(key, trade_list):
    source, target = key
    start_time = trade_list[0].time
    end_time = trade_list[-1].time
    path = trade_list
    return Path(source, target, start_time, end_time, path)

def create_trade_from_edge_attrs(edge_attrs):
    buyer = edge_attrs['buyer']
    seller = edge_attrs['seller']
    volume = edge_attrs['volume']
    price = edge_attrs['price']
    time = edge_attrs['time']  # 使用 'time_dl' 键获取交易时间，而不是 'time'
    time_dl = edge_attrs['time_dl']
    # 创建 Trade 对象并返回
    return Trade(buyer, seller, volume, price, time, time_dl)

def summarize_paths(path_list):
    # 遍历 path_list 并生成路径汇总信息
    for index, path in enumerate(path_list):
        print(f"Path {index + 1} Summary:")
        print(f"Source: {path.source}")
        print(f"Target: {path.target}")
        print(f"Start Time: {path.start_time}")
        print(f"End Time: {path.end_time}")
        print(f"Length: {path.length}")
        print(f"Trade Count: {len(path.path)}")
        print(f"Profit: {path.profit}")
        print(f"Price Changes: {path.price_changes}")
        print(f"Institution Counts: {path.institution_counts}")
        print(f"Price Standard Deviation: {path.price_std_dev}")

        # 打印每笔交易的信息
        print("Path Trades:")
        for i, trade in enumerate(path.path):
            print(f"  Trade {i + 1}:")
            print(f"    Seller: {trade.seller}")
            print(f"    Buyer: {trade.buyer}")
            print(f"    Volume: {trade.volume}")
            print(f"    Price: {trade.price}")
            print(f"    Time_dl: {trade.time_dl}")
        trade_chain = f"{path.path[0].seller} -> {path.path[0].buyer} -> " + " -> ".join([f"{trade.buyer}" for trade in path.path[1:]])
        # trade_chain = " -> ".join([f"{trade.seller} -> {trade.buyer}" for trade in path.path])
        print(trade_chain)
        trade_chain_time = " -> ".join([ str(trade.time_dl) for trade in path.path])
        print(trade_chain_time)
        path_info = f"\n"
        path_info += f"Profit Anomaly Score: {path.profit_anomaly_score}\n"
        path_info += f"Institution Counts Anomaly Score: {path.institution_counts_anomaly_score}\n"
        path_info += f"Price Standard Deviation Anomaly Score: {path.price_std_dev_anomaly_score}\n"
        path_info += f"Price Change Anomaly Score: {path.price_change_anomaly_score}\n"
        print(path_info)
        print("")

def connect_paths(path_list):
    connected_paths = path_list[:]  # 存储连接后的路径，初始化为 path_list 的拷贝
    connected_paths_set = set()  # 使用哈希集合存储已连接的路径
    while True:
        new_connected_paths = []  # 存储本轮新连接的路径
        for path in path_list:
            for other_path in path_list:
                if path.can_connect_to(other_path):
                    # 构建路径的哈希
                    connected_path_hash = tuple((trade.buyer, trade.seller, trade.time_dl) for trade in path.path + other_path.path[1:])
                    # 判断路径是否已经连接过
                    if connected_path_hash not in connected_paths_set:
                        # 连接路径
                        connected_path = path.connect_to(other_path)
                        # 判断交易链路是否可行
                        if connected_path:
                            new_connected_paths.append(connected_path)
                            # 将路径的哈希添加到已连接路径的集合中
                            connected_paths_set.add(connected_path_hash)
        if not new_connected_paths:  # 如果没有新路径连接，则退出循环
            break
        connected_paths.extend(new_connected_paths)  # 将新连接的路径加入到 connected_paths 中
    return connected_paths

def process_all_paths(G_sorted_data, all_paths):
    """
    根据给定的多重有向图和路径字典，处理所有路径并连接它们。
    Args:
        G_sorted_data (nx.MultiDiGraph): 多重有向图对象。
        all_paths (dict): 包含所有路径的字典，键为节点对，值为路径列表。

    Returns:
        list: 处理后的连接路径列表。
    """
    path_list = []
    # 遍历所有路径
    for key, value_list in all_paths.items():
        for path in all_paths[key]:
            # 创建交易列表
            trade_list = [create_trade_from_edge_attrs(G_sorted_data.get_edge_data(u, v, time)) for u, v, time in path]
            # 创建路径并添加到路径列表中
            path_list.append(create_path_from_trade_list(key, trade_list))
    # 连接路径并返回结果
    return connect_paths(path_list)

def filter_subsets(paths):
    filtered_paths = []
    for path1 in paths:
        if not any(is_sublist(path1.path, path2.path) for path2 in paths if path1 != path2):
            filtered_paths.append(path1)
    return sorted(filtered_paths)

def is_sublist(list1, list2):
    len1 = len(list1)
    len2 = len(list2)

    if len1 > len2:
        return False

    for i in range(len2 - len1 + 1):
        if all(item1.time_dl == item2.time_dl for item1, item2 in zip(list1, list2[i:i+len1])):
            return True
    return False
