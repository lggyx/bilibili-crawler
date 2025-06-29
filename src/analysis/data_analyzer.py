#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据分析模块，用于分析清洗后的数据，提取有价值的信息。

该模块提供了数据分析和可视化功能。
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from src.config.config import config
from src.utils.logger import logger


class DataAnalyzer:
    """数据分析类，用于分析数据并生成报告。"""

    def __init__(self):
        """初始化数据分析类。"""
        # 获取数据路径
        self.processed_data_path = config.get('DATA', 'processed_data_path')
        
        # 设置图表样式
        sns.set(style="whitegrid")
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    def load_data(self):
        """
        加载处理后的数据。

        Returns:
            dict: 加载的数据，包含榜单周期、详情和音乐列表
        """
        try:
            data = {}
            
            # 加载榜单周期数据
            periods_path = os.path.join(self.processed_data_path, 'rank_periods.csv')
            if os.path.exists(periods_path):
                data['periods'] = pd.read_csv(periods_path)
                data['periods']['publish_time'] = pd.to_datetime(data['periods']['publish_time'])
                data['periods']['end_time'] = pd.to_datetime(data['periods']['end_time'])
            
            # 加载榜单详情和音乐列表数据
            data['details'] = {}
            data['music_lists'] = {}
            
            # 如果已加载榜单周期数据
            if 'periods' in data and not data['periods'].empty:
                rank_ids = data['periods']['rank_id'].unique()
                
                for rank_id in rank_ids:
                    # 加载榜单详情
                    detail_path = os.path.join(self.processed_data_path, f'rank_detail_{rank_id}.csv')
                    if os.path.exists(detail_path):
                        detail_df = pd.read_csv(detail_path)
                        detail_df['publish_time'] = pd.to_datetime(detail_df['publish_time'])
                        detail_df['end_time'] = pd.to_datetime(detail_df['end_time'])
                        data['details'][rank_id] = detail_df
                    
                    # 加载音乐列表
                    music_path = os.path.join(self.processed_data_path, f'music_list_{rank_id}.csv')
                    if os.path.exists(music_path):
                        music_df = pd.read_csv(music_path)
                        music_df['create_time'] = pd.to_datetime(music_df['create_time'])
                        data['music_lists'][rank_id] = music_df
            
            logger.info("成功加载处理后的数据")
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return {}
    
    def analyze_rank_periods(self, periods_df):
        """
        分析榜单周期数据。

        Args:
            periods_df (pd.DataFrame): 榜单周期数据

        Returns:
            dict: 分析结果
        """
        try:
            if periods_df.empty:
                return {}
            
            results = {}
            
            # 统计榜单数量
            results['total_ranks'] = len(periods_df)
            
            # 按月份统计榜单数量
            periods_df['month'] = periods_df['publish_time'].dt.to_period('M')
            monthly_counts = periods_df.groupby('month').size()
            results['monthly_counts'] = monthly_counts.to_dict()
            
            # 可视化：按月份统计榜单数量
            plt.figure(figsize=(12, 6))
            monthly_counts.plot(kind='bar')
            plt.title('每月榜单数量')
            plt.xlabel('月份')
            plt.ylabel('榜单数量')
            plt.tight_layout()
            plt.savefig(os.path.join(self.processed_data_path, 'monthly_ranks.png'))
            plt.close()
            
            logger.info("成功分析榜单周期数据")
            return results
        except Exception as e:
            logger.error(f"分析榜单周期数据失败: {str(e)}")
            return {}
    
    def analyze_music_list(self, music_df):
        """
        分析音乐列表数据。

        Args:
            music_df (pd.DataFrame): 音乐列表数据

        Returns:
            dict: 分析结果
        """
        try:
            if music_df.empty:
                return {}
            
            results = {}
            
            # 统计音乐数量
            results['total_music'] = len(music_df)
            
            # 统计艺术家数量
            results['total_artists'] = music_df['artist'].nunique()
            
            # 播放量统计
            results['total_plays'] = music_df['play_count'].sum()
            results['avg_plays'] = music_df['play_count'].mean()
            results['max_plays'] = music_df['play_count'].max()
            
            # 收藏量统计
            results['total_favorites'] = music_df['favorite_count'].sum()
            results['avg_favorites'] = music_df['favorite_count'].mean()
            results['max_favorites'] = music_df['favorite_count'].max()
            
            # 最受欢迎的艺术家（按音乐数量）
            top_artists_by_count = music_df['artist'].value_counts().head(10)
            results['top_artists_by_count'] = top_artists_by_count.to_dict()
            
            # 最受欢迎的艺术家（按播放量）
            artist_plays = music_df.groupby('artist')['play_count'].sum().sort_values(ascending=False).head(10)
            results['top_artists_by_plays'] = artist_plays.to_dict()
            
            # 可视化：最受欢迎的艺术家（按音乐数量）
            plt.figure(figsize=(12, 6))
            top_artists_by_count.plot(kind='bar')
            plt.title('最受欢迎的艺术家（按音乐数量）')
            plt.xlabel('艺术家')
            plt.ylabel('音乐数量')
            plt.tight_layout()
            plt.savefig(os.path.join(self.processed_data_path, 'top_artists_by_count.png'))
            plt.close()
            
            # 可视化：最受欢迎的艺术家（按播放量）
            plt.figure(figsize=(12, 6))
            artist_plays.plot(kind='bar')
            plt.title('最受欢迎的艺术家（按播放量）')
            plt.xlabel('艺术家')
            plt.ylabel('总播放量')
            plt.tight_layout()
            plt.savefig(os.path.join(self.processed_data_path, 'top_artists_by_plays.png'))
            plt.close()
            
            # 按发布时间分析
            music_df['year_month'] = music_df['create_time'].dt.to_period('M')
            monthly_music = music_df.groupby('year_month').size()
            results['monthly_music'] = monthly_music.to_dict()
            
            # 可视化：按月份统计音乐数量
            plt.figure(figsize=(12, 6))
            monthly_music.plot(kind='line')
            plt.title('每月音乐发布数量')
            plt.xlabel('月份')
            plt.ylabel('音乐数量')
            plt.tight_layout()
            plt.savefig(os.path.join(self.processed_data_path, 'monthly_music.png'))
            plt.close()
            
            logger.info("成功分析音乐列表数据")
            return results
        except Exception as e:
            logger.error(f"分析音乐列表数据失败: {str(e)}")
            return {}
    
    def analyze_all_data(self):
        """
        分析所有数据。

        Returns:
            dict: 分析结果
        """
        try:
            # 加载数据
            data = self.load_data()
            if not data:
                return {}
            
            results = {
                'rank_analysis': {},
                'music_analysis': {}
            }
            
            # 分析榜单周期数据
            if 'periods' in data:
                results['rank_analysis'] = self.analyze_rank_periods(data['periods'])
            
            # 分析所有榜单的音乐列表数据
            all_music_df = pd.DataFrame()
            for rank_id, music_df in data['music_lists'].items():
                # 合并所有音乐列表
                all_music_df = pd.concat([all_music_df, music_df])
                
                # 分析单个榜单的音乐列表
                results['music_analysis'][rank_id] = self.analyze_music_list(music_df)
            
            # 分析所有音乐列表
            if not all_music_df.empty:
                results['overall_music_analysis'] = self.analyze_music_list(all_music_df)
            
            # 生成分析报告
            self._generate_report(results)
            
            logger.info("成功分析所有数据")
            return results
        except Exception as e:
            logger.error(f"分析所有数据失败: {str(e)}")
            return {}
    
    def _generate_report(self, results):
        """
        生成分析报告。

        Args:
            results (dict): 分析结果
        """
        try:
            # 创建报告文件
            report_path = os.path.join(self.processed_data_path, 'analysis_report.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# B站音频榜单数据分析报告\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 榜单分析
                f.write("## 榜单分析\n\n")
                if 'rank_analysis' in results and results['rank_analysis']:
                    f.write(f"- 总榜单数量: {results['rank_analysis'].get('total_ranks', 0)}\n")
                    f.write("\n### 每月榜单数量\n\n")
                    f.write("| 月份 | 榜单数量 |\n")
                    f.write("|------|--------|\n")
                    for month, count in results['rank_analysis'].get('monthly_counts', {}).items():
                        f.write(f"| {month} | {count} |\n")
                else:
                    f.write("无榜单数据\n")
                
                # 整体音乐分析
                f.write("\n## 整体音乐分析\n\n")
                if 'overall_music_analysis' in results and results['overall_music_analysis']:
                    overall = results['overall_music_analysis']
                    f.write(f"- 总音乐数量: {overall.get('total_music', 0)}\n")
                    f.write(f"- 总艺术家数量: {overall.get('total_artists', 0)}\n")
                    f.write(f"- 总播放量: {overall.get('total_plays', 0)}\n")
                    f.write(f"- 平均播放量: {overall.get('avg_plays', 0):.2f}\n")
                    f.write(f"- 最高播放量: {overall.get('max_plays', 0)}\n")
                    f.write(f"- 总收藏量: {overall.get('total_favorites', 0)}\n")
                    f.write(f"- 平均收藏量: {overall.get('avg_favorites', 0):.2f}\n")
                    f.write(f"- 最高收藏量: {overall.get('max_favorites', 0)}\n")
                    
                    f.write("\n### 最受欢迎的艺术家（按音乐数量）\n\n")
                    f.write("| 艺术家 | 音乐数量 |\n")
                    f.write("|--------|--------|\n")
                    for artist, count in overall.get('top_artists_by_count', {}).items():
                        f.write(f"| {artist} | {count} |\n")
                    
                    f.write("\n### 最受欢迎的艺术家（按播放量）\n\n")
                    f.write("| 艺术家 | 总播放量 |\n")
                    f.write("|--------|--------|\n")
                    for artist, plays in overall.get('top_artists_by_plays', {}).items():
                        f.write(f"| {artist} | {plays} |\n")
                else:
                    f.write("无音乐数据\n")
                
                # 各榜单音乐分析
                f.write("\n## 各榜单音乐分析\n\n")
                if 'music_analysis' in results and results['music_analysis']:
                    for rank_id, analysis in results['music_analysis'].items():
                        f.write(f"\n### 榜单 {rank_id}\n\n")
                        f.write(f"- 音乐数量: {analysis.get('total_music', 0)}\n")
                        f.write(f"- 艺术家数量: {analysis.get('total_artists', 0)}\n")
                        f.write(f"- 总播放量: {analysis.get('total_plays', 0)}\n")
                        f.write(f"- 平均播放量: {analysis.get('avg_plays', 0):.2f}\n")
                        f.write(f"- 总收藏量: {analysis.get('total_favorites', 0)}\n")
                        f.write(f"- 平均收藏量: {analysis.get('avg_favorites', 0):.2f}\n")
                else:
                    f.write("无榜单音乐分析数据\n")
                
                f.write("\n## 图表\n\n")
                f.write("1. 每月榜单数量: monthly_ranks.png\n")
                f.write("2. 最受欢迎的艺术家（按音乐数量）: top_artists_by_count.png\n")
                f.write("3. 最受欢迎的艺术家（按播放量）: top_artists_by_plays.png\n")
                f.write("4. 每月音乐发布数量: monthly_music.png\n")
            
            logger.info(f"成功生成分析报告: {report_path}")
        except Exception as e:
            logger.error(f"生成分析报告失败: {str(e)}")


# 创建全局数据分析对象
data_analyzer = DataAnalyzer()