import os.path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from src.utils.logger import get_log


class MusicRankDataModeling:
    def __init__(self):
        self.log = get_log("DataModeling")
        self.data = None

    def load_data(self, file_path):
        """加载数据"""
        try:
            self.data = pd.read_csv(file_path)
            self.log.info(f"成功加载数据: {file_path}")
        except FileNotFoundError:
            self.log.error(f"文件未找到: {file_path}")
        except pd.errors.EmptyDataError:
            self.log.error(f"文件为空: {file_path}")
        except Exception as e:
            self.log.error(f"加载数据失败: {e}")

    def kmeans_clustering(self, n_clusters=3):
        """使用K-means算法进行聚类（仅使用数值型特征）"""
        if self.data is None:
            self.log.error("数据未加载，请先调用load_data方法")
            return None

        try:
            # 只保留数值型特征列
            numeric_data = self.data.select_dtypes(include=['number'])
            if numeric_data.shape[1] == 0:
                self.log.error("没有可用于聚类的数值型特征列")
                return None
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.data['cluster'] = kmeans.fit_predict(numeric_data)

            # 计算轮廓系数
            score = silhouette_score(numeric_data, self.data['cluster'])
            self.log.info(f"聚类完成，轮廓系数: {score}")

            return self.data
        except Exception as e:
            self.log.error(f"聚类失败: {e}")
            return None

def main():
    """示例用法"""
    modeler = MusicRankDataModeling()
    modeler.load_data(os.path.dirname(__file__).split("\\src")[0]+"\\data\\preprocessed\\all_music_rank.csv")
    clustered_data = modeler.kmeans_clustering()
    if clustered_data is not None:
        modeler.log.info(clustered_data.head())
    else:
        modeler.log.error("聚类失败，请检查日志信息")
