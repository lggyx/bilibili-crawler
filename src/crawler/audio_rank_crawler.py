#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
B站音频榜单爬虫模块，用于爬取B站音频榜单数据。

该模块提供了爬取B站音频榜单的功能，包括获取榜单列表、榜单详情和榜单音乐列表等。
"""

import os
import json
import time
from datetime import datetime
import requests

from src.config.config import config
from src.utils.logger import logger
from src.crawler.bilibili_login import bilibili_login


class AudioRankCrawler:
    """B站音频榜单爬虫类，用于爬取B站音频榜单数据。"""

    def __init__(self):
        """初始化B站音频榜单爬虫类。"""
        # 使用登录模块的session
        self.session = bilibili_login.get_session()
        
        # 获取API URL
        self.all_period_url = config.get('CRAWLER', 'audio_rank_all_period_url')
        self.detail_url = config.get('CRAWLER', 'audio_rank_detail_url')
        self.music_list_url = config.get('CRAWLER', 'audio_rank_music_list_url')
        
        # 请求间隔时间(秒)
        self.interval = config.getint('CRAWLER', 'interval', fallback=3)
        
        # 原始数据保存路径
        self.raw_data_path = config.get('DATA', 'raw_data_path')
        
        # 确保原始数据目录存在
        if not os.path.exists(self.raw_data_path):
            os.makedirs(self.raw_data_path)
    
    def get_all_periods(self):
        """
        获取所有榜单周期。

        Returns:
            list: 榜单周期列表，每个元素是一个字典，包含榜单ID、名称等信息
        """
        try:
            logger.info("开始获取所有榜单周期")
            response = self.session.get(self.all_period_url)
            data = response.json()
            
            if data['code'] == 0:
                periods = data['data']['list']
                logger.info(f"成功获取所有榜单周期，共{len(periods)}个")
                
                # 保存原始数据
                self._save_raw_data('all_periods.json', data)
                
                return periods
            else:
                logger.error(f"获取榜单周期失败: {data['message']}")
                return []
        except Exception as e:
            logger.error(f"获取榜单周期异常: {str(e)}")
            return []
    
    def get_rank_detail(self, list_id):
        """
        获取榜单详情。

        Args:
            list_id (int): 榜单ID

        Returns:
            dict: 榜单详情信息
        """
        try:
            logger.info(f"开始获取榜单详情，榜单ID: {list_id}")
            response = self.session.get(self.detail_url, params={'list_id': list_id})
            data = response.json()
            
            if data['code'] == 0:
                detail = data['data']
                logger.info(f"成功获取榜单详情: {detail['title']}")
                
                # 保存原始数据
                self._save_raw_data(f'rank_detail_{list_id}.json', data)
                
                return detail
            else:
                logger.error(f"获取榜单详情失败: {data['message']}")
                return None
        except Exception as e:
            logger.error(f"获取榜单详情异常: {str(e)}")
            return None
    
    def get_music_list(self, list_id, pn=1, ps=100):
        """
        获取榜单音乐列表。

        Args:
            list_id (int): 榜单ID
            pn (int, optional): 页码。默认为1。
            ps (int, optional): 每页数量。默认为100。

        Returns:
            list: 音乐列表，每个元素是一个字典，包含音乐ID、标题、作者等信息
        """
        try:
            logger.info(f"开始获取榜单音乐列表，榜单ID: {list_id}，页码: {pn}，每页数量: {ps}")
            params = {
                'list_id': list_id,
                'pn': pn,
                'ps': ps
            }
            response = self.session.get(self.music_list_url, params=params)
            data = response.json()
            
            if data['code'] == 0:
                music_list = data['data']['list']
                total = data['data']['total']
                logger.info(f"成功获取榜单音乐列表，共{total}首，当前获取{len(music_list)}首")
                
                # 保存原始数据
                self._save_raw_data(f'music_list_{list_id}_p{pn}.json', data)
                
                return music_list, total
            else:
                logger.error(f"获取榜单音乐列表失败: {data['message']}")
                return [], 0
        except Exception as e:
            logger.error(f"获取榜单音乐列表异常: {str(e)}")
            return [], 0
    
    def crawl_all_music_list(self, list_id, ps=100):
        """
        爬取榜单所有音乐列表。

        Args:
            list_id (int): 榜单ID
            ps (int, optional): 每页数量。默认为100。

        Returns:
            list: 所有音乐列表
        """
        all_music_list = []
        pn = 1
        total = float('inf')
        
        while len(all_music_list) < total:
            music_list, total = self.get_music_list(list_id, pn, ps)
            if not music_list:
                break
            
            all_music_list.extend(music_list)
            logger.info(f"已获取{len(all_music_list)}/{total}首音乐")
            
            # 如果已经获取完所有数据，则退出循环
            if len(all_music_list) >= total:
                break
            
            # 请求间隔
            time.sleep(self.interval)
            pn += 1
        
        # 保存所有音乐列表
        self._save_raw_data(f'all_music_list_{list_id}.json', {
            'code': 0,
            'message': 'success',
            'data': {
                'list': all_music_list,
                'total': len(all_music_list)
            }
        })
        
        return all_music_list
    
    def crawl_all_ranks(self):
        """
        爬取所有榜单数据。

        Returns:
            dict: 所有榜单数据，键为榜单ID，值为榜单音乐列表
        """
        all_ranks = {}
        
        # 获取所有榜单周期
        periods = self.get_all_periods()
        if not periods:
            return all_ranks
        
        # 遍历所有榜单周期
        for period in periods:
            list_id = period['list_id']
            
            # 获取榜单详情
            detail = self.get_rank_detail(list_id)
            if not detail:
                continue
            
            # 请求间隔
            time.sleep(self.interval)
            
            # 获取榜单音乐列表
            music_list = self.crawl_all_music_list(list_id)
            all_ranks[list_id] = {
                'detail': detail,
                'music_list': music_list
            }
            
            # 请求间隔
            time.sleep(self.interval)
        
        return all_ranks
    
    def _save_raw_data(self, filename, data):
        """
        保存原始数据到文件。

        Args:
            filename (str): 文件名
            data (dict): 数据字典
        """
        try:
            filepath = os.path.join(self.raw_data_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"成功保存原始数据: {filepath}")
        except Exception as e:
            logger.error(f"保存原始数据失败: {str(e)}")


# 创建全局爬虫对象
audio_rank_crawler = AudioRankCrawler()