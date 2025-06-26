import unittest
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

class AssociationAnalyzerTest(unittest.TestCase):
    def setUp(self):
        # 模拟用户观看历史数据
        # 每个列表代表一个用户观看过的视频ID
        self.user_watch_history = [
            ['视频A', '视频B', '视频D'],
            ['视频B', '视频C', '视频E'],
            ['视频A', '视频B', '视频C'],
            ['视频A', '视频D', '视频E'],
            ['视频B', '视频C', '视频E'],
            ['视频A', '视频B', '视频D', '视频E'],
            ['视频B', '视频C', '视频D'],
            ['视频A', '视频B', '视频E'],
            ['视频A', '视频C', '视频D'],
            ['视频B', '视频D', '视频E']
        ]
        
        # 视频标题映射（用于结果解释）
        self.video_titles = {
            '视频A': '【游戏】最新RPG游戏攻略',
            '视频B': '【游戏】游戏主播搞笑集锦',
            '视频C': '【学习】Python编程入门',
            '视频D': '【游戏】英雄联盟比赛解说',
            '视频E': '【学习】数据分析实战'
        }

    def test_transaction_encoding(self):
        """测试交易编码（将观看历史转换为二进制矩阵）"""
        # 使用TransactionEncoder将列表数据转换为适合关联规则挖掘的格式
        te = TransactionEncoder()
        te_ary = te.fit_transform(self.user_watch_history)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 验证编码结果
        self.assertEqual(df.shape[0], len(self.user_watch_history))  # 行数应等于用户数
        self.assertEqual(set(df.columns), set(['视频A', '视频B', '视频C', '视频D', '视频E']))  # 列应为所有视频ID
        
        # 打印部分数据（方便查看）
        print("\n交易编码结果（前3行）:")
        print(df.head(3))

    def test_frequent_itemsets(self):
        """测试频繁项集挖掘"""
        # 编码数据
        te = TransactionEncoder()
        te_ary = te.fit_transform(self.user_watch_history)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 使用Apriori算法挖掘频繁项集
        min_support = 0.3  # 最小支持度
        frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
        
        # 验证频繁项集结果
        self.assertGreater(len(frequent_itemsets), 0)  # 应该找到至少一个频繁项集
        
        # 打印频繁项集（方便查看）
        print("\n频繁项集（最小支持度=0.3）:")
        for index, row in frequent_itemsets.iterrows():
            items = list(row['itemsets'])
            support = row['support']
            print(f"项集: {items}, 支持度: {support:.3f}")

    def test_association_rules_mining(self):
        """测试关联规则挖掘"""
        # 编码数据
        te = TransactionEncoder()
        te_ary = te.fit_transform(self.user_watch_history)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 挖掘频繁项集
        frequent_itemsets = apriori(df, min_support=0.3, use_colnames=True)
        
        # 生成关联规则
        min_confidence = 0.7  # 最小置信度
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        # 验证关联规则结果
        if len(rules) > 0:  # 可能没有满足最小置信度的规则
            self.assertTrue(all(rules['confidence'] >= min_confidence))
            
            # 打印关联规则（方便查看）
            print("\n关联规则（最小置信度=0.7）:")
            for index, rule in rules.iterrows():
                antecedents = list(rule['antecedents'])
                consequents = list(rule['consequents'])
                support = rule['support']
                confidence = rule['confidence']
                lift = rule['lift']
                
                # 将视频ID转换为标题（如果有映射）
                ant_titles = [self.video_titles.get(vid, vid) for vid in antecedents]
                con_titles = [self.video_titles.get(vid, vid) for vid in consequents]
                
                print(f"规则: {antecedents} -> {consequents}")
                print(f"标题: {ant_titles} -> {con_titles}")
                print(f"支持度: {support:.3f}, 置信度: {confidence:.3f}, 提升度: {lift:.3f}")
                print("---")
        else:
            print("\n没有找到满足最小置信度的关联规则。")

    def test_rule_evaluation(self):
        """测试关联规则评估"""
        # 编码数据
        te = TransactionEncoder()
        te_ary = te.fit_transform(self.user_watch_history)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # 挖掘频繁项集
        frequent_itemsets = apriori(df, min_support=0.2, use_colnames=True)
        
        # 生成关联规则（使用较低的置信度以确保有规则生成）
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
        
        if len(rules) > 0:
            # 按提升度排序
            rules_sorted = rules.sort_values('lift', ascending=False)
            
            # 验证排序结果
            if len(rules_sorted) > 1:
                self.assertGreaterEqual(rules_sorted.iloc[0]['lift'], rules_sorted.iloc[1]['lift'])
            
            # 打印排序后的前3条规则（方便查看）
            print("\n按提升度排序的前3条规则:")
            for index, rule in rules_sorted.head(3).iterrows():
                antecedents = list(rule['antecedents'])
                consequents = list(rule['consequents'])
                support = rule['support']
                confidence = rule['confidence']
                lift = rule['lift']
                
                print(f"规则: {antecedents} -> {consequents}")
                print(f"支持度: {support:.3f}, 置信度: {confidence:.3f}, 提升度: {lift:.3f}")
                print("---")
            
            # 找出最有价值的规则（提升度最高且支持度不太低的规则）
            valuable_rules = rules[(rules['lift'] > 1.2) & (rules['support'] > 0.25)]
            print(f"\n找到 {len(valuable_rules)} 条有价值的规则（提升度>1.2且支持度>0.25）")
        else:
            print("\n没有找到满足条件的关联规则。")

if __name__ == '__main__':
    unittest.main()