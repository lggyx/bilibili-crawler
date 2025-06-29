import json
import os
import re
import time

from src.config.config import config
from src.utils.logger import get_log
from src.utils.requester import request_mine
from src.utils.storager import write_file_to_raw


def get_audio_rank_detail(list_id, csrf):
    """
    查询音频榜单单期信息
    :param list_id: 榜单 id    见 获取音频榜单每期列表   必要
    :param csrf:    CSRF Token（位于cookie）    非必要
    :return:
    """
    url = "https://api.bilibili.com/x/copyright-music-publicity/toplist/detail"
    params = {"list_id": list_id, "csrf": csrf}
    return request_mine(url, params)


def get_audio_rank_all_period(list_type, csrf):
    """
    获取音频榜单每期列表
    :param list_type:   榜单类型    1：热榜2：原创榜   必要
    :param csrf:    CSRF Token（位于cookie）    非必要
    :return:
    """
    url = "https://api.bilibili.com/x/copyright-music-publicity/toplist/all_period"
    params = {"list_type": list_type, "csrf": csrf}
    return request_mine(url, params)


def get_audio_rank_music_list(list_id, csrf):
    """
    获取音频榜单单期内容
    :param list_id: 榜单 id    见 获取音频榜单每期列表   必要
    :param csrf:    CSRF Token（位于cookie）    非必要
    :return:
    """
    url = "https://api.bilibili.com/x/copyright-music-publicity/toplist/music_list"
    params = {"list_id": list_id, "csrf": csrf}
    return request_mine(url, params)


class MusicRankCrawler:
    def __init__(self):
        self.log = get_log("MusicRankCrawler")
        self.AUDIO_RANK_ALL_PERIOD_URL = config.get("CRAWLER", "AUDIO_RANK_ALL_PERIOD_URL")
        self.AUDIO_RANK_DETAIL_URL = config.get("CRAWLER", "AUDIO_RANK_DETAIL_URL")
        self.AUDIO_RANK_MUSIC_LIST_URL = config.get("CRAWLER", "AUDIO_RANK_MUSIC_LIST_URL")
    def run_crawler(self):
        write_file_to_raw("音乐榜单-热榜-", get_audio_rank_all_period(1, None))
        time.sleep(3)
        raw_data_dir = os.path.dirname(__file__).split("\\src")[0] + "\\data\\raw"  # 假设原始数据存放在raw目录下
        pattern = re.compile(r"^音乐榜单-热榜-.*\.json$")
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
            for key, value in data_json['data']['list'].items():
                self.log.info(f"年度:{key}")
                for item in value:
                    write_file_to_raw(f"音频榜单单期信息-热榜-第{item["priod"]}期-{key}年度-",
                                      get_audio_rank_music_list(item["ID"], None))

musicRankCrawler = MusicRankCrawler()
