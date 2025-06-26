"""
TODO 存储数据的方法
"""
import json
import os.path

from config.logger import get_logger
from utils.time_utils import get_time_str

path=os.path.dirname(__file__).split("\\utils")[0]+"\\data\\"
def write_file_to_raw(filename,data):
    """
    将爬取的原始数据写入本地
    :param filename:
    :param data:
    :return:
    """
    with open(path+"\\raw\\"+filename+get_time_str()+".json", 'w', encoding='utf-8') as f:
        json.dump(data,f)
    log = get_logger("bilibili-crawler")
    log.info(f"当前存储的文件为：{filename+get_time_str()}.json")
    return path+filename+get_time_str()+".json"

def write_file_to_processed(filename, data):
    """
    将清洗后的数据写入本地
    :param filename:
    :param data:
    :return:
    """
    with open(path+"\\processed\\"+filename, 'w', encoding='utf-8') as f:
        json.dump(data,f)
    log = get_logger("bilibili-cleaner")
    log.info(f"当前存储的文件为：{filename+get_time_str()}.json")
    return path+filename+get_time_str()+".json"


def write_file_to_mysql(filename,data):
    """
    将爬取的原始数据写入MySql
    :param filename:
    :param data:
    :return:
    """
    pass