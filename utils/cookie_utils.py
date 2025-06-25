"""
TODO Cookie工具类
    具体操作是检查本地是否存在cookie，如果不存在就利用selenium获取
    除此之外就是提供读取本地Cookie的方法
"""
import os

from requests.cookies import RequestsCookieJar
from selenium import webdriver
import json

filepath=os.path.dirname(__file__).split("\\utils")[0]+"\\data\\cookies\\cookies.json"
def write_cookies():
    """
    登录，写入cookies
    :return:
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://www.bilibili.com/')
    input("登录后输入回车")
    dict_cookies = driver.get_cookies()  # 获取list的cookies
    json_cookies = json.dumps(dict_cookies)  # 转换成字符串保存
    with open(filepath, 'w') as f:
        f.write(json_cookies)
    print('cookies保存成功！')

def get_cookies():
    """
    cookies获取方法
    :return:
    """
    jar = RequestsCookieJar()
    with open(filepath, "r") as fp:
        cookies = json.load(fp)
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'])
    return jar