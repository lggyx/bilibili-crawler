import unittest
import pandas as pd
import numpy as np
import re
import jieba
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder

class DataPreprocessorTest(unittest.TestCase):
    def setUp(self):
        # 创建模拟的B站视频数据
        self.video_data = pd.DataFrame({
            'video_id': ['BV1xx411c7mD', 'BV1Gx411c7mC', 'BV1Hx411c7mB', 'BV1Ix411c7mA', 'BV1Jx411c7m9'],
            'title': [
                '【科普】关于新冠疫苗的十个真相',
                '3分钟学会数据分析【Python教程】',
                '这才是真正的日本东京！实拍vlog',
                '【游戏】我的世界建筑教程：豪华别墅',
                '如何30天减肥10斤【健身教程】'
            ],
            'description': [
                '本视频讲解了关于新冠疫苗的十个科学真相，打破谣言！',
                '简单易学的Python数据分析教程，从入门到精通！',
                '东京旅游必去的地方，绝对和你想的不一样！',
                '我的世界建筑教程，教你如何建造豪华别墅！',
                '科学减肥方法，30天瘦10斤不是梦！'
            ],
            'view_count': [1500000, 250000, 780000, 1200000, 950000],
            'like_count': [120000, 18000, 65000, 95000, 82000],
            'coin_count': [50000, 8000, 25000, 40000, 30000],
            'favorite_count': [80000, 12000, 40000, 60000, 45000],
            'share_count': [20000, 3000, 15000, 18000, 12000],
            'comment_count': [15000, 2500, 8000, 12000, 9000],
            'duration': [1200, 360, 900, 1500, 1080],  # 视频时长（秒）
            'upload_time': [
                '2021-01-15 14:30:00',
                '2021-02-20 10:15:00',
                '2021-03-05 18:45:00',
                '2021-03-15 20:00:00',
                '2021-04-01 12:30:00'
            ],
            'category': ['科学', '教育', '生活', '游戏', '运动'],
            'tags': [
                '科普,疫苗,新冠',
                'Python,教程,数据分析',
                '旅游,日本,vlog',
                '游戏,我的世界,建筑',
                '健身,减肥,教程'
            ]
        })

    def test_handle_missing_values(self):
        """测试处理缺失值"""
        # 创建包含缺失值的数据
        df = self.video_data.copy()
        df.loc[0, 'view_count'] = np.nan
        df.loc[1, 'like_count'] = np.nan
        df.loc[2, 'description'] = np.nan
        
        # 处理缺失值
        # 数值型数据用中位数填充
        numeric_cols = ['view_count', 'like_count', 'coin_count', 'favorite_count', 'share_count', 'comment_count', 'duration']
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        
        # 文本型数据用空字符串填充
        text_cols = ['title', 'description', 'tags']
        for col in text_cols:
            df[col] = df[col].fillna('')
        
        # 验证结果
        self.assertFalse(df['view_count'].isnull().any())
        self.assertFalse(df['like_count'].isnull().any())
        self.assertFalse(df['description'].isnull().any())
        
        # 打印处理结果
        print("\n缺失值处理结果:")
        print(f"view_count[0] = {df['view_count'][0]}")
        print(f"like_count[1] = {df['like_count'][1]}")
        print(f"description[2] = '{df['description'][2]}'")

    def test_normalize_numeric_features(self):
        """测试数值特征归一化"""
        df = self.video_data.copy()
        
        # 选择需要归一化的特征
        numeric_features = ['view_count', 'like_count', 'coin_count', 'favorite_count', 'share_count', 'comment_count']
        
        # Min-Max归一化（将数据缩放到[0,1]区间）
        scaler = MinMaxScaler()
        df[numeric_features] = scaler.fit_transform(df[numeric_features])
        
        # 验证结果
        for col in numeric_features:
            self.assertTrue(df[col].min() >= 0)
            self.assertTrue(df[col].max() <= 1)
        
        # 打印归一化结果
        print("\nMin-Max归一化结果:")
        print(df[numeric_features].head(2))
        
        # Z-score标准化（均值为0，标准差为1）
        df = self.video_data.copy()
        scaler = StandardScaler()
        df[numeric_features] = scaler.fit_transform(df[numeric_features])
        
        # 验证结果
        for col in numeric_features:
            self.assertAlmostEqual(df[col].mean(), 0, delta=1e-10)
            self.assertAlmostEqual(df[col].std(), 1, delta=1e-10)
        
        # 打印标准化结果
        print("\nZ-score标准化结果:")
        print(df[numeric_features].head(2))

    def test_time_feature_extraction(self):
        """测试时间特征提取"""
        df = self.video_data.copy()
        
        # 将字符串时间转换为datetime对象
        df['upload_time'] = pd.to_datetime(df['upload_time'])
        
        # 提取时间特征
        df['upload_year'] = df['upload_time'].dt.year
        df['upload_month'] = df['upload_time'].dt.month
        df['upload_day'] = df['upload_time'].dt.day
        df['upload_hour'] = df['upload_time'].dt.hour
        df['upload_weekday'] = df['upload_time'].dt.dayofweek  # 0=周一，6=周日
        
        # 验证结果
        self.assertEqual(df['upload_year'][0], 2021)
        self.assertEqual(df['upload_month'][0], 1)
        self.assertEqual(df['upload_day'][0], 15)
        
        # 打印时间特征
        print("\n时间特征提取结果:")
        print(df[['upload_time', 'upload_year', 'upload_month', 'upload_day', 'upload_hour', 'upload_weekday']].head(3))
        
        # 计算视频发布至今的天数
        now = datetime.now()
        df['days_since_upload'] = (now - df['upload_time']).dt.days
        
        print("\n视频发布至今的天数:")
        print(df[['upload_time', 'days_since_upload']].head(3))

    def test_categorical_encoding(self):
        """测试类别特征编码"""
        df = self.video_data.copy()
        
        # 标签编码（将类别映射为整数）
        category_mapping = {cat: i for i, cat in enumerate(df['category'].unique())}
        df['category_encoded'] = df['category'].map(category_mapping)
        
        # 验证结果
        self.assertEqual(len(category_mapping), len(df['category'].unique()))
        
        # 打印标签编码结果
        print("\n标签编码结果:")
        print(df[['category', 'category_encoded']].head())
        print(f"类别映射: {category_mapping}")
        
        # One-Hot编码
        encoder = OneHotEncoder(sparse=False)
        onehot = encoder.fit_transform(df[['category']])
        onehot_df = pd.DataFrame(
            onehot, 
            columns=[f'category_{cat}' for cat in encoder.categories_[0]],
            index=df.index
        )
        
        # 将One-Hot编码结果合并到原始数据
        df = pd.concat([df, onehot_df], axis=1)
        
        # 验证结果
        self.assertEqual(onehot_df.shape[1], len(df['category'].unique()))
        
        # 打印One-Hot编码结果
        print("\nOne-Hot编码结果:")
        print(df[['category'] + list(onehot_df.columns)].head())

    def test_text_feature_extraction(self):
        """测试文本特征提取"""
        df = self.video_data.copy()
        
        # 提取标题长度作为特征
        df['title_length'] = df['title'].apply(len)
        
        # 提取标题中的特殊符号数量
        df['title_special_chars'] = df['title'].apply(lambda x: len(re.findall(r'[^\w\s]', x)))
        
        # 提取标题中的数字数量
        df['title_digits'] = df['title'].apply(lambda x: len(re.findall(r'\d', x)))
        
        # 验证结果
        self.assertTrue(all(df['title_length'] > 0))
        
        # 打印文本特征
        print("\n文本特征提取结果:")
        print(df[['title', 'title_length', 'title_special_chars', 'title_digits']].head())
        
        # 处理标签（tags）
        # 将逗号分隔的标签转换为列表
        df['tag_list'] = df['tags'].apply(lambda x: x.split(','))
        
        # 计算每个视频的标签数量
        df['tag_count'] = df['tag_list'].apply(len)
        
        # 打印标签处理结果
        print("\n标签处理结果:")
        print(df[['tags', 'tag_list', 'tag_count']].head(3))

    def test_feature_discretization(self):
        """测试特征离散化"""
        df = self.video_data.copy()
        
        # 将观看次数离散化为区间
        bins = [0, 300000, 800000, float('inf')]
        labels = ['低', '中', '高']
        df['view_count_level'] = pd.cut(df['view_count'], bins=bins, labels=labels)
        
        # 验证结果
        self.assertEqual(len(df['view_count_level'].unique()), len(labels))
        
        # 打印离散化结果
        print("\n观看次数离散化结果:")
        print(df[['video_id', 'view_count', 'view_count_level']].head())
        
        # 将点赞数与观看数的比例离散化
        df['like_view_ratio'] = df['like_count'] / df['view_count']
        ratio_bins = [0, 0.07, 0.09, float('inf')]
        ratio_labels = ['低互动', '中互动', '高互动']
        df['interaction_level'] = pd.cut(df['like_view_ratio'], bins=ratio_bins, labels=ratio_labels)
        
        # 打印互动水平结果
        print("\n互动水平离散化结果:")
        print(df[['video_id', 'view_count', 'like_count', 'like_view_ratio', 'interaction_level']].head())

    def test_data_transformation(self):
        """测试数据变换"""
        df = self.video_data.copy()
        
        # 对高度倾斜的数据进行对数变换
        skewed_features = ['view_count', 'like_count', 'comment_count']
        for feature in skewed_features:
            df[f'{feature}_log'] = np.log1p(df[feature])  # log1p = log(1+x)，避免log(0)
        
        # 验证结果
        for feature in skewed_features:
            self.assertTrue(df[f'{feature}_log'].max() < df[feature].max())
        
        # 打印对数变换结果
        print("\n对数变换结果:")
        for feature in skewed_features:
            print(f"{feature}: 原始范围 [{df[feature].min()}, {df[feature].max()}], "
                  f"变换后范围 [{df[f'{feature}_log'].min():.2f}, {df[f'{feature}_log'].max():.2f}]")
        
        # 创建复合特征
        # 计算互动指数 = (点赞数 + 投币数 + 收藏数) / 观看数
        df['interaction_index'] = (df['like_count'] + df['coin_count'] + df['favorite_count']) / df['view_count']
        
        # 计算评论率 = 评论数 / 观看数
        df['comment_rate'] = df['comment_count'] / df['view_count']
        
        # 打印复合特征结果
        print("\n复合特征结果:")
        print(df[['video_id', 'interaction_index', 'comment_rate']].head())

if __name__ == '__main__':
    unittest.main()