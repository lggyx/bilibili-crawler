from src.crawler.bilibili_login_crawler import bilibiliLoginCrawler
from src.preprocessing.music_rank_preprocessing import musicRankPreprocessing


def login():
    bilibiliLoginCrawler.run_crawler()
def music_rank():
    # musicRankCrawler.run_crawler()
    musicRankPreprocessing.run_all_preprocessing()
if __name__ == '__main__':
    music_rank()