"""
数据分析模块
负责对预处理后的数据进行分析
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple
from collections import Counter
import re
from datetime import datetime

# 统计分析
from scipy import stats
import statsmodels.api as sm

# 文本分析
try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

# 机器学习
try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

import sys
import os
# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.logger import get_logger
from utils.helpers import load_yaml, save_json, ensure_dir

logger = get_logger(__name__)


class BaseAnalyzer:
    """分析器基类"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.analysis_config = self.config.get("analysis", {})
        
        # 创建输出目录
        self.output_dir = "../../data/output"
        ensure_dir(self.output_dir)
    
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
    
    def analyze(self, data: Any) -> Dict:
        """
        分析数据的主方法
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 分析结果
        """
        raise NotImplementedError("子类必须实现analyze方法")
    
    def save_results(self, results: Dict, filename: str) -> str:
        """
        保存分析结果
        
        Args:
            results: 分析结果
            filename: 文件名
            
        Returns:
            str: 保存的文件路径
        """
        file_path = os.path.join(self.output_dir, filename)
        save_json(file_path, results)
        logger.info(f"分析结果已保存到: {file_path}")
        return file_path


class StatisticalAnalyzer(BaseAnalyzer):
    """统计分析器"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化统计分析器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.stats_config = self.analysis_config.get("statistical", {})
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """
        对数据进行统计分析
        
        Args:
            data: 输入数据DataFrame
            
        Returns:
            Dict: 分析结果
        """
        results = {
            "basic_stats": self.basic_statistics(data),
            "correlation": self.correlation_analysis(data),
            "distribution": self.distribution_analysis(data)
        }
        
        # 如果配置了假设检验，则进行假设检验
        if self.stats_config.get("hypothesis_testing", {}).get("enabled", False):
            results["hypothesis_tests"] = self.hypothesis_testing(data)
        
        return results
    
    def basic_statistics(self, data: pd.DataFrame) -> Dict:
        """
        计算基本统计量
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 基本统计量
        """
        # 只对数值列进行统计
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            logger.warning("没有数值列可以进行统计分析")
            return {}
        
        # 计算基本统计量
        stats_dict = {
            "count": numeric_data.count().to_dict(),
            "mean": numeric_data.mean().to_dict(),
            "std": numeric_data.std().to_dict(),
            "min": numeric_data.min().to_dict(),
            "25%": numeric_data.quantile(0.25).to_dict(),
            "50%": numeric_data.median().to_dict(),
            "75%": numeric_data.quantile(0.75).to_dict(),
            "max": numeric_data.max().to_dict(),
            "skewness": numeric_data.skew().to_dict(),
            "kurtosis": numeric_data.kurtosis().to_dict()
        }
        
        return stats_dict
    
    def correlation_analysis(self, data: pd.DataFrame) -> Dict:
        """
        相关性分析
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 相关性分析结果
        """
        # 只对数值列进行相关性分析
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            logger.warning("没有数值列可以进行相关性分析")
            return {}
        
        # 计算相关系数
        corr_method = self.stats_config.get("correlation", {}).get("method", "pearson")
        
        try:
            # 将相关系数矩阵转换为字典
            corr_matrix = numeric_data.corr(method=corr_method).to_dict()
            
            # 找出强相关的特征对
            threshold = self.stats_config.get("correlation", {}).get("threshold", 0.7)
            strong_correlations = []
            
            for col1 in numeric_data.columns:
                for col2 in numeric_data.columns:
                    if col1 != col2:
                        corr = abs(numeric_data[col1].corr(numeric_data[col2], method=corr_method))
                        if corr >= threshold:
                            strong_correlations.append({
                                "feature1": col1,
                                "feature2": col2,
                                "correlation": corr
                            })
            
            return {
                "method": corr_method,
                "matrix": corr_matrix,
                "strong_correlations": strong_correlations
            }
        except Exception as e:
            logger.error(f"相关性分析失败: {str(e)}")
            return {"error": str(e)}
    
    def distribution_analysis(self, data: pd.DataFrame) -> Dict:
        """
        分布分析
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 分布分析结果
        """
        # 只对数值列进行分布分析
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            logger.warning("没有数值列可以进行分布分析")
            return {}
        
        distribution_results = {}
        
        for column in numeric_data.columns:
            column_data = numeric_data[column].dropna()
            
            if len(column_data) < 10:
                logger.warning(f"列 {column} 的数据点太少，无法进行分布分析")
                continue
            
            try:
                # 正态性检验
                shapiro_test = stats.shapiro(column_data)
                
                # 计算分位数
                quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
                quantile_values = [float(column_data.quantile(q)) for q in quantiles]
                
                # 计算直方图数据
                hist_data, bin_edges = np.histogram(column_data, bins='auto')
                
                distribution_results[column] = {
                    "normality_test": {
                        "test": "shapiro",
                        "statistic": float(shapiro_test[0]),
                        "p_value": float(shapiro_test[1]),
                        "is_normal": shapiro_test[1] > 0.05
                    },
                    "quantiles": {str(int(q*100))+"%": val for q, val in zip(quantiles, quantile_values)},
                    "histogram": {
                        "counts": hist_data.tolist(),
                        "bin_edges": bin_edges.tolist()
                    }
                }
            except Exception as e:
                logger.error(f"列 {column} 的分布分析失败: {str(e)}")
                distribution_results[column] = {"error": str(e)}
        
        return distribution_results
    
    def hypothesis_testing(self, data: pd.DataFrame) -> Dict:
        """
        假设检验
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 假设检验结果
        """
        # 获取假设检验配置
        test_config = self.stats_config.get("hypothesis_testing", {})
        test_type = test_config.get("type", "t_test")
        
        if not test_config.get("columns"):
            logger.warning("未指定假设检验的列")
            return {}
        
        test_results = {}
        
        try:
            if test_type == "t_test":
                # 单样本t检验
                for column in test_config.get("columns", []):
                    if column not in data.columns:
                        logger.warning(f"列 {column} 不存在")
                        continue
                    
                    column_data = data[column].dropna()
                    
                    if not np.issubdtype(column_data.dtype, np.number):
                        logger.warning(f"列 {column} 不是数值类型")
                        continue
                    
                    # 获取假设均值
                    mu = test_config.get("mu", 0)
                    
                    # 执行t检验
                    t_stat, p_value = stats.ttest_1samp(column_data, mu)
                    
                    test_results[column] = {
                        "test": "t_test",
                        "mu": mu,
                        "t_statistic": float(t_stat),
                        "p_value": float(p_value),
                        "reject_null": p_value < 0.05
                    }
            
            elif test_type == "chi2_test":
                # 卡方检验
                for column_pair in test_config.get("column_pairs", []):
                    if len(column_pair) != 2:
                        logger.warning("卡方检验需要指定两列")
                        continue
                    
                    col1, col2 = column_pair
                    
                    if col1 not in data.columns or col2 not in data.columns:
                        logger.warning(f"列 {col1} 或 {col2} 不存在")
                        continue
                    
                    # 创建列联表
                    contingency_table = pd.crosstab(data[col1], data[col2])
                    
                    # 执行卡方检验
                    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                    
                    test_results[f"{col1}_{col2}"] = {
                        "test": "chi2_test",
                        "chi2_statistic": float(chi2),
                        "p_value": float(p_value),
                        "degrees_of_freedom": int(dof),
                        "reject_null": p_value < 0.05
                    }
        
        except Exception as e:
            logger.error(f"假设检验失败: {str(e)}")
            test_results["error"] = str(e)
        
        return test_results


class TextAnalyzer(BaseAnalyzer):
    """文本分析器"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化文本分析器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.text_config = self.analysis_config.get("text", {})
        
        # 检查jieba是否可用
        if not JIEBA_AVAILABLE:
            logger.warning("jieba库不可用，部分文本分析功能将受限")
        
        # 加载停用词
        self.stopwords = set()
        if self.text_config.get("use_stopwords", True):
            self._load_stopwords()
    
    def _load_stopwords(self):
        """加载停用词"""
        try:
            # 这里可以根据需要加载不同语言的停用词表
            language = self.text_config.get("language", "chinese")
            # 示例路径，实际应该配置在配置文件中
            stopwords_path = f"../../data/resources/stopwords_{language}.txt"
            
            if os.path.exists(stopwords_path):
                with open(stopwords_path, 'r', encoding='utf-8') as f:
                    self.stopwords = set(line.strip() for line in f)
                logger.info(f"已加载 {len(self.stopwords)} 个停用词")
            else:
                logger.warning(f"停用词文件不存在: {stopwords_path}")
        except Exception as e:
            logger.error(f"加载停用词失败: {str(e)}")
    
    def analyze(self, texts: Union[str, List[str], pd.Series]) -> Dict:
        """
        分析文本
        
        Args:
            texts: 输入文本，可以是单个字符串、字符串列表或pandas Series
            
        Returns:
            Dict: 分析结果
        """
        # 将输入转换为列表
        if isinstance(texts, str):
            text_list = [texts]
        elif isinstance(texts, pd.Series):
            text_list = texts.tolist()
        else:
            text_list = texts
        
        # 过滤空文本
        text_list = [text for text in text_list if text and isinstance(text, str)]
        
        if not text_list:
            logger.warning("没有有效的文本可以分析")
            return {}
        
        # 合并所有文本用于整体分析
        all_text = "\n