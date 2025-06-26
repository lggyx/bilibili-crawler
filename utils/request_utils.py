import requests
import random
import time

from config.config_loader import load_config
from utils.cookie_utils import get_cookies

config = load_config()

USER_AGENTS = [
    config['crawler'].get('user_agent', ''),
    # 可在此添加更多User-Agent
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
]

def request_mine(url, params, max_retries=3, timeout=10):
    """
    requests 集成类，增加反爬虫措施
    :param url:
    :param params:
    :param max_retries: 最大重试次数
    :param timeout: 超时时间
    :return:
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    cookies = get_cookies()
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"[尝试{attempt+1}/{max_retries}] Error fetching video info: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(1, 3))  # 随机延迟1-3秒
            else:
                return None