"""
TODO 音乐榜单爬虫
"""
from src.utils.request_utils import request_mine


# TODO 音乐榜单
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
