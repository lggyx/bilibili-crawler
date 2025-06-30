import json
import os

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService

from src.config.config import config
from src.utils.logger import get_log


class BilibiliLoginCrawler:
    def __init__(self):
        self.driver = None
        self.logger = get_log("BilibiliLoginCrawler")
        self.filepath = os.path.dirname(__file__).split("\\src")[0] + "\\data\\cookies\\cookies.json"
        self.driver_path = os.path.join(os.path.dirname(__file__).split("\\src")[0],"driver", "msedgedriver.exe")
    def login(self):
        self.logger.info("BilibiliLoginCrawler login")
        edge_options = webdriver.EdgeOptions()
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = EdgeService(executable_path=self.driver_path)
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.driver.get(config.get("CRAWLER","BILIBILI_LOGIN_URL"))
        self.driver.implicitly_wait(10)
        self.logger.warning("请手动登录Bilibili，登录成功后请按任意键继续...")
        input()
        self.logger.info("BilibiliLoginCrawler login success")
    def logout(self):
        self.driver.quit()
        self.logger.info("BilibiliLoginCrawler logout success")
    def set_cookies(self):
        dict_cookies = self.driver.get_cookies()  # 获取list的cookies
        json_cookies = json.dumps(dict_cookies)  # 转换成字符串保存
        cookies_dir = os.path.dirname(self.filepath)
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)
        with open(self.filepath, 'w') as f:
            f.write(json_cookies)
        self.logger.info('Cookies saved successfully!')

    def run_crawler(self):
        self.login()
        self.set_cookies()
        self.logout()
bilibiliLoginCrawler = BilibiliLoginCrawler()