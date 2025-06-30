import os
import warnings

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.logger import get_log

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False     # 解决负号显示问题
class DataVisualizer:
    def __init__(self, output_dir=os.path.dirname(__file__).split("\\src")[0]+"\\data\\reporter\\music_rank\\"):
        """
        数据可视化工具类，支持多种业务相关的统计图和词云图生成。
        output_dir: 图表输出目录，默认自动定位到data/reporter/
        """
        self.output_dir = output_dir
        self.log = get_log("DataVisualizer")
        os.makedirs(self.output_dir, exist_ok=True)

    def bar_chart(self, data, x, y, title="柱形图", filename="bar_chart.png", xlabel=None, ylabel=None, note=None):
        """
        绘制通用柱形图，可自定义标题、坐标轴标签和下方说明。
        note: 图表下方的业务说明文字
        """
        plt.figure(figsize=(10,6))
        ax = sns.barplot(x=x, y=y, data=data)
        plt.title(title)
        if xlabel:
            plt.xlabel(xlabel)
        if ylabel:
            plt.ylabel(ylabel)
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        # 图例自适应
        handles, labels = ax.get_legend_handles_labels()
        if labels and len(labels) < 10:
            plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def line_chart(self, data, x, y, title="折线图", filename="line_chart.png"):
        """
        绘制简单折线图
        """
        plt.figure(figsize=(10,6))
        sns.lineplot(x=x, y=y, data=data)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def pie_chart(self, data, labels, values, title="饼图", filename="pie_chart.png"):
        """
        绘制饼图
        """
        plt.figure(figsize=(8,8))
        plt.pie(data[values], labels=data[labels], autopct='%1.1f%%')
        plt.title(title)
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")


    def scatter_plot(self, data, x, y, title="散点图", filename="scatter_plot.png"):
        """
        绘制散点图
        """
        plt.figure(figsize=(10,6))
        sns.scatterplot(x=x, y=y, data=data)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def area_chart(self, data, x, y, title="面积图", filename="area_chart.png"):
        """
        绘制面积图
        """
        plt.figure(figsize=(10,6))
        plt.fill_between(data[x], data[y], alpha=0.5)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def feature_importance_bar(self, feature_scores, feature_names, title="特征重要性条形图", filename="feature_importance.png"):
        """
        绘制特征重要性条形图
        """
        plt.figure(figsize=(10,6))
        sns.barplot(x=feature_scores, y=feature_names, orient='h')
        plt.title(title)
        plt.xlabel('Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def cluster_heat_distribution(self, data, cluster_col='cluster', heat_col='heat', title="各聚类热度分布", filename="cluster_heat_bar.png"):
        """
        绘制各聚类的热度分布柱形图
        """
        # 统计每个聚类的平均热度
        cluster_mean = data.groupby(cluster_col)[heat_col].mean().reset_index()
        plt.figure(figsize=(8,6))
        sns.barplot(x=cluster_col, y=heat_col, data=cluster_mean)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def rank_heat_trend(self, data, rank_col='rank', heat_col='heat', title="排名与热度趋势", filename="rank_heat_line.png"):
        """
        绘制排名与热度的趋势图
        """
        # 按排名排序
        data_sorted = data.sort_values(by=rank_col)
        plt.figure(figsize=(10,6))
        sns.lineplot(x=rank_col, y=heat_col, data=data_sorted)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def top_singer_heat(self, data, singer_col='singer', heat_col='heat', top_n=10, title="歌手热度TOP10", filename="top_singer_bar.png", note=None):
        """
        绘制热度最高的前N位歌手的热度条形图
        """
        singer_heat = data.groupby(singer_col)[heat_col].sum().sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10,6))
        sns.barplot(x=singer_heat.values, y=singer_heat.index, orient='h')
        plt.title(title)
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def heat_scatter_by_rank(self, data, rank_col='rank', heat_col='heat', title="热度-排名散点图", filename="heat_rank_scatter.png"):
        """
        绘制热度与排名的散点图
        """
        plt.figure(figsize=(10,6))
        sns.scatterplot(x=rank_col, y=heat_col, data=data)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def singer_top_count(self, data, singer_col='singer', top_n=10, title="歌手上榜次数TOP10", filename="singer_top_count.png", note=None):
        """
        绘制上榜次数最多的前N位歌手的条形图
        """
        singer_count = data[singer_col].value_counts().head(top_n)
        plt.figure(figsize=(10,6))
        sns.barplot(x=singer_count.values, y=singer_count.index, orient='h')
        plt.title(title)
        plt.xlabel('上榜次数')
        plt.ylabel('歌手')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def album_top_heat(self, data, album_col='album', heat_col='heat', top_n=10, title="专辑热度TOP10", filename="album_top_heat.png", note=None):
        """
        绘制热度最高的前N张专辑的热度条形图
        """
        album_heat = data.groupby(album_col)[heat_col].sum().sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10,6))
        sns.barplot(x=album_heat.values, y=album_heat.index, orient='h')
        plt.title(title)
        plt.xlabel('热度')
        plt.ylabel('专辑')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def year_heat_trend(self, data, year_col='year', heat_col='heat', title="年度热度趋势", filename="year_heat_trend.png", note=None):
        """
        绘制年度热度变化趋势图
        """
        # 绘制年度热度趋势
        self.log.info("绘制年度热度趋势")
        year_heat = data.groupby(year_col)[heat_col].mean().reset_index()
        plt.figure(figsize=(10,6))
        sns.lineplot(x=year_col, y=heat_col, data=year_heat)
        plt.title(title)
        plt.xlabel('年度')
        plt.ylabel('平均热度')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def year_singer_heat_box(self, data, year_col='year', singer_col='singer', heat_col='heat', title="年度歌手热度分布", filename="year_singer_heat_box.png", note=None):
        """
        绘制年度歌手热度的箱线图
        """
        # 绘制年度歌手热度分布
        self.log.info("绘制年度歌手热度分布")
        plt.figure(figsize=(12,7))
        sns.boxplot(x=year_col, y=heat_col, data=data)
        plt.title(title)
        plt.xlabel('年度')
        plt.ylabel('歌手热度')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def wordcloud_plot(self, text, title="词云图", filename="wordcloud.png", font_path=None, max_words=100):
        """
        生成中文支持的词云图，自动选择系统常见中文字体。
        text: 输入文本（建议用空格分词）
        title: 图表标题
        filename: 输出文件名
        font_path: 字体路径，默认自动选择
        max_words: 最大词数
        """
        self.log.info(f"Generating {filename}")
        from wordcloud import WordCloud, STOPWORDS
        import platform
        plt.figure(figsize=(10, 7))
        # 自动选择常见中文字体
        if font_path is None:
            if platform.system() == "Windows":
                font_path = "C:/Windows/Fonts/simhei.ttf"
            elif platform.system() == "Darwin":
                font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
            else:
                font_path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
        wc = WordCloud(
            background_color="white",
            max_words=max_words,
            font_path=font_path,
            stopwords=STOPWORDS,
            width=800,
            height=400
        )
        wc.generate(text)
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(title, fontsize=18)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

    def year_top1_heat_trend(self, data, year_col='year', rank_col='rank', heat_col='heat', title="年度榜首歌曲热度趋势", filename="year_top1_heat_trend.png", note=None):
        """
        绘制年度榜首歌曲热度的变化趋势图
        """
        # 取每年rank=1的歌曲热度
        self.log.info("年度榜首歌曲热度趋势")
        top1 = data[data[rank_col] == 1].groupby(year_col)[heat_col].mean().reset_index()
        plt.figure(figsize=(10,6))
        sns.lineplot(x=year_col, y=heat_col, data=top1)
        plt.title(title)
        plt.xlabel('年度')
        plt.ylabel('榜首歌曲热度')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def singer_year_heatmap(self, data, singer_col='singer', year_col='year', title="歌手年度上榜次数热力图", filename="singer_year_heatmap.png", top_n=10, note=None):
        """
        绘制歌手年度上榜次数的热力图
        """
        # 统计每年上榜次数最多的歌手
        self.log.info("统计每年上榜次数最多的歌手")
        pivot = data.pivot_table(index=singer_col, columns=year_col, values='title', aggfunc='count', fill_value=0)
        top_singers = pivot.sum(axis=1).sort_values(ascending=False).head(top_n).index
        pivot = pivot.loc[top_singers]
        plt.figure(figsize=(12,7))
        sns.heatmap(pivot, annot=True, fmt='d', cmap='YlGnBu')
        plt.title(title)
        plt.xlabel('年度')
        plt.ylabel('歌手')
        if note:
            plt.figtext(0.5, -0.08, note, ha='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), bbox_inches='tight')
        plt.close()
        self.log.info(f"{filename} saved")

    def association_rule_plot(self, rules, support_col='support', confidence_col='confidence', lift_col='lift', title="关联规则支持度-置信度分布", filename="association_rule_scatter.png"):
        """
        绘制关联规则的支持度-置信度散点图，气泡大小代表提升度
        rules: 包含support/confidence/lift等列的DataFrame
        """
        self.log.info("绘制关联规则支持度-置信度分布散点图")
        plt.figure(figsize=(10,7))
        if rules is None or rules.empty:
            plt.text(0.5, 0.5, '无有效关联规则', fontsize=18, ha='center', va='center')
            plt.xlabel('支持度(support)')
            plt.ylabel('置信度(confidence)')
            plt.title(title)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, filename))
            plt.close()
            self.log.info(f"{filename} saved (empty)")
            return
        sc = plt.scatter(rules[support_col], rules[confidence_col], s=rules[lift_col]*50, alpha=0.6, c=rules[lift_col], cmap='viridis')
        plt.colorbar(sc, label='提升度(lift)')
        plt.xlabel('支持度(support)')
        plt.ylabel('置信度(confidence)')
        plt.title(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.close()
        self.log.info(f"{filename} saved")

def main():
    df = pd.read_csv(os.path.dirname(__file__).split("\\src")[0]+"\\data\\preprocessed\\all_music_rank.csv")
    vis = DataVisualizer()
    # 歌手热度TOP10
    vis.top_singer_heat(df, singer_col='singer', heat_col='heat', top_n=10, title="歌手热度TOP10", note="展示热度最高的10位歌手，反映榜单头部歌手分布。")
    # 歌手上榜次数TOP10
    vis.singer_top_count(df, singer_col='singer', top_n=10, title="歌手上榜次数TOP10", note="统计上榜次数最多的歌手，体现歌手持续影响力。")
    # 专辑热度TOP10
    vis.album_top_heat(df, album_col='album', heat_col='heat', top_n=10, title="专辑热度TOP10", note="展示热度最高的10张专辑，反映专辑受欢迎程度。")
    # 年度热度趋势
    vis.year_heat_trend(df, year_col='year', heat_col='heat', title="年度热度趋势", note="分析各年度平均热度变化，洞察整体流行趋势。")
    # 年度歌手热度分布箱线图
    vis.year_singer_heat_box(df, year_col='year', singer_col='singer', heat_col='heat', title="年度歌手热度分布", note="展示不同年度歌手热度分布，反映年度间差异。")
    # 年度榜首歌曲热度趋势
    vis.year_top1_heat_trend(df, year_col='year', rank_col='rank', heat_col='heat', title="年度榜首歌曲热度趋势", note="展示每年榜首歌曲的热度变化，反映年度流行巅峰。")
    # 歌手年度上榜次数热力图
    vis.singer_year_heatmap(df, singer_col='singer', year_col='year', title="歌手年度上榜次数热力图", top_n=10, note="统计头部歌手在各年度的上榜活跃度。")
    # 词云图：标题
    vis.wordcloud_plot(' '.join(df['title'].astype(str)), title="歌曲标题词云", filename="title_wordcloud.png")
    # 词云图：歌手
    vis.wordcloud_plot(' '.join(df['singer'].astype(str)), title="歌手词云", filename="singer_wordcloud.png")
    # 词云图：专辑
    vis.wordcloud_plot(' '.join(df['album'].astype(str)), title="专辑词云", filename="album_wordcloud.png")

    # 关联规则挖掘与可视化（多策略自动尝试，最大化生成有效规则）
    from mlxtend.preprocessing import TransactionEncoder
    from mlxtend.frequent_patterns import apriori, association_rules
    def try_apriori(transactions, min_support_list=[0.02, 0.01, 0.005], min_conf=0.2):
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        basket = pd.DataFrame(te_ary, columns=te.columns_)
        for min_sup in min_support_list:
            frequent_itemsets = apriori(basket, min_support=min_sup, use_colnames=True)
            if not frequent_itemsets.empty:
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_conf)
                rules = rules[(rules['support'] > 0) & (rules['confidence'] > 0) & (rules['lift'] > 1)]
                if not rules.empty:
                    return rules, min_sup
        return None, None

    # 1. 歌手+专辑联合事务
    transactions = []
    for _, row in df.iterrows():
        singers = [s.strip() for s in str(row['singer']).split(',') if s.strip()]
        albums = [a.strip() for a in str(row['album']).split(',') if a.strip()]
        transaction = singers + albums
        transactions.append(transaction)
    rules, used_sup = try_apriori(transactions)
    if rules is not None:
        vis.association_rule_plot(rules, support_col='support', confidence_col='confidence', lift_col='lift',
                                  title=f"歌手/专辑关联规则支持度-置信度分布(min_support={used_sup})", filename="association_rule_scatter.png")
    else:
        # 2. 只用歌手字段
        transactions = [[s.strip() for s in str(row['singer']).split(',') if s.strip()] for _, row in df.iterrows()]
        rules, used_sup = try_apriori(transactions)
        if rules is not None:
            vis.association_rule_plot(rules, support_col='support', confidence_col='confidence', lift_col='lift',
                                      title=f"歌手关联规则支持度-置信度分布(min_support={used_sup})", filename="association_rule_scatter.png")
        else:
            # 3. 只用专辑字段
            transactions = [[a.strip() for a in str(row['album']).split(',') if a.strip()] for _, row in df.iterrows()]
            rules, used_sup = try_apriori(transactions)
            if rules is not None:
                vis.association_rule_plot(rules, support_col='support', confidence_col='confidence', lift_col='lift',
                                          title=f"专辑关联规则支持度-置信度分布(min_support={used_sup})", filename="association_rule_scatter.png")

