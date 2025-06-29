from src.utils.logger import get_log
import pandas as pd

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

# 示例用法
if __name__ == "__main__":
    analyzer = MusicRankAnalyzer()
    analyzer.load_data("data/preprocessed/all_music_rank.csv")
    features = analyzer.feature_selection()
    if features is not None:
        print(features.head())
    else:
        print("特征选择失败，请检查日志信息")