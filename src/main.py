"""
数据分析系统入口
提供命令行接口，用于执行数据采集、处理、分析和可视化任务
"""

import os
import sys
import argparse
from typing import Dict, List, Optional
import logging
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.logger import get_logger
from utils.helpers import load_yaml, ensure_dir
from crawler.crawler import BaseCrawler
from preprocessor.preprocessor import DataPreprocessor
from analyzer.analyzer import StatisticalAnalyzer, TextAnalyzer, TimeSeriesAnalyzer
from visualizer.visualizer import StatisticalVisualizer, TextVisualizer, TimeSeriesVisualizer
from storage.storage import FileStorage, SQLiteStorage

logger = get_logger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="数据分析系统")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 数据采集命令
    crawl_parser = subparsers.add_parser("crawl", help="数据采集")
    crawl_parser.add_argument("--config", type=str, default="config/crawler_config.yaml", help="爬虫配置文件路径")
    crawl_parser.add_argument("--output", type=str, default="data/raw", help="数据保存目录")
    
    # 数据预处理命令
    preprocess_parser = subparsers.add_parser("preprocess", help="数据预处理")
    preprocess_parser.add_argument("--config", type=str, default="config/preprocess_config.yaml", help="预处理配置文件路径")
    preprocess_parser.add_argument("--input", type=str, required=True, help="输入数据路径")
    preprocess_parser.add_argument("--output", type=str, default="data/processed", help="输出数据路径")
    
    # 数据分析命令
    analyze_parser = subparsers.add_parser("analyze", help="数据分析")
    analyze_parser.add_argument("--config", type=str, default="config/analysis_config.yaml", help="分析配置文件路径")
    analyze_parser.add_argument("--input", type=str, required=True, help="输入数据路径")
    analyze_parser.add_argument("--type", type=str, choices=["statistical", "text", "time_series"], required=True, help="分析类型")
    analyze_parser.add_argument("--output", type=str, default="data/analysis", help="分析结果保存路径")
    
    # 数据可视化命令
    visualize_parser = subparsers.add_parser("visualize", help="数据可视化")
    visualize_parser.add_argument("--config", type=str, default="config/visualization_config.yaml", help="可视化配置文件路径")
    visualize_parser.add_argument("--input", type=str, required=True, help="输入数据路径")
    visualize_parser.add_argument("--type", type=str, choices=["statistical", "text", "time_series"], required=True, help="可视化类型")
    visualize_parser.add_argument("--output", type=str, default="data/visualizations", help="可视化结果保存路径")
    
    return parser.parse_args()


def crawl_data(config_path: str, output_dir: str):
    """
    执行数据采集
    
    Args:
        config_path: 配置文件路径
        output_dir: 输出目录
    """
    try:
        # 加载配置
        config = load_yaml(config_path)
        if not config:
            logger.error("加载爬虫配置失败")
            return
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        
        # 创建爬虫实例
        crawler = BaseCrawler(config)
        
        # 执行数据采集
        data = crawler.crawl()
        
        # 保存数据
        storage = FileStorage(output_dir)
        filename = f"crawled_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        storage.save(data, filename)
        
        logger.info(f"数据采集完成，已保存到: {os.path.join(output_dir, filename)}")
    
    except Exception as e:
        logger.error(f"数据采集失败: {str(e)}")


def preprocess_data(config_path: str, input_path: str, output_dir: str):
    """
    执行数据预处理
    
    Args:
        config_path: 配置文件路径
        input_path: 输入数据路径
        output_dir: 输出目录
    """
    try:
        # 加载配置
        config = load_yaml(config_path)
        if not config:
            logger.error("加载预处理配置失败")
            return
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        
        # 加载数据
        storage = FileStorage(os.path.dirname(input_path))
        data = storage.load(os.path.basename(input_path))
        
        # 创建预处理器实例
        preprocessor = DataPreprocessor(config)
        
        # 执行预处理
        processed_data = preprocessor.preprocess(data)
        
        # 保存处理后的数据
        output_storage = FileStorage(output_dir)
        filename = f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_storage.save(processed_data, filename)
        
        logger.info(f"数据预处理完成，已保存到: {os.path.join(output_dir, filename)}")
    
    except Exception as e:
        logger.error(f"数据预处理失败: {str(e)}")


def analyze_data(config_path: str, input_path: str, analysis_type: str, output_dir: str):
    """
    执行数据分析
    
    Args:
        config_path: 配置文件路径
        input_path: 输入数据路径
        analysis_type: 分析类型
        output_dir: 输出目录
    """
    try:
        # 加载配置
        config = load_yaml(config_path)
        if not config:
            logger.error("加载分析配置失败")
            return
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        
        # 加载数据
        storage = FileStorage(os.path.dirname(input_path))
        data = storage.load(os.path.basename(input_path))
        
        # 创建分析器实例
        if analysis_type == "statistical":
            analyzer = StatisticalAnalyzer(config_path)
        elif analysis_type == "text":
            analyzer = TextAnalyzer(config_path)
        elif analysis_type == "time_series":
            analyzer = TimeSeriesAnalyzer(config_path)
        else:
            logger.error(f"不支持的分析类型: {analysis_type}")
            return
        
        # 执行分析
        results = analyzer.analyze(data)
        
        # 保存分析结果
        output_storage = FileStorage(output_dir)
        filename = f"{analysis_type}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_storage.save(results, filename)
        
        logger.info(f"数据分析完成，已保存到: {os.path.join(output_dir, filename)}")
    
    except Exception as e:
        logger.error(f"数据分析失败: {str(e)}")


def visualize_data(config_path: str, input_path: str, viz_type: str, output_dir: str):
    """
    执行数据可视化
    
    Args:
        config_path: 配置文件路径
        input_path: 输入数据路径
        viz_type: 可视化类型
        output_dir: 输出目录
    """
    try:
        # 加载配置
        config = load_yaml(config_path)
        if not config:
            logger.error("加载可视化配置失败")
            return
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        
        # 加载数据
        storage = FileStorage(os.path.dirname(input_path))
        data = storage.load(os.path.basename(input_path))
        
        # 创建可视化器实例
        if viz_type == "statistical":
            visualizer = StatisticalVisualizer(config_path)
        elif viz_type == "text":
            visualizer = TextVisualizer(config_path)
        elif viz_type == "time_series":
            visualizer = TimeSeriesVisualizer(config_path)
        else:
            logger.error(f"不支持的可视化类型: {viz_type}")
            return
        
        # 执行可视化
        results = visualizer.visualize(data)
        
        logger.info(f"数据可视化完成，结果已保存到: {output_dir}")
        
        # 打印每个可视化结果的路径
        for viz_name, paths in results.items():
            logger.info(f"{viz_name}:")
            for fmt, path in paths.items():
                logger.info(f"  - {fmt}: {path}")
    
    except Exception as e:
        logger.error(f"数据可视化失败: {str(e)}")


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 根据命令执行相应的操作
    if args.command == "crawl":
        crawl_data(args.config, args.output)
    elif args.command == "preprocess":
        preprocess_data(args.config, args.input, args.output)
    elif args.command == "analyze":
        analyze_data(args.config, args.input, args.type, args.output)
    elif args.command == "visualize":
        visualize_data(args.config, args.input, args.type, args.output)
    else:
        logger.error("请指定要执行的命令")


if __name__ == "__main__":
    main()