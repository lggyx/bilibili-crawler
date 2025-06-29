#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
B站登录模块，用于处理B站的登录认证。

该模块提供了登录B站、保存和加载Cookie等功能。
由于B站登录需要扫码或账号密码，这里我们主要实现Cookie管理功能，
实际的登录过程需要手动在浏览器中完成，然后将Cookie保存下来供程序使用。
"""

import os
import json
import time
from pathlib import Path
import requests

from src.config.config import config
from src.utils.logger import logger


class BilibiliLogin:
    """B站登录类，处理登录认证相关功能。"""

    def __init__(self):
        """初始化B站登录类。"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('CRAWLER', 'user_agent')
        })
        self.cookies = None
        self.cookie_path = config.get('CRAWLER', 'cookie_path')

        # 确保cookie文件所在目录存在
        cookie_dir = os.path.dirname(self.cookie_path)
        if not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir)

    def load_cookies(self):
        """
        从文件加载Cookie。

        Returns:
            bool: 是否成功加载Cookie
        """
        try:
            if os.path.exists(self.cookie_path):
                with open(self.cookie_path, 'r', encoding='utf-8') as f:
                    self.cookies = json.load(f)
                    self.session.cookies.update(self.cookies)
                    logger.info("成功加载Cookie")
                    return True
            else:
                logger.warning("Cookie文件不存在")
                return False
        except Exception as e:
            logger.error(f"加载Cookie失败: {str(e)}")
            return False

    def save_cookies(self, cookies):
        """
        保存Cookie到文件。

        Args:
            cookies (dict): Cookie字典

        Returns:
            bool: 是否成功保存Cookie
        """
        try:
            with open(self.cookie_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.info("成功保存Cookie")
            return True
        except Exception as e:
            logger.error(f"保存Cookie失败: {str(e)}")
            return False

    def check_login_status(self):
        """
        检查登录状态。

        Returns:
            bool: 是否已登录
        """
        try:
            # 访问B站首页检查登录状态
            response = self.session.get(
                config.get('CRAWLER', 'login_url'),
                timeout=config.getint('CRAWLER', 'timeout', fallback=10)
            )

            # 通过返回的页面内容判断是否登录
            # 这里的判断条件需要根据实际情况调整
            if response.status_code == 200 and 'logout' in response.text:
                logger.info("登录状态有效")
                return True
            else:
                logger.warning("登录状态已失效")
                return False
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False

    def update_cookies_from_browser(self, cookies_str):
        """
        从浏览器中更新Cookie。

        Args:
            cookies_str (str): 从浏览器复制的Cookie字符串

        Returns:
            bool: 是否成功更新Cookie
        """
        try:
            # 解析Cookie字符串
            cookies_dict = {}
            for item in cookies_str.split(';'):
                item = item.strip()
                if not item:
                    continue
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies_dict[key.strip()] = value.strip()

            # 更新session的cookies
            self.session.cookies.update(cookies_dict)
            self.cookies = cookies_dict

            # 保存Cookie到文件
            if self.save_cookies(cookies_dict):
                logger.info("成功更新Cookie")
                return True
            return False
        except Exception as e:
            logger.error(f"更新Cookie失败: {str(e)}")
            return False

    def get_session(self):
        """
        获取当前的requests session对象。

        Returns:
            requests.Session: 当前的session对象
        """
        return self.session


# 创建全局登录对象
bilibili_login = BilibiliLogin()