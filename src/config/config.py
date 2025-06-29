#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块，用于读取和管理配置信息。

该模块使用configparser库读取配置文件，并提供获取配置的方法。
"""

import os
import configparser
from pathlib import Path


class Config:
    """配置类，用于读取和管理配置信息。"""

    def __init__(self, config_file=None):
        """
        初始化配置类。

        Args:
            config_file (str, optional): 配置文件路径。默认为None，使用默认路径。
        """
        self.config = configparser.ConfigParser()
        
        # 如果未指定配置文件，则使用默认路径
        if config_file is None:
            # 获取当前文件所在目录
            current_dir = Path(__file__).parent
            config_file = current_dir / 'config.ini'
        
        # 读取配置文件
        if os.path.exists(config_file):
            self.config.read(config_file, encoding='utf-8')
        else:
            raise FileNotFoundError(f"配置文件 {config_file} 不存在")
    
    def get(self, section, option, fallback=None):
        """
        获取配置项的值。

        Args:
            section (str): 配置节名称
            option (str): 配置项名称
            fallback (str, optional): 默认值。当配置项不存在时返回该值。

        Returns:
            str: 配置项的值
        """
        return self.config.get(section, option, fallback=fallback)
    
    def getint(self, section, option, fallback=None):
        """
        获取整型配置项的值。

        Args:
            section (str): 配置节名称
            option (str): 配置项名称
            fallback (int, optional): 默认值。当配置项不存在时返回该值。

        Returns:
            int: 配置项的整型值
        """
        return self.config.getint(section, option, fallback=fallback)
    
    def getfloat(self, section, option, fallback=None):
        """
        获取浮点型配置项的值。

        Args:
            section (str): 配置节名称
            option (str): 配置项名称
            fallback (float, optional): 默认值。当配置项不存在时返回该值。

        Returns:
            float: 配置项的浮点型值
        """
        return self.config.getfloat(section, option, fallback=fallback)
    
    def getboolean(self, section, option, fallback=None):
        """
        获取布尔型配置项的值。

        Args:
            section (str): 配置节名称
            option (str): 配置项名称
            fallback (bool, optional): 默认值。当配置项不存在时返回该值。

        Returns:
            bool: 配置项的布尔型值
        """
        return self.config.getboolean(section, option, fallback=fallback)


# 创建全局配置对象
config = Config()