import unittest
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import jieba
import matplotlib.pyplot as plt
from collections import Counter

class ClusteringAnalyzerTest(unittest.TestCase):
    def setUp(self):
        # 示例视频标题数据（模拟不同类别的视频）
        self.video_titles = [
            # 游戏类
            "【游戏实况】最新RPG游戏通关攻略",
            "我的世界：如何建造豪华别墅",
            "英雄联盟S13总决赛精彩集锦",
            "游戏主播搞笑时刻合集",
            
            # 学习类
            "高等数学期末复习要点",
            "Python编程入门教程",
            "英语四级听力满分技巧",
            "考研政治知识点总结",
            
            # 生活类
            "夏日清爽减肥食谱分享",
            "三分钟学会化妆技巧",
            "旅行vlog：探索云南秘境",
            "家居收纳整理小窍门"
        ]
        
        # 预期的类别（仅用于验证，实际聚类不使用）
        self.expected_categories = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]  # 0:游戏, 1:学习, 2:生活

    def test_tfidf_vectorization(self):
        """测试TF-IDF向量化"""
        # 分词处理
        segmented_titles = [' '.join(jieba.cut(title)) for title in self.video_titles]
        
        # TF-IDF特征提取
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_titles)
        
        # 验证向量化结果
        self.assertEqual(X.shape[0], len(self.video_titles))  # 样本数量应该相同
        self.assertGreater(X.shape[1], 0)  # 特征数量应该大于0
        
        # 打印一些特征词（方便查看）
        feature_names = vectorizer.get_feature_names_out()
        print(f"\n特征词示例: {feature_names[:10]}")

    def test_kmeans_clustering(self):
        """测试K-means聚类"""
        # 分词和特征提取
        segmented_titles = [' '.join(jieba.cut(title)) for title in self.video_titles]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_titles)
        
        # 设置聚类数量
        n_clusters = 3
        
        # 执行K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # 验证聚类结果
        self.assertEqual(len(clusters), len(self.video_titles))  # 每个样本都应该有一个聚类标签
        self.assertEqual(len(set(clusters)), n_clusters)  # 应该有n_clusters个不同的聚类
        
        # 打印聚类结果（方便查看）
        print("\n聚类结果:")
        for i, (title, cluster) in enumerate(zip(self.video_titles, clusters)):
            print(f"标题: {title} | 聚类: {cluster} | 预期类别: {self.expected_categories[i]}")

    def test_silhouette_score(self):
        """测试使用轮廓系数评估聚类效果"""
        # 分词和特征提取
        segmented_titles = [' '.join(jieba.cut(title)) for title in self.video_titles]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_titles)
        
        # 尝试不同的聚类数量
        silhouette_scores = []
        cluster_range = range(2, 6)  # 尝试2到5个聚类
        
        for n_clusters in cluster_range:
            # 执行K-means聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # 计算轮廓系数
            score = silhouette_score(X, clusters)
            silhouette_scores.append(score)
            
            print(f"聚类数量 {n_clusters}, 轮廓系数: {score:.3f}")
        
        # 验证轮廓系数
        self.assertEqual(len(silhouette_scores), len(cluster_range))
        self.assertTrue(all(-1 <= score <= 1 for score in silhouette_scores))  # 轮廓系数在-1到1之间

    def test_cluster_analysis(self):
        """测试聚类结果分析"""
        # 分词和特征提取
        segmented_titles = [' '.join(jieba.cut(title)) for title in self.video_titles]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_titles)
        
        # 执行K-means聚类
        n_clusters = 3
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # 分析每个聚类的关键词
        feature_names = vectorizer.get_feature_names_out()
        cluster_centers = kmeans.cluster_centers_
        
        print("\n聚类关键词分析:")
        for i in range(n_clusters):
            # 获取该聚类中心的前10个最重要的词
            top_indices = cluster_centers[i].argsort()[-10:][::-1]
            top_features = [feature_names[j] for j in top_indices]
            
            # 获取该聚类的样本
            cluster_samples = [self.video_titles[j] for j in range(len(clusters)) if clusters[j] == i]
            
            print(f"\n聚类 {i}:")
            print(f"关键词: {', '.join(top_features)}")
            print(f"样本数量: {len(cluster_samples)}")
            print(f"样本示例: {cluster_samples[:2]}")
        
        # 验证每个聚类至少有一个样本
        cluster_counts = Counter(clusters)
        self.assertEqual(len(cluster_counts), n_clusters)
        self.assertTrue(all(count > 0 for count in cluster_counts.values()))

if __name__ == '__main__':
    unittest.main()