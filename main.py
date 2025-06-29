from src.analyzer.music_rank_analyzer import musicRankAnalyzer
from src.crawler.bilibili_login_crawler import bilibiliLoginCrawler
from src.crawler.music_rank_crawler import musicRankCrawler
from src.preprocessing.music_rank_preprocessing import musicRankPreprocessing


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
    notebook_path = os.path.join(os.path.dirname(__file__), 'src', 'analyzer', 'analysis_report.ipynb')
    # 自动执行Notebook所有代码块
    os.system(f'jupyter nbconvert --to notebook --execute "{notebook_path}" --inplace')
    # 启动jupyter notebook服务（后台）
    os.system(f'jupyter notebook "{notebook_path}"')
    # 自动用默认浏览器打开
    webbrowser.open(f'file://{notebook_path}')


def main():
    argparse = __import__('argparse')
    parser = argparse.ArgumentParser(description='Bilibili 音乐榜单分析工具')
    parser.add_argument('--login', action='store_true', help='登录Bilibili账号')
    parser.add_argument('--crawl', action='store_true', help='爬取Bilibili音乐榜单数据')
    parser.add_argument('--preprocess', action='store_true', help='预处理音乐榜单数据')
    parser.add_argument('--analyze', action='store_true', help='分析音乐榜单数据并生成可视化报告')
    args = parser.parse_args()
    # 顺序执行所有命令
    if args.login and args.crawl and args.preprocess and args.analyze:
        login()
        music_rank_crawler()
        music_rank_preprocessing()
        music_rank_analyzer()
    else:
        if args.login:
            login()
        if args.crawl:
            music_rank_crawler()
        if args.preprocess:
            music_rank_preprocessing()
        if args.analyze:
            music_rank_analyzer()
if __name__ == '__main__':
    main()