#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
B站音频榜单数据分析运行脚本

此脚本用于运行音频榜单数据分析，生成可视化报告。

使用方法:
    python run_audio_analysis.py --data_dir <数据目录路径> --output_dir <输出目录路径>

示例:
    python run_audio_analysis.py --data_dir ./data/processed --output_dir ./data/reports
"""

import os
import argparse
import sys
from datetime import datetime

from analyzer.audio.audio_rank_analyzer import AudioRankAnalyzer
from config.logger import get_logger

log=get_logger("bilibili-analyzer")
def generate_report(analyzer, df, output_dir):
    """生成分析报告"""
    log.info("生成分析报告...")
    
    # 创建报告目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 执行各项分析
    heat_trends_result, heat_chart = analyzer.analyze_heat_trends(df)
    singer_counts, singer_chart = analyzer.analyze_singer_distribution(df)
    top_creators, creator_chart = analyzer.analyze_creation_performance(df)
    correlation_matrix, corr_chart = analyzer.analyze_correlation_matrix(df)
    song_type_counts, song_type_chart = analyzer.analyze_song_type_distribution(df)
    
    # 生成报告内容
    report = "# B站音频榜单数据分析报告\n\n"
    report += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    # 基础统计信息
    report += "## 1. 基础统计信息\n\n"
    report += f"- 总数据量：{len(df)}条\n"
    report += f"- 统计期数：{df['period'].nunique()}期\n"
    report += f"- 独立歌手数：{df['singer'].nunique()}位\n"
    report += f"- 独立创作者数：{df['creation_nickname'].nunique()}位\n\n"
    
    # 热度分析
    report += "## 2. 热度趋势分析\n\n"
    report += f"![热度趋势](charts/heat_trends.png)\n\n"
    report += f"- 最高热度：{df['heat'].max():,}\n"
    report += f"- 平均热度：{df['heat'].mean():,.0f}\n"
    report += f"- 热度中位数：{df['heat'].median():,.0f}\n\n"
    
    # 歌手分析
    report += "## 3. 歌手分布分析\n\n"
    report += f"![歌手分布](charts/singer_distribution.png)\n\n"
    report += "### Top5歌手及其出现次数\n\n"
    top_singers = singer_counts.head(5)
    for singer, count in top_singers.items():
        report += f"- **{singer}**: {count}次\n"
    report += "\n"
    
    # 创作者分析
    report += "## 4. 创作者表现分析\n\n"
    report += f"![创作者表现](charts/creator_performance.png)\n\n"
    report += "### Top5创作者及其平均播放量\n\n"
    for i in range(min(5, len(top_creators))):
        creator = top_creators.iloc[i]
        report += f"- **{creator['creation_nickname']}**: {int(creator['creation_play']):,}次播放 (共{int(creator['music_id'])}首歌)\n"
    report += "\n"
    
    # 相关性分析
    report += "## 5. 特征相关性分析\n\n"
    report += f"![相关性矩阵](charts/correlation_matrix.png)\n\n"
    report += "### 主要发现\n\n"
    
    # 提取一些相关性发现
    if 'heat' in correlation_matrix.index and 'creation_play' in correlation_matrix.columns:
        heat_play_corr = correlation_matrix.loc['heat', 'creation_play']
        report += f"- 热度与播放量的相关性: {heat_play_corr:.2f}\n"
    
    if 'rank' in correlation_matrix.index and 'heat' in correlation_matrix.columns:
        rank_heat_corr = correlation_matrix.loc['rank', 'heat']
        report += f"- 排名与热度的相关性: {rank_heat_corr:.2f} (负相关表示排名越高，热度越高)\n"
    
    report += "\n"
    
    # 歌曲类型分析
    report += "## 6. 歌曲类型分析\n\n"
    report += f"![歌曲类型分布](charts/song_type_distribution.png)\n\n"
    report += "### 各类型歌曲占比\n\n"
    for song_type, count in song_type_counts.items():
        percentage = count / song_type_counts.sum() * 100
        report += f"- **{song_type}**: {count}首 ({percentage:.1f}%)\n"
    report += "\n"
    
    # 结论与建议
    report += "## 7. 结论与建议\n\n"
    report += "### 主要发现\n\n"
    report += "1. **热度趋势**: 音频榜单热度呈现波动趋势，可能与特定事件或季节性因素相关。\n"
    report += "2. **歌手分布**: 少数歌手在榜单中占据主导地位，表明B站音频市场存在明星效应。\n"
    report += "3. **创作表现**: 高播放量创作者往往有特定的内容风格或粉丝基础。\n"
    report += "4. **歌曲类型**: 不同类型歌曲在榜单中的分布反映了B站用户的音乐偏好。\n\n"
    
    report += "### 建议\n\n"
    report += "1. **内容创作者**: 关注热门歌手和创作类型，结合自身特色进行创作。\n"
    report += "2. **平台运营**: 可以考虑增加对小众音乐类型的推广，丰富平台音乐生态。\n"
    report += "3. **用户**: 可以通过榜单发现热门音乐，也可以关注一些小众但高质量的音频内容。\n\n"
    
    # 保存报告
    report_path = os.path.join(output_dir, 'audio_rank_analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    log.info(f"报告已生成: {report_path}")
    return report_path

def run_audio_analysis():
    # 定义数据及报告路径
    data_dir = os.path.dirname(__file__).split("\\analyzer")[0]+ '\\data\\processed'
    output_dir = os.path.dirname(__file__).split("\\analyzer")[0]+ '\\data\\reports'
    # 创建分析器
    analyzer = AudioRankAnalyzer(data_dir, output_dir)
    
    # 加载数据
    df = analyzer.load_data()
    
    # 数据预处理
    df = analyzer.preprocess_data(df)
    
    # 生成报告
    report_path = generate_report(analyzer, df, output_dir)
    
    log.info(f"分析完成！报告已保存至: {report_path}")
    os.startfile(report_path)
