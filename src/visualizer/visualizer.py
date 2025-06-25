"""
数据可视化模块
负责将分析结果以图表形式展示
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime

# 可视化库
try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# 交互式可视化
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# 词云
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

import sys
import os
# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.logger import get_logger
from utils.helpers import load_yaml, ensure_dir

logger = get_logger(__name__)


class BaseVisualizer:
    """可视化基类"""
    
    def __init__(self, config_path: str = "../../config/visualization_config.yaml"):
        """
        初始化可视化器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.viz_config = self.config.get("visualization", {})
        
        # 创建输出目录
        self.output_dir = "../../data/output/visualizations"
        ensure_dir(self.output_dir)
        
        # 设置样式
        if MATPLOTLIB_AVAILABLE:
            plt.style.use(self.viz_config.get("style", "seaborn-v0_8-whitegrid"))
            
            # 设置中文字体（如果需要）
            if self.viz_config.get("use_chinese_font", False):
                try:
                    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
                    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
                except Exception as e:
                    logger.warning(f"设置中文字体失败: {str(e)}")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 配置信息
        """
        try:
            return load_yaml(config_path)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def visualize(self, data: Any) -> Dict:
        """
        可视化数据的主方法
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 可视化结果路径
        """
        raise NotImplementedError("子类必须实现visualize方法")
    
    def save_figure(self, fig, filename: str, formats: List[str] = None) -> Dict[str, str]:
        """
        保存图表
        
        Args:
            fig: 图表对象
            filename: 文件名（不含扩展名）
            formats: 保存格式列表，默认为["png", "pdf"]
            
        Returns:
            Dict[str, str]: 不同格式的保存路径
        """
        if formats is None:
            formats = self.viz_config.get("output_formats", ["png", "pdf"])
        
        saved_paths = {}
        
        for fmt in formats:
            file_path = os.path.join(self.output_dir, f"{filename}.{fmt}")
            
            try:
                if MATPLOTLIB_AVAILABLE and isinstance(fig, plt.Figure):
                    fig.savefig(file_path, bbox_inches='tight', dpi=300)
                elif PLOTLY_AVAILABLE and (isinstance(fig, go.Figure) or hasattr(fig, 'to_html')):
                    if fmt == 'html':
                        pio.write_html(fig, file_path)
                    elif fmt == 'json':
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fig.to_json())
                    else:
                        pio.write_image(fig, file_path)
                
                saved_paths[fmt] = file_path
                logger.info(f"图表已保存为 {fmt} 格式: {file_path}")
            except Exception as e:
                logger.error(f"保存 {fmt} 格式图表失败: {str(e)}")
        
        return saved_paths


class StatisticalVisualizer(BaseVisualizer):
    """统计数据可视化器"""
    
    def __init__(self, config_path: str = "../../config/visualization_config.yaml"):
        """
        初始化统计数据可视化器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.stats_viz_config = self.viz_config.get("statistical", {})
    
    def visualize(self, data: Dict, prefix: str = "stats") -> Dict:
        """
        可视化统计分析结果
        
        Args:
            data: 统计分析结果
            prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib库不可用，无法进行可视化")
            return {}
        
        results = {}
        
        # 可视化基本统计量
        if "basic_stats" in data:
            basic_stats_paths = self.visualize_basic_stats(data["basic_stats"], f"{prefix}_basic_stats")
            results["basic_stats"] = basic_stats_paths
        
        # 可视化相关性
        if "correlation" in data:
            correlation_paths = self.visualize_correlation(data["correlation"], f"{prefix}_correlation")
            results["correlation"] = correlation_paths
        
        # 可视化分布
        if "distribution" in data:
            distribution_paths = self.visualize_distribution(data["distribution"], f"{prefix}_distribution")
            results["distribution"] = distribution_paths
        
        return results
    
    def visualize_basic_stats(self, basic_stats: Dict, filename_prefix: str) -> Dict:
        """
        可视化基本统计量
        
        Args:
            basic_stats: 基本统计量
            filename_prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        results = {}
        
        try:
            # 创建统计量表格
            if "mean" in basic_stats and "std" in basic_stats:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # 提取均值和标准差
                means = basic_stats["mean"]
                stds = basic_stats["std"]
                
                # 创建DataFrame
                stats_df = pd.DataFrame({
                    "Mean": means,
                    "Std": stds
                })
                
                # 绘制条形图
                stats_df.plot(kind="bar", yerr=stds, ax=ax, alpha=0.7)
                ax.set_title("基本统计量")
                ax.set_ylabel("值")
                ax.set_xlabel("特征")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                
                # 保存图表
                paths = self.save_figure(fig, f"{filename_prefix}_mean_std")
                results["mean_std"] = paths
                plt.close(fig)
        
        except Exception as e:
            logger.error(f"可视化基本统计量失败: {str(e)}")
        
        return results
    
    def visualize_correlation(self, correlation_data: Dict, filename_prefix: str) -> Dict:
        """
        可视化相关性
        
        Args:
            correlation_data: 相关性数据
            filename_prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        results = {}
        
        try:
            if "matrix" in correlation_data:
                # 将相关系数矩阵转换为DataFrame
                corr_matrix = pd.DataFrame(correlation_data["matrix"])
                
                # 绘制热力图
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
                ax.set_title(f"相关系数矩阵 ({correlation_data.get('method', 'pearson')})")
                plt.tight_layout()
                
                # 保存图表
                paths = self.save_figure(fig, f"{filename_prefix}_heatmap")
                results["heatmap"] = paths
                plt.close(fig)
                
                # 如果有强相关特征对，绘制散点图
                if "strong_correlations" in correlation_data and len(correlation_data["strong_correlations"]) > 0:
                    # 这里需要原始数据，但我们没有，所以跳过
                    pass
        
        except Exception as e:
            logger.error(f"可视化相关性失败: {str(e)}")
        
        return results
    
    def visualize_distribution(self, distribution_data: Dict, filename_prefix: str) -> Dict:
        """
        可视化分布
        
        Args:
            distribution_data: 分布数据
            filename_prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        results = {}
        
        try:
            # 为每个特征绘制分布图
            for feature, feature_data in distribution_data.items():
                if "error" in feature_data:
                    continue
                
                if "histogram" in feature_data:
                    # 绘制直方图
                    fig, ax = plt.subplots(figsize=(8, 6))
                    
                    counts = feature_data["histogram"]["counts"]
                    bin_edges = feature_data["histogram"]["bin_edges"]
                    
                    ax.bar(
                        x=bin_edges[:-1],
                        height=counts,
                        width=np.diff(bin_edges),
                        align="edge",
                        alpha=0.7
                    )
                    
                    # 添加正态性检验结果
                    if "normality_test" in feature_data:
                        p_value = feature_data["normality_test"]["p_value"]
                        is_normal = feature_data["normality_test"]["is_normal"]
                        
                        normality_text = f"正态性检验 p值: {p_value:.4f}\n"
                        normality_text += "符合正态分布" if is_normal else "不符合正态分布"
                        
                        ax.text(
                            0.95, 0.95, normality_text,
                            transform=ax.transAxes,
                            verticalalignment="top",
                            horizontalalignment="right",
                            bbox=dict(boxstyle="round", alpha=0.1)
                        )
                    
                    ax.set_title(f"{feature} 分布")
                    ax.set_xlabel("值")
                    ax.set_ylabel("频数")
                    plt.tight_layout()
                    
                    # 保存图表
                    paths = self.save_figure(fig, f"{filename_prefix}_{feature}_histogram")
                    results[f"{feature}_histogram"] = paths
                    plt.close(fig)
        
        except Exception as e:
            logger.error(f"可视化分布失败: {str(e)}")
        
        return results


class TextVisualizer(BaseVisualizer):
    """文本数据可视化器"""
    
    def __init__(self, config_path: str = "../../config/visualization_config.yaml"):
        """
        初始化文本数据可视化器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.text_viz_config = self.viz_config.get("text", {})
    
    def visualize(self, data: Dict, prefix: str = "text") -> Dict:
        """
        可视化文本分析结果
        
        Args:
            data: 文本分析结果
            prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib库不可用，无法进行可视化")
            return {}
        
        results = {}
        
        # 可视化词频
        if "word_frequency" in data:
            word_freq_paths = self.visualize_word_frequency(data["word_frequency"], f"{prefix}_word_freq")
            results["word_frequency"] = word_freq_paths
        
        # 可视化词云
        if "word_frequency" in data and WORDCLOUD_AVAILABLE:
            wordcloud_paths = self.visualize_wordcloud(data["word_frequency"], f"{prefix}_wordcloud")
            results["wordcloud"] = wordcloud_paths
        
        # 可视化情感分析
        if "sentiment_analysis" in data:
            sentiment_paths = self.visualize_sentiment(data["sentiment_analysis"], f"{prefix}_sentiment")
            results["sentiment"] = sentiment_paths
        
        # 可视化主题分析
        if "topic_analysis" in data:
            topic_paths = self.visualize_topics(data["topic_analysis"], f"{prefix}_topics")
            results["topics"] = topic_paths
        
        return results
    
    def visualize_word_frequency(self, word_freq_data: Dict, filename_prefix: str) -> Dict:
        """
        可视化词频
        
        Args:
            word_freq_data: 词频数据
            filename_prefix: 文件名前缀
            
        Returns:
            Dict: 可视化结果路径
        """
        results = {}
        
        try:
            if "top_words" in word_freq_data:
                # 获取前N个高频词
                top_words = word_freq_data["top_words"]
                n_words = min(20, len(top_words))  # 最多显示20个词
                
                # 转换为DataFrame
                df = pd.DataFrame(
                    list(top_words.items())[:n_words],
                    columns=["Word", "Frequency"]
                ).sort_values("Frequency", ascending=True)
                
                # 绘制水平条形图
                fig, ax