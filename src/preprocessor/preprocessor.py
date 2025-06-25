"""
数据预处理模块
负责数据清洗、转换和标准化
"""

import re
import json
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import jieba
from collections import Counter

import sys
import os
# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.logger import get_logger
from utils.helpers import load_yaml, save_json

logger = get_logger(__name__)


class BasePreprocessor:
    """数据预处理基类"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化预处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.preprocessing_config = self.config.get("preprocessing", {})
    
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
    
    def process(self, data: Any) -> Any:
        """
        处理数据的主方法
        
        Args:
            data: 输入数据
            
        Returns:
            处理后的数据
        """
        raise NotImplementedError("子类必须实现process方法")


class TextPreprocessor(BasePreprocessor):
    """文本数据预处理器"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化文本预处理器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.text_config = self.preprocessing_config.get("text", {})
        
        # 加载停用词
        self.stopwords = set()
        if self.text_config.get("remove_stopwords", True):
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
            else:
                logger.warning(f"停用词文件不存在: {stopwords_path}")
        except Exception as e:
            logger.error(f"加载停用词失败: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 输入文本
            
        Returns:
            str: 清理后的文本
        """
        if not isinstance(text, str):
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除标点符号
        if self.text_config.get("remove_punctuation", True):
            text = re.sub(r'[^\w\s]', '', text)
        
        # 移除数字
        if self.text_config.get("remove_numbers", False):
            text = re.sub(r'\d+', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def segment_text(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 分词结果
        """
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        min_length = self.text_config.get("min_word_length", 2)
        max_length = self.text_config.get("max_word_length", 20)
        
        words = [
            word for word in words
            if word not in self.stopwords
            and min_length <= len(word) <= max_length
        ]
        
        return words
    
    def process(self, text: str) -> Dict:
        """
        处理文本
        
        Args:
            text: 输入文本
            
        Returns:
            Dict: 处理结果，包含清理后的文本、分词结果等
        """
        # 清理文本
        cleaned_text = self.clean_text(text)
        
        # 分词
        words = self.segment_text(cleaned_text)
        
        # 统计词频
        word_freq = Counter(words)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "words": words,
            "word_count": len(words),
            "unique_words": len(word_freq),
            "word_frequency": dict(word_freq.most_common())
        }


class NumericPreprocessor(BasePreprocessor):
    """数值数据预处理器"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化数值预处理器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.numeric_config = self.preprocessing_config.get("numeric", {})
    
    def handle_missing_values(self, data: pd.Series) -> pd.Series:
        """
        处理缺失值
        
        Args:
            data: 输入数据
            
        Returns:
            pd.Series: 处理后的数据
        """
        method = self.numeric_config.get("handle_missing", "mean")
        
        if method == "mean":
            return data.fillna(data.mean())
        elif method == "median":
            return data.fillna(data.median())
        elif method == "mode":
            return data.fillna(data.mode()[0])
        elif method == "remove":
            return data.dropna()
        else:
            logger.warning(f"未知的缺失值处理方法: {method}，使用均值填充")
            return data.fillna(data.mean())
    
    def scale_data(self, data: pd.Series) -> pd.Series:
        """
        数据缩放
        
        Args:
            data: 输入数据
            
        Returns:
            pd.Series: 缩放后的数据
        """
        method = self.numeric_config.get("scaling", "standard")
        
        if method == "standard":
            # 标准化 (Z-score)
            return (data - data.mean()) / data.std()
        elif method == "minmax":
            # 最小-最大缩放
            return (data - data.min()) / (data.max() - data.min())
        elif method == "robust":
            # 稳健缩放
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            return (data - data.median()) / iqr
        elif method == "none":
            return data
        else:
            logger.warning(f"未知的缩放方法: {method}，不进行缩放")
            return data
    
    def detect_outliers(self, data: pd.Series) -> pd.Series:
        """
        检测异常值
        
        Args:
            data: 输入数据
            
        Returns:
            pd.Series: 布尔序列，True表示异常值
        """
        method = self.numeric_config.get("outlier_detection", {}).get("method", "iqr")
        
        if method == "iqr":
            # IQR方法
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            threshold = self.numeric_config.get("outlier_detection", {}).get("threshold", 1.5)
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            return (data < lower_bound) | (data > upper_bound)
        
        elif method == "zscore":
            # Z-score方法
            z_scores = (data - data.mean()) / data.std()
            threshold = self.numeric_config.get("outlier_detection", {}).get("threshold", 3)
            return abs(z_scores) > threshold
        
        else:
            logger.warning(f"未知的异常值检测方法: {method}")
            return pd.Series([False] * len(data))
    
    def process(self, data: pd.Series) -> Dict:
        """
        处理数值数据
        
        Args:
            data: 输入数据
            
        Returns:
            Dict: 处理结果，包含处理后的数据、统计信息等
        """
        # 处理缺失值
        processed_data = self.handle_missing_values(data)
        
        # 检测异常值
        outliers = self.detect_outliers(processed_data)
        
        # 缩放数据
        scaled_data = self.scale_data(processed_data)
        
        # 计算基本统计量
        stats = {
            "mean": processed_data.mean(),
            "median": processed_data.median(),
            "std": processed_data.std(),
            "min": processed_data.min(),
            "max": processed_data.max(),
            "missing_count": data.isna().sum(),
            "outlier_count": outliers.sum()
        }
        
        return {
            "original_data": data.tolist(),
            "processed_data": processed_data.tolist(),
            "scaled_data": scaled_data.tolist(),
            "outliers": outliers.tolist(),
            "statistics": stats
        }


class DataFramePreprocessor(BasePreprocessor):
    """DataFrame数据预处理器"""
    
    def __init__(self, config_path: str = "../../config/analysis_config.yaml"):
        """
        初始化DataFrame预处理器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.text_preprocessor = TextPreprocessor(config_path)
        self.numeric_preprocessor = NumericPreprocessor(config_path)
    
    def process(self, df: pd.DataFrame) -> Dict:
        """
        处理DataFrame数据
        
        Args:
            df: 输入DataFrame
            
        Returns:
            Dict: 处理结果
        """
        results = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isna().sum().to_dict(),
            "column_results": {}
        }
        
        for column in df.columns:
            # 获取列的数据类型
            dtype = df[column].dtype
            
            # 根据数据类型选择相应的预处理器
            if dtype == "object":
                # 文本数据
                column_data = df[column].fillna("")
                column_results = self.text_preprocessor.process(
                    "\n".join(column_data.astype(str))
                )
            elif np.issubdtype(dtype, np.number):
                # 数值数据
                column_results = self.numeric_preprocessor.process(df[column])
            else:
                # 其他类型数据
                logger.warning(f"不支持的数据类型: {dtype}, 列: {column}")
                continue
            
            results["column_results"][column] = column_results
        
        return results


# 示例用法
if __name__ == "__main__":
    # 测试文本预处理
    text_processor = TextPreprocessor()
    sample_text = "这是一个示例文本，包含数字123和标点符号！"
    text_results = text_processor.process(sample_text)
    print("文本预处理结果:", json.dumps(text_results, ensure_ascii=False, indent=2))
    
    # 测试数值预处理
    numeric_processor = NumericPreprocessor()
    sample_data = pd.Series([1, 2, np.nan, 4, 100])  # 包含异常值和缺失值
    numeric_results = numeric_processor.process(sample_data)
    print("\n数值预处理结果:", json.dumps(numeric_results, indent=2))
    
    # 测试DataFrame预处理
    df_processor = DataFramePreprocessor()
    sample_df = pd.DataFrame({
        "text": ["示例文本1", "示例文本2", "示例文本3"],
        "value": [1, 2, 3]
    })
    df_results = df_processor.process(sample_df)
    print("\nDataFrame预处理结果:", json.dumps(df_results, ensure_ascii=False, indent=2))