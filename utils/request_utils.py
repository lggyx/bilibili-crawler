import requests

from config.config_loader import load_config
from utils.cookie_utils import get_cookies

config = load_config()

def request_mine(url,params):
    """
    requests 集成类
    :param url:
    :param params:
    :return:
    """
    headers = {"User-Agent": config['crawler']['user_agent'],}
    cookies = get_cookies()
    try:
        response = requests.get(url, params=params, headers=headers, cookies=cookies)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching video info: {e}")
        return None