from src.utils.requester import request_mine
from src.utils.storager import load_cookies
from src.utils.logger import get_log
from src.utils.storager import write_file_to_raw, write_file_to_raw_with_html
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService

class VideoDanmakuCrawler:
    def __init__(self):
        self.danmaku_data = []
        self.log=get_log("VideoDanmakuCrawler")
        self.driver_path = os.path.join(os.path.dirname(__file__).split("\\src")[0],"driver", "msedgedriver.exe")
        
    def get_video_info(self,aid=None,bvid=None):
        """
        https://api.bilibili.com/x/web-interface/wbi/view
        """
        url = "https://api.bilibili.com/x/web-interface/wbi/view"
        params = {"bvid": bvid, "aid": aid}
        cookies=load_cookies()
        if cookies==None:
            self.log.error("cookies is None，please login first")
            exit(1)
        return request_mine(url, params, cookies=cookies)
    def get_video_danmaku(self, cid):
        """
        https://comment.bilibili.com/{cid}.xml
        """
        url = f"https://comment.bilibili.com/{cid}.xml"
        edge_options = webdriver.EdgeOptions()
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging']) # 禁用日志
        edge_options.add_argument('--headless')  # 无头模式
        edge_options.add_argument('--disable-gpu')  # 禁用GPU加速
        service = EdgeService(executable_path=self.driver_path)
        driver =webdriver.Edge(service=service, options=edge_options)
        driver.get(url)
        driver.implicitly_wait(10)  # 等待页面加载
        # 等待页面加载完成后获取页面源代码
        data= driver.page_source
        driver.quit()  # 关闭浏览器
        return data  # 返回页面源代码
    def run_crawler(self,**kwargs):
        """
        :param kwargs: aid or bvid
        :return:
        """
        if "aid" in kwargs:
            self.danmaku_data = self.get_video_info(aid=kwargs["aid"])
        elif "bvid" in kwargs:
            self.danmaku_data = self.get_video_info(bvid=kwargs["bvid"])
        else:
            self.log.error("aid or bvid is required")
            exit(1)
        if self.danmaku_data is None:
            self.log.error("获取视频信息失败，请检查网络连接或视频ID是否正确")
            exit(1)
        else:
            self.log.info(f"视频标题：{self.danmaku_data.get('data', {}).get('title', '未知标题')}")
            write_file_to_raw(f"视频详细信息-{self.danmaku_data.get('data', {}).get('title', '未知标题')}-", self.danmaku_data)
        raw_data_dir = os.path.dirname(__file__).split("\\src")[0] + "\\data\\raw"  # 假设原始数据存放在raw目录下
        pattern = re.compile(r"^视频详细信息-.*\.json$")
        matched_files = [f for f in os.listdir(raw_data_dir) if pattern.match(f)]
        self.log.info(f"匹配到的文件: {matched_files}")
        if not matched_files:
            self.log.error("未找到匹配的原始数据文件")
            return
        latest_file = max(matched_files, key=lambda f: os.path.getmtime(os.path.join(raw_data_dir, f)))
        file_path = os.path.join(raw_data_dir, latest_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
            self.log.info(f"最新的原始数据文件: {latest_file}")
            self.log.info(f"视频标题：{data_json.get('data', {}).get('title', '未知标题')}")
            self.log.info(f"视频CID：{data_json.get('data', {}).get('cid', '未知ID')}")
            self.log.info(f"视频AID：{data_json.get('data', {}).get('bvid', '未知BVID')}")
        self.log.info("视频信息爬取完成，数据已保存到 raw 目录下")
        self.log.info("开始爬取视频弹幕数据...")
        if data_json.get('data', {}).get('cid', '未知ID') != '未知ID':
            response = self.get_video_danmaku(cid=data_json["data"]["cid"])
        if not response:
            self.log.error("获取视频弹幕数据失败，请检查网络连接或视频ID是否正确")
            exit(1)
        else:
            write_file_to_raw_with_html(f"视频弹幕数据-{data_json.get('data', {}).get('title', '未知标题')}-", response)
            self.log.info("视频弹幕数据爬取完成，数据已保存到 raw 目录下")
videoDanmakuCrawler = VideoDanmakuCrawler()
