import json
import random
# import pandas as pd
# from collections import defaultdict

def generate_color_map(flat_list, seed=42, saturation=40, lightness=70):
    """
    为给定的机构列表生成颜色映射。

    参数：
    - flat_list (list): 包含机构名称的列表。
    - seed (int): 随机种子，默认值为 42。
    - saturation (int): 饱和度，默认值为 40。
    - lightness (int): 亮度，默认值为 70。

    返回：
    - dict: 机构名称到 RGB 颜色的映射字典。
    """
    organizations = {item['name'] for item in flat_list}
    num_organizations = len(organizations)
    hue_step = 360 / num_organizations
    hsl_colors = [(i * hue_step, saturation, lightness) for i in range(num_organizations)]

    random.seed(seed)
    random.shuffle(hsl_colors)
    
    return {org: hsl_to_rgb(*hsl_colors[i]) for i, org in enumerate(organizations)}

def hsl_to_rgb(h, s, l):
    h /= 360
    s /= 100
    l /= 100
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            t = (t + 1) % 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return int(r * 255), int(g * 255), int(b * 255)

def generate_data_chain_json(flat_list, output_file):
    """
    根据给定的平面列表生成 JSON 文件。

    参数：
    - flat_list (list): 包含数据的列表。
    - output_file (str): 输出文件的路径。
    """
    nodes = [{
        'name': item['name'],
        'time_dl': item['time_dl'],
        'volume': item['volume'],
        'price': item['price'],
        'xy_coordinates': item['xy_coordinates'],
        'color': item['color']
    } for item in flat_list]
    
    tangleLayout = {'bundles': [{"links": []}], 'nodes': nodes}
    with open(output_file, "w") as json_file:
        json.dump(tangleLayout, json_file, indent=4)

def convert_timestamp_to_string(all_paths_with_xy):
    """
    将数据中的时间戳字段转换为字符串格式，并返回转换后的副本。

    参数：
    - all_paths_with_xy (list): 包含路径数据的列表。

    返回：
    - list: 转换后的副本列表。
    """
    def convert_item(item):
        item_copy = item.copy()
        item_copy['time_dl'] = item['time_dl'].strftime('%Y-%m-%d %H:%M:%S')
        return item_copy
    
    return [[convert_item(item) for item in path] for path in all_paths_with_xy]

def add_color_to_items(flat_list, color_map):
    """
    给 flat_list 中的每个项添加颜色项。

    参数：
    - flat_list (list): 包含项的列表。
    - color_map (dict): 包含机构颜色映射的字典。

    返回：
    - list: 添加颜色项后的项列表。
    """
    return [{
        'name': item['name'],
        'time_dl': item['time_dl'],
        'volume': item['volume'],
        'price': item['price'],
        'xy_coordinates': item['xy_coordinates'],
        'color': color_map.get(item['name'], (255, 255, 255))
    } for item in flat_list]
