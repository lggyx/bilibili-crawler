import os
import json
import re

from utils.storage_utils import write_file_to_processed

# 定义需要保留的字段
fields_to_keep = [
    "music_id", "music_title", "singer", "album", "heat", "rank",
    "creation_aid", "creation_bvid", "creation_cover", "creation_title",
    "creation_nickname", "creation_duration", "creation_play"
]
# 数据清洗函数
def clean_data(data):
    cleaned_data = {"data": {"list": []}}
    for item in data["data"]["list"]:
        cleaned_item = {field: item[field] for field in fields_to_keep if field in item}
        cleaned_data["data"]["list"].append(cleaned_item)
    return cleaned_data

# 指定原始数据目录路径
directory = os.path.dirname(__file__).split("\\cleaner")[0]+"\\data\\raw"
# 使用正则表达式匹配以“音频榜单单期信息-热榜-第X期-YYYY年度-”开头的文件
file_prefix_pattern = re.compile(r"音频榜单单期信息-热榜-第\d+期-\d{4}年度-")

def is_target_file(item):
    return file_prefix_pattern.match(item) is not None

def rank_cleaner():
    # 遍历目录下所有符合前缀的json文件
    for filename in os.listdir(directory):
        if is_target_file(filename) and filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 清洗数据
                cleaned_data = clean_data(data)
                # 保存清洗后的数据
                write_file_to_processed(filename,cleaned_data)







