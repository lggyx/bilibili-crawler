import requests
import random
import time

from src.config.config import config
from src.utils.logger import get_log

USER_AGENTS = [
    config.get("CRAWLER", "USER_AGENT"),
    # 可在此添加更多User-Agent
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
]
log=get_log("request_mine")
def request_mine(url, params=None,cookies=None):
    """
    requests 集成类，增加反爬虫措施
    :param cookies:
    :param url:
    :param params:
    :return:
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    for attempt in range(int(config.get("CRAWLER", "MAX_RETRIES"))):
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies,timeout=int(config.get("CRAWLER", "TIME_OUT")))
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            log.error(f"[尝试{attempt+1}/{int(config.get("CRAWLER", "MAX_RETRIES"))}] Error fetching video info: {e}")
            if attempt < int(config.get('CRAWLER', 'MAX_RETRIES')) - 1:
                time.sleep(random.uniform(1, 3))  # 随机延迟1-3秒
            else:
                return None
    return None