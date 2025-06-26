"""
TODO 主程序，可以执行的操作如下：
    1.登录
    2.爬取往期所有音乐排行榜单数据，数据清洗，分析生成云图，数据表等，生成热点话题走向
    3.爬取各分区视频排行榜单数据，数据清洗，分析生成云图，数据表等，生成热点话题走向
    4.爬取单一视频数据弹幕等，数据清洗，分析生成对应的数据展示
"""
import argparse
import time

import crawler.audio.rank_crawler
from analyzer.audio.run_audio_analysis import run_audio_analysis
from cleaner.audio.rank_cleaner import rank_cleaner
from config.logger import get_logger
from utils.cookie_utils import write_cookies

log=get_logger("bilibili-crawler")


def login():
    write_cookies()

def music_rank():
    # 爬取往期所有音乐排行榜单数据，数据清洗，分析生成云图，数据表等，生成热点话题走向
    log.info("开始爬取数据")
    # 爬取数据、存储原始数据
    crawler.audio.rank_crawler.rank_crawler()
    log.info("爬取数据完成")
    log.info("开始数据清洗")
    rank_cleaner()
    log.info("数据清洗完成")
    log.info("生成数据分析报告中")
    # 生成分析报告，文档等，生成完成跳转对应的文件夹
    run_audio_analysis()
    log.info("数据分析报告已生成")


def video_rank(area=None):
    # 爬取各分区视频排行榜单数据，数据清洗，分析生成云图，数据表等，生成热点话题走向
    # area: 分区参数，默认为None，表示全部分区
    log.info("开始爬取数据")
    # 爬取数据、存储原始数据
    time.sleep(2)
    log.info("爬取数据完成")

    log.info("开始数据清洗")
    # 原始数据清洗整理，变成可以使用的数据
    time.sleep(2)
    log.info("数据清洗完成")

    log.info("生成数据分析报告中")
    # 生成分析报告，文档等，生成完成跳转对应的文件夹
    log.info("数据分析报告已生成")

def video_danmaku():
    # 爬取单一视频数据弹幕等，数据清洗，分析生成对应的数据展示
    log.info("开始爬取数据")
    # 爬取数据、存储原始数据
    time.sleep(2)
    log.info("爬取数据完成")

    log.info("开始数据清洗")
    # 原始数据清洗整理，变成可以使用的数据
    time.sleep(2)
    log.info("数据清洗完成")

    log.info("生成数据分析报告中")
    # 生成分析报告，文档等，生成完成跳转对应的文件夹
    log.info("数据分析报告已生成")

def main():
    parser = argparse.ArgumentParser(description="Bilibili Crawler")
    parser.add_argument('--mode', type=str, required=True, help='运行模式: login, music_rank, video_rank, video_danmaku')
    parser.add_argument('--area', type=str, default=None, help='分区参数，仅在video_rank模式下使用，分区ID参照doc')
    parser.add_argument('--storage', type=str, default=None, help='数据存储方式   1:静态json存储    2:mysql')
    args = parser.parse_args()

    if args.mode == 'login':
        login()
    elif args.mode == 'music_rank':
        music_rank()
    elif args.mode == 'video_rank':
        video_rank(area=args.area)
    elif args.mode == 'video_danmaku':
        video_danmaku()
    else:
        print(f"未知的mode: {args.mode}")

if __name__ == "__main__":
    main()