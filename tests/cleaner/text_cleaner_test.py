import unittest
import jieba
import pandas as pd
from collections import Counter

class TextCleanerTest(unittest.TestCase):
    def setUp(self):
        # 示例评论数据
        self.comments = [
            "这个视频真的很好看，很喜欢！",
            "这个视频真的很好看，很喜欢！",  # 重复评论
            "UP主讲得太棒了，我们都学会了",
            "视频质量很高，但是有点短",
            "希望UP主多更新一些视频呢"
        ]
        
        # 示例停用词表
        self.stop_words = {"的", "了", "呢", "我们", "都", "但是", "一些"}

    def test_remove_duplicates(self):
        """测试去除重复评论"""
        # 将评论转换为DataFrame
        df = pd.DataFrame({"comment": self.comments})
        
        # 去重
        df_unique = df.drop_duplicates(subset=["comment"])
        
        # 验证结果
        self.assertEqual(len(df_unique), 4)  # 应该只剩4条评论
        self.assertNotEqual(len(df), len(df_unique))  # 确保去重生效

    def test_word_segmentation(self):
        """测试中文分词"""
        # 选择一条评论进行分词
        comment = "视频质量很高，但是有点短"
        
        # 使用jieba分词
        words = list(jieba.cut(comment))
        
        # 验证分词结果
        self.assertIn("视频", words)
        self.assertIn("质量", words)
        self.assertIn("很", words)
        self.assertIn("高", words)

    def test_remove_stop_words(self):
        """测试去除停用词"""
        # 对评论进行分词
        comment = "UP主讲得太棒了，我们都学会了"
        words = list(jieba.cut(comment))
        
        # 去除停用词
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # 验证结果
        self.assertNotIn("了", filtered_words)
        self.assertNotIn("我们", filtered_words)
        self.assertNotIn("都", filtered_words)
        self.assertIn("UP主", filtered_words)
        self.assertIn("讲", filtered_words)
        self.assertIn("太棒", filtered_words)

    def test_word_frequency(self):
        """测试词频统计"""
        # 所有评论合并分词
        all_words = []
        for comment in self.comments:
            words = jieba.cut(comment)
            all_words.extend([w for w in words if w not in self.stop_words])
        
        # 统计词频
        word_freq = Counter(all_words)
        
        # 验证结果
        self.assertGreater(word_freq["视频"], 1)  # "视频"应该出现多次
        self.assertIn("UP主", word_freq)  # 应该包含"UP主"

if __name__ == '__main__':
    unittest.main()