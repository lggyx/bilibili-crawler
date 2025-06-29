import json
import os
from datetime import datetime

from requests.cookies import RequestsCookieJar

from src.utils.logger import get_log

path=os.path.dirname(__file__).split("\\src")[0]+"\\data\\"
def write_file_to_raw(filename, data):
    """
    将爬取的原始数据写入本地
    :param filename:
    :param data:
    :return:
    """

    # 拼接文件路径
    file_path = os.path.join(path, "raw", filename + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json")
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    # 记录日志
    log = get_log("write_file_to_raw")
    log.info(f"当前存储的文件为：{file_path}")

    return file_path
def load_cookies():
    log = get_log("load_cookies")
    log.info('Loading cookies...')
    filepath = os.path.dirname(__file__).split("\\src")[0] + "\\data\\cookies\\cookies.json"
    if not os.path.exists(filepath):
        log.info('cookies.json does not exist')
        return None
    log.info('cookies.json exists')
    jar = RequestsCookieJar()
    with open(filepath, "r") as fp:
        if fp:
            cookies = json.load(fp)
            for cookie in cookies:
                jar.set(cookie['name'], cookie['value'])
                return jar
        else:
            log.info('cookies.json is empty')
        return None
