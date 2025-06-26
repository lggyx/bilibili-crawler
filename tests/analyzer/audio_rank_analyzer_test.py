import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import re
from datetime import datetime
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False     # 解决负号显示问题

class AudioRankAnalyzerTest(unittest.TestCase):
    def setUp(self):
        # 示例数据，实际使用时会被真实数据替换
        self.sample_data = {
            "data": {
                "list": [
                    {
                        "music_id": "MA406539399526893936",
                        "music_title": "爱你",
                        "singer": "王心凌",
                        "album": "爱你",
                        "heat": 1319444,
                        "rank": 1,
                        "creation_aid": 596981019,
                        "creation_bvid": "BV15B4y1X7pq",
                        "creation_cover": "http://i1.hdslb.com/bfs/archive/xxx.jpg",
                        "creation_title": "【猛男版】爱你",
                        "creation_nickname": "猛男舞团IconX",
                        "creation_duration": 119,
                        "creation_play": 6115132
                    }
                ]
            }
        }

    def load_data_from_directory(self, directory_path):
        """从指定目录加载所有音频榜单数据"""
        all_data = []
        pattern = re.compile(r"音频榜单单期信息-热榜-第(\d+)期-(\d{4})年度-")
        
        for filename in os.listdir(directory_path):
            match = pattern.match(filename)
            if match:
                period = int(match.group(1))
                year = int(match.group(2))
                
                with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data['data']['list']:
                        item['period'] = period
                        item['year'] = year
                        all_data.append(item)
        
        return pd.DataFrame(all_data)

    def preprocess_data(self, df):
        """数据预处理"""
        # 处理缺失值
        df = df.fillna({
            'music_title': '未知歌曲',
            'singer': '未知歌手',
            'album': '未知专辑',
            'creation_title': '未知视频',
            'creation_nickname': '未知创作者'
        })
        
        # 添加新的特征
        df['heat_normalized'] = df.groupby('period')['heat'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min())
        )
        
        # 计算播放量与热度的比率
        df['play_heat_ratio'] = df['creation_play'] / df['heat']
        
        return df

    def analyze_heat_trends(self, df):
        """分析热度趋势"""
        plt.figure(figsize=(12, 6))
        
        # 计算每期排名前3的平均热度
        top3_heat = df[df['rank'] <= 3].groupby('period')['heat'].mean()
        
        plt.plot(top3_heat.index, top3_heat.values, marker='o')
        plt.title('音频榜单Top3平均热度趋势')
        plt.xlabel('期数')
        plt.ylabel('平均热度')
        plt.grid(True)
        
        # 保存图表
        plt.savefig('heat_trends.png')
        plt.close()
        
        return top3_heat

    def analyze_singer_distribution(self, df):
        """分析歌手分布"""
        plt.figure(figsize=(12, 6))
        
        # 统计歌手出现次数
        singer_counts = df['singer'].value_counts().head(10)
        
        # 创建横向条形图
        sns.barplot(x=singer_counts.values, y=singer_counts.index)
        plt.title('热门歌手榜单出现次数Top10')
        plt.xlabel('出现次数')
        plt.ylabel('歌手')
        
        # 保存图表
        plt.savefig('singer_distribution.png')
        plt.close()
        
        return singer_counts

    def analyze_creation_performance(self, df):
        """分析创作表现"""
        plt.figure(figsize=(12, 6))
        
        # 计算每个创作者的平均播放量
        creator_avg_play = df.groupby('creation_nickname')['creation_play'].mean().sort_values(ascending=False).head(10)
        
        sns.barplot(x=creator_avg_play.values, y=creator_avg_play.index)
        plt.title('创作者平均播放量Top10')
        plt.xlabel('平均播放量')
        plt.ylabel('创作者')
        
        # 保存图表
        plt.savefig('creator_performance.png')
        plt.close()
        
        return creator_avg_play

    def analyze_correlation_matrix(self, df):
        """分析相关性矩阵"""
        plt.figure(figsize=(10, 8))
        
        # 选择数值型列进行相关性分析
        numeric_columns = ['heat', 'rank', 'creation_duration', 'creation_play', 'play_heat_ratio']
        correlation_matrix = df[numeric_columns].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('特征相关性矩阵')
        
        # 保存图表
        plt.savefig('correlation_matrix.png')
        plt.close()
        
        return correlation_matrix

    def generate_report(self, df):
        """生成分析报告"""
        report = "# 音频榜单数据分析报告\n\n"
        
        # 基础统计信息
        report += "## 1. 基础统计信息\n\n"
        report += f"- 总数据量：{len(df)}条\n"
        report += f"- 统计期数：{df['period'].nunique()}期\n"
        report += f"- 独立歌手数：{df['singer'].nunique()}位\n"
        report += f"- 独立创作者数：{df['creation_nickname'].nunique()}位\n\n"
        
        # 热度分析
        report += "## 2. 热度分析\n\n"
        report += "- 见热度趋势图(heat_trends.png)\n"
        report += f"- 最高热度：{df['heat'].max():,}\n"
        report += f"- 平均热度：{df['heat'].mean():,.0f}\n\n"
        
        # 歌手分析
        report += "## 3. 歌手分析\n\n"
        report += "- 见歌手分布图(singer_distribution.png)\n"
        top_singers = df['singer'].value_counts().head(5)
        report += "- Top5歌手及其出现次数：\n"
        for singer, count in top_singers.items():
            report += f"  * {singer}: {count}次\n"
        report += "\n"
        
        # 创作者分析
        report += "## 4. 创作者分析\n\n"
        report += "- 见创作者表现图(creator_performance.png)\n"
        top_creators = df.groupby('creation_nickname')['creation_play'].mean().sort_values(ascending=False).head(5)
        report += "- Top5创作者及其平均播放量：\n"
        for creator, plays in top_creators.items():
            report += f"  * {creator}: {plays:,.0f}次播放\n"
        report += "\n"
        
        # 相关性分析
        report += "## 5. 相关性分析\n\n"
        report += "- 见相关性矩阵图(correlation_matrix.png)\n"
        report += "- 主要发现：\n"
        report += "  * 热度与播放量呈现正相关\n"
        report += "  * 排名与热度呈现负相关（排名数字越小，热度越高）\n\n"
        
        # 保存报告
        with open('audio_rank_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

    def test_full_analysis(self):
        """完整分析流程测试"""
        # 注意：实际使用时，需要提供真实的数据目录路径
        directory=os.path.dirname(__file__).split("\\bilibili-crawler\\")[0]+"\\bilibili-crawler\\data\\processed"
        df = self.load_data_from_directory(directory)
        
        # # 使用示例数据创建DataFrame
        # df = pd.DataFrame(self.sample_data['data']['list'])
        df['period'] = 1
        df['year'] = 2022
        
        # 数据预处理
        df = self.preprocess_data(df)
        
        # 执行各项分析
        self.analyze_heat_trends(df)
        self.analyze_singer_distribution(df)
        self.analyze_creation_performance(df)
        self.analyze_correlation_matrix(df)
        
        # 生成报告
        report = self.generate_report(df)
        
        # 验证分析结果
        self.assertTrue(os.path.exists('heat_trends.png'))
        self.assertTrue(os.path.exists('singer_distribution.png'))
        self.assertTrue(os.path.exists('creator_performance.png'))
        self.assertTrue(os.path.exists('correlation_matrix.png'))
        self.assertTrue(os.path.exists('audio_rank_analysis_report.md'))

if __name__ == '__main__':
    unittest.main()
