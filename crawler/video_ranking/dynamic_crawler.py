"""
TODO 分区最新视频
"""
from utils.request_utils import request_mine


def get_video_ranking_region(pn, ps, rid):
    """
    获取分区最新视频列表
    :param pn:页码	非必要	默认为1
    :param ps:每页项数	非必要	默认为14, 留空为5
    :param rid:目标分区tid	必要
    :return:
    """
    url="https://api.bilibili.com/x/web-interface/dynamic/region"
    params={"pn":pn,"ps":ps,"rid":rid}
    return request_mine(url, params)


def get_video_ranking_tag(ps,pn,rid,tag_id):
    """
    获取分区标签近期互动列表
    :param ps:num	视频数	非必要	默认为14, 留空为5
    :param pn:num	列数	非必要	留空为1
    :param rid:num	目标分区id	必要	参见视频分区一览
    :param tag_id:num	目标标签id	必要
    :return:
    """
    url="https://api.bilibili.com/x/web-interface/dynamic/tag"
    params={"pn":pn,"ps":ps,"rid":rid,"tag_id":tag_id}
    return request_mine(url, params)