import os

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2

from src.analyzer import music_rank_data_modeling, music_rank_visualization
from src.utils.logger import get_log

class MusicRankAnalyzer:
    def __init__(self):
        self.log = get_log("MusicRankAnalyzer")
        self.data = None
        # 定义数值型特征列，避免硬编码
        self.numeric_columns = ['heat', 'rank']

    def load_data(self, file_path):
        """加载预处理后的CSV数据"""
        try:
            self.data = pd.read_csv(file_path)
            self.log.info(f"成功加载数据: {file_path}")
            self.log.debug(f"数据列名: {list(self.data.columns)}")  # 记录列名信息
        except FileNotFoundError:
            self.log.error(f"文件未找到: {file_path}")
        except pd.errors.EmptyDataError:
            self.log.error(f"文件为空: {file_path}")
        except Exception as e:
            self.log.error(f"加载数据失败: {e}")

    def feature_selection(self):
        """特征选择：保留数值型特征列"""
        if self.data is None:
            self.log.error("数据未加载，请先调用load_data方法")
            return None

        # 检查所需列是否存在
        missing_columns = [col for col in self.numeric_columns if col not in self.data.columns]
        if missing_columns:
            self.log.warning(f"缺少以下列: {missing_columns}，无法完成特征选择")
            return None

        # 仅保留数值型特征列
        selected_features = self.data[self.numeric_columns]

        self.log.info(f"特征选择完成，保留特征: {self.numeric_columns}")
        return selected_features

    def advanced_feature_selection(self, k=2):
        """高级特征选择：使用卡方检验选择重要特征"""
        if self.data is None:
            self.log.error("数据未加载，请先调用load_data方法")
            return None

        # 检查数值型列是否存在
        missing_columns = [col for col in self.numeric_columns if col not in self.data.columns]
        if missing_columns:
            self.log.warning(f"缺少以下列: {missing_columns}，无法完成特征选择")
            return None

        try:
            # 提取数值型特征和目标列
            X = self.data[self.numeric_columns]
            y = self.data['target'] if 'target' in self.data.columns else np.zeros(len(self.data))

            # 使用卡方检验选择特征
            selector = SelectKBest(score_func=chi2, k=k)
            selector.fit_transform(X, y)

            selected_features = selector.get_support(indices=True)
            selected_columns = [self.numeric_columns[i] for i in selected_features]

            self.log.info(f"高级特征选择完成，保留特征: {selected_columns}")
            return self.data[selected_columns]
        except Exception as e:
            self.log.error(f"高级特征选择失败: {e}")
            return None

    def run_analyzer(self):
        analyzer = MusicRankAnalyzer()
        analyzer.load_data(os.path.dirname(__file__).split("\\src")[0]+"\\data\\preprocessed\\all_music_rank.csv")
        features = analyzer.feature_selection()
        log=get_log("MusicRankAnalyzer")
        if features is not None:
            log.info(features.head())
            music_rank_data_modeling.main()
            music_rank_visualization.main()

        else:
            log.error("特征选择失败，请检查日志信息")

musicRankAnalyzer = MusicRankAnalyzer()