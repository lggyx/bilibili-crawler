from src.utils.logger import get_log
from src.utils.storager import save_to_csv
import os
import json
import jieba
import csv  # 导入csv模块


def _load_raw_data(filename):
    """加载原始JSON数据文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['data']['list']


def _load_stopwords():
    """加载停用词表"""
    stopwords_path = os.path.dirname(__file__)+"\\stopwords.txt"
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)


class MusicRankPreprocessing:
    def __init__(self):
        self.log = get_log("MusicRankPreprocessing")
        self.stopwords = _load_stopwords()

    def _tokenize(self, text):
        """使用jieba进行分词，并去除停用词"""
        tokens = jieba.cut(text)
        return [token for token in tokens if token not in self.stopwords and token.strip()]

    def process_and_save(self, raw_file, output_file):
        """处理单个原始数据文件并保存为CSV"""
        try:
            # 读取原始数据
            raw_data = _load_raw_data(raw_file)
            
            # 准备处理后的数据
            processed_data = []
            
            # 进行数据处理
            for item in raw_data:
                # 提取需要处理的文本内容
                title = item.get('music_title', '')
                singer = item.get('singer', '')
                album = item.get('album', '')
                creation_title = item.get('creation_title', '')
                
                # 对文本进行分词和停用词过滤
                title_tokens = self._tokenize(title)
                singer_tokens = self._tokenize(singer)
                album_tokens = self._tokenize(album)
                creation_title_tokens = self._tokenize(creation_title)
                
                # 添加到处理后的数据列表
                processed_data.append({
                    'music_id': item.get('music_id', ''),
                    'title': title,
                    'singer': singer,
                    'album': album,
                    'creation_title': creation_title,
                    'title_tokens': ' '.join(title_tokens),
                    'singer_tokens': ' '.join(singer_tokens),
                    'album_tokens': ' '.join(album_tokens),
                    'creation_title_tokens': ' '.join(creation_title_tokens),
                    'heat': item.get('heat', 0),
                    'rank': item.get('rank', 0)
                })
            
            # 保存为CSV文件
            save_to_csv(processed_data, output_file)
            self.log.info(f'数据处理完成，已保存至 {output_file}')
            return True
        except Exception as e:
            self.log.error(f'数据处理失败: {str(e)}')
            return False
    def run_preprocessing(self,raw_file, output_file):
        """静态方法：运行预处理流程"""
        processor = MusicRankPreprocessing()
        return processor.process_and_save(raw_file, output_file)

    def merge_preprocessed_data(self, output_file):
        """将预处理后的所有数据合并为一个文件"""
        # 获取预处理后数据存储目录
        preprocessed_data_dir = os.path.join(os.path.dirname(__file__).split("\\src")[0], "data", "preprocessing")
        
        # 创建输出文件的目录（如果不存在）
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 初始化合并后的数据
        merged_data = []
        
        # 遍历预处理后的CSV文件
        for filename in os.listdir(preprocessed_data_dir):
            if filename.endswith("_preprocessed.csv"):
                file_path = os.path.join(preprocessed_data_dir, filename)
                
                # 从文件名中提取年度信息和期次信息
                parts = filename.split("-")
                year = parts[-2]  # 从倒数第二个部分获取年度信息
                period = parts[-3]  # 从倒数第三个部分获取期次信息
                
                # 读取CSV文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # 将每行数据添加年度字段和期次字段后添加到合并列表中
                    for row in reader:
                        row['year'] = year
                        row['period'] = period
                        merged_data.append(row)
        
        # 保存合并后的数据
        save_to_csv(merged_data, output_file)
        self.log.info(f'数据合并完成，已保存至 {output_file}')
        return True

    def run_all_preprocessing(self, force_run=False):
        """运行所有预处理任务
        
        参数:
            force_run: 是否强制运行，即使已经实例化过，默认为False
        """
        # 防止重复运行的标志
        if not hasattr(MusicRankPreprocessing, '_instance_flag') or force_run:
            # 标记已实例化
            MusicRankPreprocessing._instance_flag = True
            
            # 获取原始数据目录
            raw_data_dir = os.path.join(os.path.dirname(__file__).split("\\src")[0], "data", "raw")
    
            # 获取预处理后数据存储目录
            preprocessed_data_dir = os.path.join(os.path.dirname(__file__).split("\\src")[0], "data", "preprocessing")
    
            # 处理所有原始JSON文件
            for filename in os.listdir(raw_data_dir):
                if filename.endswith(".json"):
                    # 构建完整文件路径
                    raw_file_path = os.path.join(raw_data_dir, filename)
    
                    # 生成输出文件名
                    output_filename = filename.replace(".json", "_preprocessed.csv")
                    output_file_path = os.path.join(preprocessed_data_dir, output_filename)
    
                    # 运行预处理
                    self.run_preprocessing(raw_file_path, output_file_path)
    
            # 合并所有预处理文件
            merged_output_path = os.path.join(os.path.dirname(__file__).split("\\src")[0], "data", "preprocessed", "all_music_rank.csv")
            self.merge_preprocessed_data(merged_output_path)
            
        # 返回实例本身，以便链式调用
        return self
musicRankPreprocessing=MusicRankPreprocessing()