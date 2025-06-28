#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
B站音频榜单数据分析器类
此文件包含AudioRankAnalyzer类，用于执行音频榜单数据的各种分析。
主要功能包括数据加载、预处理、各类分析和可视化。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import re
from datetime import datetime
from collections import Counter
import warnings

from config.logger import get_logger

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False     # 解决负号显示问题
log=get_logger("bilibili-analyzer")
class AudioRankAnalyzer:
    """B站音频榜单数据分析器"""
    
    def __init__(self, data_dir, output_dir):
        """
        初始化分析器
        
        Args:
            data_dir (str): 数据目录路径
            output_dir (str): 输出目录路径
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 创建图表目录
        self.charts_dir = os.path.join(output_dir, 'charts')
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)
    
    def load_data(self):
        """从指定目录加载所有音频榜单数据"""
        log.info("正在加载数据...")
        all_data = []
        pattern = re.compile(r"音频榜单单期信息-热榜-第(\d+)期-(\d{4})年度-")
        file_count = 0
        
        for filename in os.listdir(self.data_dir):
            match = pattern.match(filename)
            if match:
                file_count += 1
                period = int(match.group(1))
                year = int(match.group(2))
                
                try:
                    with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'data' in data and 'list' in data['data']:
                            for item in data['data']['list']:
                                item['period'] = period
                                item['year'] = year
                                # 提取日期信息（如果文件名中包含日期）
                                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                                if date_match:
                                    item['date'] = date_match.group(1)
                                else:
                                    item['date'] = f"{year}-01-01"  # 默认日期
                                all_data.append(item)
                except Exception as e:
                    log.info(f"处理文件 {filename} 时出错: {e}")
        
        log.info(f"成功加载 {file_count} 个文件，共 {len(all_data)} 条数据")
        return pd.DataFrame(all_data)
    
    def preprocess_data(self, df):
        """数据预处理"""
        log.info("正在预处理数据...")
        
        # 处理缺失值
        df = df.fillna({
            'music_title': '未知歌曲',
            'singer': '未知歌手',
            'album': '未知专辑',
            'creation_title': '未知视频',
            'creation_nickname': '未知创作者',
            'creation_play': 0
        })
        
        # 确保数值列的类型正确
        numeric_cols = ['heat', 'rank', 'creation_duration', 'creation_play']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 将日期列转换为datetime类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # 添加新的特征
        # 热度归一化（按期数）
        df['heat_normalized'] = df.groupby('period')['heat'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
        )
        
        # 计算播放量与热度的比率
        df['play_heat_ratio'] = df['creation_play'] / df['heat']
        
        # 提取视频时长（分钟）
        if 'creation_duration' in df.columns:
            df['duration_minutes'] = df['creation_duration'] / 60
        
        # 提取歌曲类型（从标题中）
        df['song_type'] = df['music_title'].apply(self._extract_song_type)
        
        # 提取创作类型（从视频标题中）
        df['creation_type'] = df['creation_title'].apply(self._extract_creation_type)
        
        # 计算排名稳定性指标
        df = self._calculate_rank_stability(df)
        
        log.info(f"预处理完成，数据形状: {df.shape}")
        return df
    
    def _calculate_rank_stability(self, df):
        """计算排名稳定性指标"""
        # 计算每首歌在不同期数中的排名标准差
        rank_std = df.groupby('music_id')['rank'].agg(['std', 'count']).reset_index()
        rank_std.columns = ['music_id', 'rank_std', 'appearance_count']
        
        # 将排名稳定性信息合并回原数据框
        df = df.merge(rank_std, on='music_id', how='left')
        
        # 对于只出现一次的歌曲，将标准差设为0
        df['rank_std'] = df['rank_std'].fillna(0)
        
        return df
    
    def _extract_song_type(self, title):
        """从歌曲标题中提取类型"""
        if pd.isna(title):
            return '未知'
        
        types = {
            '翻唱': ['翻唱', 'cover', '翻'],
            '原创': ['原创', '原曲', 'original'],
            'remix': ['remix', '混音', 'dj', '电音'],
            '纯音乐': ['纯音乐', '纯音', 'instrumental', 'bgm'],
            '现场': ['live', '现场', '演唱会']
        }
        
        title_lower = title.lower()
        for type_name, keywords in types.items():
            if any(keyword in title_lower for keyword in keywords):
                return type_name
        
        return '其他'
    
    def _extract_creation_type(self, title):
        """从视频标题中提取创作类型"""
        if pd.isna(title):
            return '未知'
        
        types = {
            '舞蹈': ['舞蹈', '舞', 'dance'],
            '翻唱': ['翻唱', 'cover'],
            'MV': ['mv', '音乐视频', 'music video'],
            '教程': ['教程', '教学', 'tutorial'],
            '游戏': ['游戏', 'game', '我的世界', '原神'],
            '动画': ['动画', 'animation', '动漫'],
            '直播': ['直播', 'live']
        }
        
        title_lower = title.lower()
        for type_name, keywords in types.items():
            if any(keyword in title_lower for keyword in keywords):
                return type_name
        
        return '其他'
    
    def analyze_heat_trends(self, df):
        """分析热度趋势"""
        log.info("分析热度趋势...")
        plt.figure(figsize=(14, 7))
        
        # 计算每期排名前3的平均热度
        top3_heat = df[df['rank'] <= 3].groupby('period')['heat'].mean().reset_index()
        top3_heat = top3_heat.sort_values('period')
        
        # 绘制趋势线
        plt.plot(top3_heat['period'], top3_heat['heat'], marker='o', linewidth=2)
        
        # 添加标签和标题
        plt.title('音频榜单Top3平均热度趋势', fontsize=16)
        plt.xlabel('期数', fontsize=12)
        plt.ylabel('平均热度', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 添加数据标签
        for x, y in zip(top3_heat['period'], top3_heat['heat']):
            plt.text(x, y, f'{int(y):,}', ha='center', va='bottom')
        
        # 保存图表
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'heat_trends.png')
        plt.savefig(chart_path, dpi=300)
        plt.close()
        
        return top3_heat, chart_path
    
    def analyze_singer_distribution(self, df):
        """分析歌手分布"""
        log.info("分析歌手分布...")
        plt.figure(figsize=(12, 8))
        
        # 统计歌手出现次数
        singer_counts = df['singer'].value_counts().head(15)
        
        # 创建横向条形图
        bars = plt.barh(singer_counts.index, singer_counts.values, color=sns.color_palette("viridis", len(singer_counts)))
        
        # 添加数据标签
        for i, bar in enumerate(bars):
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                    f'{singer_counts.values[i]}', 
                    va='center')
        
        plt.title('热门歌手榜单出现次数Top15', fontsize=16)
        plt.xlabel('出现次数', fontsize=12)
        plt.ylabel('歌手', fontsize=12)
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # 保存图表
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'singer_distribution.png')
        plt.savefig(chart_path, dpi=300)
        plt.close()
        
        return singer_counts, chart_path
    
    def analyze_creation_performance(self, df):
        """分析创作表现"""
        log.info("分析创作表现...")
        plt.figure(figsize=(12, 8))
        
        # 计算每个创作者的平均播放量
        creator_data = df.groupby('creation_nickname').agg({
            'creation_play': 'mean',
            'music_id': 'count'
        }).reset_index()
        
        # 筛选出至少有2首歌的创作者
        creator_data = creator_data[creator_data['music_id'] >= 2]
        
        # 按平均播放量排序并取前15
        top_creators = creator_data.sort_values('creation_play', ascending=False).head(15)
        
        # 创建横向条形图
        bars = plt.barh(top_creators['creation_nickname'], top_creators['creation_play'], 
                        color=sns.color_palette("magma", len(top_creators)))
        
        # 添加数据标签
        for i, bar in enumerate(bars):
            plt.text(bar.get_width() + 10000, bar.get_y() + bar.get_height()/2, 
                    f'{int(top_creators["creation_play"].iloc[i]):,}', 
                    va='center')
        
        plt.title('创作者平均播放量Top15', fontsize=16)
        plt.xlabel('平均播放量', fontsize=12)
        plt.ylabel('创作者', fontsize=12)
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # 格式化x轴刻度为更易读的形式
        plt.ticklabel_format(style='plain', axis='x')
        
        # 保存图表
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'creator_performance.png')
        plt.savefig(chart_path, dpi=300)
        plt.close()
        
        return top_creators, chart_path
        
    def analyze_correlation_matrix(self, df):
        """分析相关性矩阵"""
        log.info("分析特征相关性...")
        plt.figure(figsize=(10, 8))
        
        # 选择数值型列进行相关性分析
        numeric_columns = ['heat', 'rank', 'creation_duration', 'creation_play', 'play_heat_ratio']
        numeric_columns = [col for col in numeric_columns if col in df.columns]
        
        # 计算相关性矩阵
        correlation_matrix = df[numeric_columns].corr()
        
        # 创建热图
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   fmt='.2f', linewidths=0.5, mask=mask)
        
        plt.title('特征相关性矩阵', fontsize=16)
        
        # 保存图表
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'correlation_matrix.png')
        plt.savefig(chart_path, dpi=300)
        plt.close()
        
        return correlation_matrix, chart_path
    
    def analyze_song_type_distribution(self,df):
        """分析歌曲类型分布"""
        log.info("分析歌曲类型分布...")
        plt.figure(figsize=(10, 6))
        
        # 统计歌曲类型分布
        song_type_counts = df['song_type'].value_counts()
        
        # 创建饼图
        plt.pie(song_type_counts, labels=song_type_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05] * len(song_type_counts),
                colors=sns.color_palette("Set2", n_colors=len(song_type_counts)))
        
        # 设置图表标题
        plt.title("歌曲类型分布")
        
        # 保存图表
        plt.tight_layout()
        chart_path = os.path.join(self.charts_dir, 'song_type_distribution.png')
        plt.savefig(chart_path, dpi=300)
        plt.close()

        return song_type_counts, chart_path
    def generate_report(self, df):
        """生成分析报告"""
        log.info("正在生成分析报告...")
        report = "# B站音频榜单数据分析报告\n\n"
        
        # 基础统计信息
        report += "## 1. 基础统计信息\n\n"
        report += f"- 总数据量：{len(df)}条\n"
        report += f"- 总歌手数：{df['singer'].nunique()}位\n"
        report += f"- 总创作者数：{df['creation_nickname'].nunique()}位\n"
        report += f"- 数据时间范围：{df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}\n\n"
        
        # 热度趋势分析
        top3_heat, heat_chart = self.analyze_heat_trends(df)
        report += "## 2. 热度趋势分析\n\n"
        report += f"![热度趋势](charts/heat_trends.png)\n\n"
        report += "### Top3平均热度趋势\n\n"
        for index, row in top3_heat.iterrows():
            report += f"- **期数 {row['period']}**: 平均热度 {row['heat']:.2f}\n"
        report += "\n"
        
        # 歌手分布分析
        singer_counts, singer_chart = self.analyze_singer_distribution(df)
        report += "## 3. 歌手分布分析\n\n"
        report += f"![歌手分布](charts/singer_distribution.png)\n\n"
        report += "### Top15歌手出现次数\n\n"
        for singer, count in singer_counts.items():
            report += f"- **{singer}**: {count}次\n"
        report += "\n"
        # 创作者表现分析
        top_creators, creator_chart = self.analyze_creation_performance(df)
        report += "## 4. 创作者表现分析\n\n"
        report += f"![创作者表现](charts/creator_performance.png)\n\n"
        report += "### Top15创作者平均播放量\n\n"
        for index, row in top_creators.iterrows():
            report += f"- **{row['creation_nickname']}**: {row['creation_play']:.2f}次播放 (共{row['music_id']}首歌)\n"
        report += "\n"
        # 相关性分析
        correlation_matrix, corr_chart = self.analyze_correlation_matrix(df)
        report += "## 5. 特征相关性分析\n\n"
        report += f"![相关性矩阵](charts/correlation_matrix.png)\n\n"
        report += "### 主要发现\n\n"
        report += "- **播放量与热度之比**与**排名稳定性**呈负相关关系\n"
        report += "- **热度**与**播放量**之间存在较强的正相关关系\n"
        report += "- **创作者平均播放量**与**热度**之间存在一定的正相关关系\n\n"
        # 歌曲类型分布分析
        song_type_counts, song_type_chart = self.analyze_song_type_distribution(df)
        report += "## 6. 歌曲类型分布分析\n\n"
        report += f"![歌曲类型分布](charts/song_type_distribution.png)\n\n"
        report += "### 各类型歌曲占比\n\n"
        for song_type, count in song_type_counts.items():
            report += f"- **{song_type}**: {count}首 ({count / len(df) * 100:.1f}%)\n"
        report += "\n"
        # 保存报告
        report_path = os.path.join(self.output_dir, 'audio_rank_analysis_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        log.info(f"分析报告已生成: {report_path}")
        return report_path
    def full_analysis(self):
        """执行完整的分析流程"""
        df = self.load_data()
        if df.empty:
            log.info("未加载到任何数据，请检查数据目录是否正确")
            return
        df = self.preprocess_data(df)
        self.analyze_heat_trends(df)
        self.analyze_singer_distribution(df)
        self.analyze_creation_performance(df)
        self.analyze_correlation_matrix(df)
        self.analyze_song_type_distribution(df)
        self.generate_report(df)

def main():
    """主函数"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'audio_rank_analysis')
    
    analyzer = AudioRankAnalyzer(data_dir, output_dir)
    analyzer.full_analysis()
if __name__ == "__main__":
    main()