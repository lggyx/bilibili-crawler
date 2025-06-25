import requests

from src.utils.cookie_utils import get_cookies


def request_mine(url,params):
    """
    requests 集成类
    :param url:
    :param params:
    :return:
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    cookies = get_cookies()
    try:
        response = requests.get(url, params=params, headers=headers, cookies=cookies)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching video info: {e}")
        return None