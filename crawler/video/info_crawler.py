"""
TODO 视频基本信息
"""
from utils.request_utils import request_mine


def get_video_info_view(aid,bvid):
    """
    获取视频详细信息(web端)
    认证方式：Cookie(SESSDATA)   限制游客访问的视频需要登录
    :param aid:num	稿件avid	必要(可选)	avid与bvid任选一个
    :param bvid:str	稿件bvid	必要(可选)	avid与bvid任选一个
    :return:
    """
    url="https://api.bilibili.com/x/web-interface/wbi/view"
    params={"aid": aid, "bvid": bvid}
    return request_mine(url,params)

def get_video_info_detail(aid,bvid,need_elec):
    """
    获取视频超详细信息(web端)
    认证方式：Cookie(SESSDATA)   鉴权方式：Wbi 签名   限制游客访问的视频需要登录
    :param aid:num	稿件avid	必要(可选)	avid与bvid任选一个
    :param bvid:str	稿件bvid	必要(可选)	avid与bvid任选一个
    :param need_elec:num	是否获取UP主充电信息	非必要	0：否1：是
    :return:
    """
    url="https://api.bilibili.com/x/web-interface/view/detail"
    params={"aid": aid, "bvid": bvid, "need_elec": need_elec}
    return request_mine(url,params)

def get_video_info_desc(aid,bvid):
    """
    获取视频简介
    :param aid:num	稿件avid	必要（可选）	avid与bvid任选一个
    :param bvid:str	稿件bvid	必要（可选）	avid与bvid任选一个
    :return:
    """
    url="https://api.bilibili.com/x/web-interface/archive/desc"
    params={"aid": aid, "bvid": bvid}
    return request_mine(url,params)