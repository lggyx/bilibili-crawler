import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import jieba
from collections import Counter
from src.utils.logger import get_log

class VideoDanmakuAnalyzer:
    def __init__(self):
        self.log = get_log("VideoDanmakuAnalyzer")
        self.df = None
        self.latest_file = None
        self.pre_dir = os.path.abspath(os.path.join(os.path.dirname(__file__).split("\\src")[0], 'data', 'preprocessed'))
        self.output_dir = os.path.dirname(__file__).split("\\src")[0] + "\\data\\reporter\\video_danmaku\\"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """自动查找最新弹幕csv并加载"""
        pattern = re.compile(r'^视频弹幕数据-.*_preprocessed.csv$')
        matched_files = [f for f in os.listdir(self.pre_dir) if pattern.match(f)]
        if not matched_files:
            self.log.error("未找到弹幕预处理数据文件")
            return False
        self.latest_file = max(matched_files, key=lambda f: os.path.getmtime(os.path.join(self.pre_dir, f)))
        file_path = os.path.join(self.pre_dir, self.latest_file)
        self.df = pd.read_csv(file_path)
        self.log.info(f"已加载数据文件: {self.latest_file}, 共{len(self.df)}条弹幕")
        return True

    def basic_stats(self):
        """基础统计"""
        stats = {
            '弹幕总数': len(self.df),
            '不同类型弹幕数': self.df['type'].nunique() if 'type' in self.df.columns else 0,
            '用户数': self.df['user_hash'].nunique() if 'user_hash' in self.df.columns else 0,
        }
        stats['平均每用户弹幕数'] = round(stats['弹幕总数'] / stats['用户数'], 2) if stats['用户数'] else 0
        self.log.info(f"基础统计: {stats}")
        return stats

    def time_distribution(self):
        """弹幕时间分布直方图"""
        self.df['time'] = pd.to_numeric(self.df['time'], errors='coerce')
        plt.figure(figsize=(12,4))
        sns.histplot(self.df['time'].dropna(), bins=50, kde=False)
        plt.title('弹幕出现时间分布')
        plt.xlabel('视频时间（秒）')
        plt.ylabel('弹幕数')
        img_path = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_time_dist.png'))
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        self.log.info(f"弹幕时间分布图已保存: {img_path}")
        return img_path

    def font_color_distribution(self):
        """字体大小分布和颜色分布Top10"""
        # 字体大小
        plt.figure(figsize=(6,3))
        self.df['font_size'].value_counts().sort_index().plot(kind='bar')
        plt.title('弹幕字体大小分布')
        plt.xlabel('字体大小')
        plt.ylabel('数量')
        font_img = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_font_size.png'))
        plt.tight_layout()
        plt.savefig(font_img)
        plt.close()
        # 颜色分布
        plt.figure(figsize=(8,3))
        top_colors = self.df['color'].value_counts().head(10)
        top_colors.plot(kind='bar', color=[f'#{int(c):06x}' for c in top_colors.index])
        plt.title('弹幕颜色分布Top10')
        plt.xlabel('颜色（十进制）')
        plt.ylabel('数量')
        color_img = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_color_top10.png'))
        plt.tight_layout()
        plt.savefig(color_img)
        plt.close()
        self.log.info(f"字体大小分布图: {font_img}, 颜色分布图: {color_img}")
        return font_img, color_img

    def wordcloud_analysis(self):
        """高频词统计与词云"""
        all_text = ' '.join(self.df['content'].astype(str))
        words = jieba.lcut(all_text)
        stopwords = set(list(STOPWORDS) + ['，', '。', '！', '？', '的', '了', '是', '我', '你', '他', '在', '也', '有', '和', '就', '都', '不', '啊', '吧', '吗', '着', '这', '一个'])
        words = [w for w in words if w.strip() and w not in stopwords]
        word_freq = Counter(words)
        wc = WordCloud(font_path='simhei.ttf', background_color='white', width=800, height=400, stopwords=stopwords).generate(' '.join(words))
        wc_img = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_wordcloud.png'))
        plt.figure(figsize=(10,5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title('弹幕内容词云')
        plt.tight_layout()
        plt.savefig(wc_img)
        plt.close()
        self.log.info(f"词云图已保存: {wc_img}")
        return word_freq.most_common(20), wc_img

    def user_activity(self):
        """用户活跃度分析"""
        user_counts = self.df['user_hash'].value_counts()
        # Top20活跃用户柱状图
        plt.figure(figsize=(10,4))
        user_counts.head(20).plot(kind='bar')
        plt.title('Top20活跃用户弹幕数')
        plt.xlabel('用户Hash')
        plt.ylabel('弹幕数')
        top_user_img = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_top20_user.png'))
        plt.tight_layout()
        plt.savefig(top_user_img)
        plt.close()
        # 用户活跃度分布直方图
        plt.figure(figsize=(8,4))
        user_counts.plot(kind='hist', bins=30, alpha=0.7)
        plt.title('用户活跃度分布')
        plt.xlabel('弹幕数')
        plt.ylabel('用户数')
        user_hist_img = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_user_hist.png'))
        plt.tight_layout()
        plt.savefig(user_hist_img)
        plt.close()
        self.log.info(f"用户活跃度图已保存: {top_user_img}, {user_hist_img}")
        return top_user_img, user_hist_img

    def generate_report(self):
        """自动生成markdown报告和图片"""
        stats = self.basic_stats()
        time_img = self.time_distribution()
        font_img, color_img = self.font_color_distribution()
        word_freq, wc_img = self.wordcloud_analysis()
        top_user_img, user_hist_img = self.user_activity()
        summary = f"""
# 分析结论摘要\n
- 弹幕总数：{stats['弹幕总数']}
- 不同类型弹幕数：{stats['不同类型弹幕数']}
- 用户数：{stats['用户数']}
- 平均每用户弹幕数：{stats['平均每用户弹幕数']}
- 高频词Top10：{', '.join([w for w, _ in word_freq[:10]])}
"""
        md_path = os.path.join(self.output_dir, self.latest_file.replace('.csv', '_danmaku_analysis_summary.md'))
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        self.log.info(f"分析摘要已保存为 {md_path}")
        return md_path, [time_img, font_img, color_img, wc_img, top_user_img, user_hist_img]

    def run_analyzer(self):
        if not self.load_data():
            return
        self.generate_report()

videoDanmakuAnalyzer = VideoDanmakuAnalyzer()
