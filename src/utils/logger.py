#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志记录模块，用于记录程序运行日志。

该模块使用Python标准库中的logging模块，根据配置文件设置日志级别、格式等。
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.config import config


class Logger:
    """日志记录类，用于记录程序运行日志。"""

    def __init__(self, name=None, level=None):
        """
        初始化日志记录类。

        Args:
            name (str, optional): 日志记录器名称。默认为None，使用模块名称。
            level (str, optional): 日志级别。默认为None，使用配置文件中的设置。
        """
        # 如果未指定名称，则使用调用模块的名称
        self.name = name if name else __name__
        
        # 创建日志记录器
        self.logger = logging.getLogger(self.name)
        
        # 如果未指定日志级别，则使用配置文件中的设置
        if level is None:
            level = config.get('LOGGING', 'level', fallback='INFO')
        
        # 设置日志级别
        level_dict = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(level_dict.get(level.upper(), logging.INFO))
        
        # 如果已经添加了处理器，则不再添加
        if self.logger.handlers:
            return
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.logger.level)
        
        # 创建文件处理器
        log_file = config.get('LOGGING', 'file_path', fallback='logs/bilibili_crawler.log')
        log_dir = os.path.dirname(log_file)
        
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建按大小轮转的文件处理器，最大10MB，最多备份5个文件
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(self.logger.level)
        
        # 设置日志格式
        log_format = config.get(
            'LOGGING', 'format', 
            fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """记录调试级别的日志。"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录信息级别的日志。"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告级别的日志。"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误级别的日志。"""
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误级别的日志。"""
        self.logger.critical(message)


# 创建全局日志记录器
logger = Logger('bilibili_crawler')