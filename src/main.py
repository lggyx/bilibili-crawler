from src.utils.cookie_utils import get_cookies


def get_video_info(video_id):
    """
    url:https://api.bilibili.com/x/web-interface/wbi/view
    :param video_id: 视频id
    :return: 视频信息"""
    import requests

    url = "https://api.bilibili.com/x/web-interface/wbi/view"
    params = {
        'bvid': video_id
    }
    cookie = get_cookies()
    headers = {
        # Referer 防盗链 告诉服务器你请求链接是从哪里跳转过来的
        "Referer": "https://www.bilibili.com/video/"+video_id,
        # User-Agent 用户代理, 表示浏览器/设备基本身份信息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(url, params=params, headers=headers, cookies=cookie)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching video info: {e}")
        return None

