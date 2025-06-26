"""
TODO 存储数据的方法
"""
import json
import os.path

from config.logger import get_logger
from utils.time_utils import get_time_str

path=os.path.dirname(__file__).split("\\utils")[0]+"\\data\\"
import os
import json
from config.logger import get_logger
from utils.time_utils import get_time_str

def write_file_to_raw(filename, data):
    """
    将爬取的原始数据写入本地
    :param filename:
    :param data:
    :return:
    """

    
    # 拼接文件路径
    file_path = os.path.join(path, "raw", filename + get_time_str() + ".json")
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    # 记录日志
    log = get_logger("bilibili-crawler")
    log.info(f"当前存储的文件为：{file_path}")
    
    return file_path

def write_file_to_processed(filename, data):
    """
    将清洗后的数据写入本地
    :param filename:
    :param data:
    """

    
    # 拼接文件路径
    file_path = os.path.join(path, "processed", filename + get_time_str() + ".json")
    # 确保数据目录存在
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    # 记录日志
    log = get_logger("bilibili-crawler")
    log.info(f"当前存储的文件为：{file_path}")
    
    return file_path


def write_file_to_mysql(filename,data):
    """
    将爬取的原始数据写入MySql
    :param filename:
    :param data:
    :return:
    """
    pass