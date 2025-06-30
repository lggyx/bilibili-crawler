from src.analyzer.music_rank_analyzer import musicRankAnalyzer
from src.analyzer.video_danmaku_analyzer import videoDanmakuAnalyzer
from src.crawler.bilibili_login_crawler import bilibiliLoginCrawler
from src.crawler.music_rank_crawler import musicRankCrawler
from src.crawler.video_danmaku_crawler import videoDanmakuCrawler
from src.preprocessing.music_rank_preprocessing import musicRankPreprocessing
from src.preprocessing.video_danmaku_preprocessing import videoDanmakuPreprocessing

from src.utils.logger import get_log
log=get_log("main")
def login():
    bilibiliLoginCrawler.run_crawler()
def music_rank_crawler():
    musicRankCrawler.run_crawler()
def music_rank_preprocessing():
    musicRankPreprocessing.run_all_preprocessing()
def music_rank_analyzer():
    musicRankAnalyzer.run_analyzer()
    # 运行Jupyter Notebook并用浏览器打开分析报告
    import os
    import webbrowser
    notebook_path = os.path.join(os.path.dirname(__file__), 'src', 'analyzer', 'music_rank_analysis_report.ipynb')
    # 自动执行Notebook所有代码块
    os.system(f'jupyter nbconvert --to notebook --execute "{notebook_path}" --inplace')
    # 启动jupyter notebook服务（后台）
    os.system(f'jupyter notebook "{notebook_path}"')
    # 自动用默认浏览器打开
    webbrowser.open(f'file://{notebook_path}')

def video_danmaku_crawler(id):
    if id.startswith('BV'):
        # 处理BVID
        videoDanmakuCrawler.run_crawler(bvid=id)  
    elif id.isdigit():
        # 处理AID
        videoDanmakuCrawler.run_crawler(aid=id) 
    

def video_danmaku_preprocessing():
    videoDanmakuPreprocessing.run_preprocessing()

def video_danmaku_analyzer():
    videoDanmakuAnalyzer.run_analyzer()
    # 运行Jupyter Notebook并用浏览器打开分析报告
    import os
    import webbrowser
    notebook_path = os.path.join(os.path.dirname(__file__), 'src', 'analyzer', 'video_danmaku_analysis_report.ipynb')
    # 自动执行Notebook所有代码块
    os.system(f'jupyter nbconvert --to notebook --execute "{notebook_path}" --inplace')
    # 启动jupyter notebook服务（后台）
    os.system(f'jupyter notebook "{notebook_path}"')
    # 自动用默认浏览器打开
    webbrowser.open(f'file://{notebook_path}')

def main():
    argparse = __import__('argparse')
    parser = argparse.ArgumentParser(description='Bilibili 数据分析工具')
    parser.add_argument('--type', choices=['login', 'music_rank', 'video_danmaku'], required=True, help='指定分析类型：login、music_rank 或 video_danmaku')
    parser.add_argument('--crawl', action='store_true', help='爬取数据')
    parser.add_argument('--preprocess', action='store_true', help='预处理数据')
    parser.add_argument('--analyze', action='store_true', help='分析数据并生成可视化报告')
    parser.add_argument('--id', type=str, help='视频弹幕分析时需指定视频id')
    args = parser.parse_args()
    # 只根据type分流
    if args.type == 'login':
        login()
    elif args.type == 'music_rank':
        if args.crawl:
            music_rank_crawler()
        if args.preprocess:
            music_rank_preprocessing()
        if args.analyze:
            music_rank_analyzer()
    elif args.type == 'video_danmaku':
        if args.crawl and not args.id:
            log.error('使用 --type video_danmaku --crawl 时，必须通过 --id 指定视频id！')
            exit(1)
        if args.crawl and args.id:
            id = args.id
            video_danmaku_crawler(id)
        if args.preprocess:
            video_danmaku_preprocessing()
        if args.analyze:
            video_danmaku_analyzer()

if __name__ == '__main__':
    main()