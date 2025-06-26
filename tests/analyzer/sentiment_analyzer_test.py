import unittest
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
from sklearn.metrics import precision_score, recall_score, f1_score
import jieba

class SentimentAnalyzerTest(unittest.TestCase):
    def setUp(self):
        # 示例评论数据和标签（0：负面，1：正面）
        self.comments = [
            "这个视频太棒了，学到很多知识",      # 正面
            "UP主讲得特别好，很专业",           # 正面
            "画质清晰，内容充实",               # 正面
            "视频太短了，讲得不够详细",         # 负面
            "内容质量一般，不太推荐",           # 负面
            "节奏太慢，浪费时间",               # 负面
            "制作很用心，值得三连",             # 正面
            "音质太差，听不清楚",               # 负面
            "干货满满，收藏了",                 # 正面
            "完全看不懂在讲什么"                # 负面
        ]
        self.labels = [1, 1, 1, 0, 0, 0, 1, 0, 1, 0]  # 对应的情感标签

    def test_feature_extraction(self):
        """测试TF-IDF特征提取"""
        # 分词处理
        segmented_comments = [' '.join(jieba.cut(comment)) for comment in self.comments]
        
        # TF-IDF特征提取
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_comments)
        
        # 验证特征提取结果
        self.assertEqual(X.shape[0], len(self.comments))  # 样本数量应该相同
        self.assertGreater(X.shape[1], 0)  # 特征数量应该大于0
        
        # 检查一些重要词语是否在特征中
        feature_names = vectorizer.get_feature_names_out()
        self.assertTrue(any('视频' in name for name in feature_names))
        self.assertTrue(any('质量' in name for name in feature_names))

    def test_feature_selection(self):
        """测试特征选择（使用卡方检验）"""
        # 分词和特征提取
        segmented_comments = [' '.join(jieba.cut(comment)) for comment in self.comments]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_comments)
        
        # 使用卡方检验选择最重要的特征
        k = 5  # 选择前5个最重要的特征
        selector = SelectKBest(chi2, k=k)
        X_selected = selector.fit_transform(X, self.labels)
        
        # 验证特征选择结果
        self.assertEqual(X_selected.shape[1], k)  # 确保只选择了k个特征
        self.assertEqual(X_selected.shape[0], len(self.comments))  # 样本数量应保持不变

    def test_model_training(self):
        """测试模型训练和评估"""
        # 准备数据
        segmented_comments = [' '.join(jieba.cut(comment)) for comment in self.comments]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_comments)
        y = np.array(self.labels)
        
        # 创建并训练模型
        model = MultinomialNB()
        
        # 使用5折交叉验证评估模型
        cv_scores = cross_val_score(model, X, y, cv=5)
        
        # 验证评估结果
        self.assertEqual(len(cv_scores), 5)  # 应该有5个分数
        self.assertTrue(all(0 <= score <= 1 for score in cv_scores))  # 分数应在0-1之间

    def test_model_metrics(self):
        """测试模型评估指标"""
        # 准备数据
        segmented_comments = [' '.join(jieba.cut(comment)) for comment in self.comments]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(segmented_comments)
        y = np.array(self.labels)
        
        # 训练模型
        model = MultinomialNB()
        model.fit(X, y)
        
        # 预测
        y_pred = model.predict(X)
        
        # 计算各种评估指标
        precision = precision_score(y, y_pred)
        recall = recall_score(y, y_pred)
        f1 = f1_score(y, y_pred)
        
        # 验证评估指标
        self.assertTrue(0 <= precision <= 1)
        self.assertTrue(0 <= recall <= 1)
        self.assertTrue(0 <= f1 <= 1)
        
        # 打印评估结果（方便查看）
        print(f"\nModel Evaluation Metrics:")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")
        print(f"F1-score: {f1:.3f}")

if __name__ == '__main__':
    unittest.main()