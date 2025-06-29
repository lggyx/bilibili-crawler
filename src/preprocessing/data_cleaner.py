#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据清洗模块，用于处理和清洗从B站爬取的原始数据。

该模块提供了数据清洗、格式化和标准化等功能。
"""

import os
import json
import pandas as pd
from datetime import datetime

from src.config.config import config
from src.utils.logger import logger


class DataCleaner:
    """数据清洗类，用于处理和清洗数据。"""

    def __init__(self):
        """初始化数据清洗类。"""
        # 获取数据路径
        self.raw_data_path = config.get('DATA', 'raw_data_path')
        self.processed_data_path = config.get('DATA', 'processed_data_path')
        
        # 确保处理后的数据目录存在
        if not os.path.exists(self.processed_data_path):
            os.makedirs(self.processed_data_path)
    
    def clean_rank_periods(self, filename='all_periods.json'):
        """
        清洗榜单周期数据。

        Args:
            filename (str, optional): 原始数据文件名。默认为'all_periods.json'。

        Returns:
            pd.DataFrame: 清洗后的榜单周期数据
        """
        try:
            # 读取原始数据
            filepath = os.path.join(self.raw_data_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取榜单列表
            periods = data['data']['list']
            
            # 转换为DataFrame
            df = pd.DataFrame(periods)
            
            # 重命名列
            df = df.rename(columns={
                'list_id': 'rank_id',
                'title': 'rank_title',
                'publish_time': 'publish_timestamp',
                'end_time': 'end_timestamp'
            })
            
            # 转换时间戳为日期时间
            df['publish_time'] = pd.to_datetime(df['publish_timestamp'], unit='s')
            df['end_time'] = pd.to_datetime(df['end_timestamp'], unit='s')
            
            # 保存处理后的数据
            output_path = os.path.join(self.processed_data_path, 'rank_periods.csv')
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"成功清洗榜单周期数据，保存至: {output_path}")
            
            return df
        except Exception as e:
            logger.error(f"清洗榜单周期数据失败: {str(e)}")
            return pd.DataFrame()
    
    def clean_rank_detail(self, rank_id):
        """
        清洗榜单详情数据。

        Args:
            rank_id (int): 榜单ID

        Returns:
            pd.DataFrame: 清洗后的榜单详情数据
        """
        try:
            # 读取原始数据
            filename = f'rank_detail_{rank_id}.json'
            filepath = os.path.join(self.raw_data_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取榜单详情
            detail = data['data']
            
            # 转换为DataFrame
            df = pd.DataFrame([detail])
            
            # 重命名列
            df = df.rename(columns={
                'list_id': 'rank_id',
                'title': 'rank_title',
                'publish_time': 'publish_timestamp',
                'end_time': 'end_timestamp'
            })
            
            # 转换时间戳为日期时间
            df['publish_time'] = pd.to_datetime(df['publish_timestamp'], unit='s')
            df['end_time'] = pd.to_datetime(df['end_timestamp'], unit='s')
            
            # 保存处理后的数据
            output_path = os.path.join(self.processed_data_path, f'rank_detail_{rank_id}.csv')
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"成功清洗榜单详情数据，保存至: {output_path}")
            
            return df
        except Exception as e:
            logger.error(f"清洗榜单详情数据失败: {str(e)}")
            return pd.DataFrame()
    
    def clean_music_list(self, rank_id):
        """
        清洗榜单音乐列表数据。

        Args:
            rank_id (int): 榜单ID

        Returns:
            pd.DataFrame: 清洗后的音乐列表数据
        """
        try:
            # 读取原始数据
            filename = f'all_music_list_{rank_id}.json'
            filepath = os.path.join(self.raw_data_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取音乐列表
            music_list = data['data']['list']
            
            # 转换为DataFrame
            df = pd.DataFrame(music_list)
            
            # 添加榜单ID
            df['rank_id'] = rank_id
            
            # 重命名列
            df = df.rename(columns={
                'id': 'music_id',
                'title': 'music_title',
                'author': 'artist',
                'create_time': 'create_timestamp',
                'play_count': 'play_count',
                'collect_count': 'favorite_count'
            })
            
            # 转换时间戳为日期时间
            df['create_time'] = pd.to_datetime(df['create_timestamp'], unit='s')
            
            # 处理数值型数据
            numeric_columns = ['play_count', 'favorite_count']
            df[numeric_columns] = df[numeric_columns].fillna(0).astype(int)
            
            # 保存处理后的数据
            output_path = os.path.join(self.processed_data_path, f'music_list_{rank_id}.csv')
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"成功清洗音乐列表数据，保存至: {output_path}")
            
            return df
        except Exception as e:
            logger.error(f"清洗音乐列表数据失败: {str(e)}")
            return pd.DataFrame()
    
    def clean_all_data(self):
        """
        清洗所有数据。

        Returns:
            dict: 清洗后的所有数据，包含榜单周期、详情和音乐列表
        """
        try:
            # 清洗榜单周期数据
            periods_df = self.clean_rank_periods()
            if periods_df.empty:
                return {}
            
            # 获取所有榜单ID
            rank_ids = periods_df['rank_id'].unique()
            
            all_data = {
                'periods': periods_df,
                'details': {},
                'music_lists': {}
            }
            
            # 清洗每个榜单的详情和音乐列表数据
            for rank_id in rank_ids:
                # 清洗榜单详情
                detail_df = self.clean_rank_detail(rank_id)
                if not detail_df.empty:
                    all_data['details'][rank_id] = detail_df
                
                # 清洗音乐列表
                music_df = self.clean_music_list(rank_id)
                if not music_df.empty:
                    all_data['music_lists'][rank_id] = music_df
            
            logger.info("成功清洗所有数据")
            return all_data
        except Exception as e:
            logger.error(f"清洗所有数据失败: {str(e)}")
            return {}


# 创建全局数据清洗对象
data_cleaner = DataCleaner()