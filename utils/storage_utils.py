"""
TODO 存储数据的方法
"""
import json
import os.path

from utils.time_utils import get_time_str

path=os.path.dirname(__file__).split("\\utils")[0]+"\\data\\raw\\"
def write_file_to_raw(filename,data):
    """
    将爬取的原始数据写入本地
    :param filename:
    :param data:
    :return:
    """
    with open(path+filename+get_time_str()+".json", 'w', encoding='utf-8') as f:
        json.dump(data,f)

    return path+filename+get_time_str()+".json"

def write_file_to_mysql(filename,data):
    """
    将爬取的原始数据写入MySql
    :param filename:
    :param data:
    :return:
    """
    pass