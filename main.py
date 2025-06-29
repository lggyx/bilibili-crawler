#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
B站音频榜单爬虫主程序。

该程序用于爬取B站音频榜单数据，并进行数据清洗和分析。
"""

import os
import time
from src.utils.logger import logger
from src.crawler.bilibili_login import bilibili_login
from src.crawler.audio_rank_crawler import audio_rank_crawler
from src.preprocessing.data_cleaner import data_cleaner
from src.analysis.data_analyzer import data_analyzer


def main():
    """主程序入口。"""
    try:
        logger.info("开始运行B站音频榜单爬虫程序")
        
        # 检查登录状态
        # if not bilibili_login.load_cookies():
        #     logger.error("未找到Cookie文件，请先手动登录并保存Cookie")
        #     return
        #
        # if not bilibili_login.check_login_status():
        #     logger.error("Cookie已失效，请更新Cookie")
        #     return
        
        # 爬取数据
        logger.info("开始爬取数据")
        ranks_data = audio_rank_crawler.crawl_all_ranks()
        if not ranks_data:
            logger.error("爬取数据失败")
            return
        logger.info("数据爬取完成")
        
        # 清洗数据
        logger.info("开始清洗数据")
        cleaned_data = data_cleaner.clean_all_data()
        if not cleaned_data:
            logger.error("数据清洗失败")
            return
        logger.info("数据清洗完成")
        
        # 分析数据
        logger.info("开始分析数据")
        analysis_results = data_analyzer.analyze_all_data()
        if not analysis_results:
            logger.error("数据分析失败")
            return
        logger.info("数据分析完成")
        
        logger.info("程序运行完成")
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")


def setup_directories():
    """创建必要的目录。"""
    directories = [
        'data/raw',
        'data/processed',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")


if __name__ == "__main__":
    # 创建必要的目录
    setup_directories()
    
    # 运行主程序
    main()