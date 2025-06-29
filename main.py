from src.crawler.bilibili_login_crawler import bilibiliLoginCrawler
from src.crawler.music_rank_crawler import musicRankCrawler


def login():
    bilibiliLoginCrawler.run_crawler()
def music_rank():
    musicRankCrawler.rank_crawler()

if __name__ == '__main__':
    music_rank()