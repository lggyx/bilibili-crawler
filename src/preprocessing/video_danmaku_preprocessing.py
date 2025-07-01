import os
import re
import csv
from bs4 import BeautifulSoup
from src.utils.logger import get_log

def preprocess_latest_danmaku():
    log = get_log("video_danmaku_preprocessing")
    raw_data_dir = os.path.dirname(__file__).split("\\src")[0] + "\\data\\raw"
    pre_dir = os.path.dirname(__file__).split("\\src")[0] + "\\data\\preprocessed"
    os.makedirs(pre_dir, exist_ok=True)
    pattern = re.compile(r"^视频弹幕数据-.*\.(html|xml)$")
    matched_files = [f for f in os.listdir(raw_data_dir) if pattern.match(f)]
    if not matched_files:
        log.error("未找到弹幕原始数据文件")
        return
    latest_file = max(matched_files, key=lambda f: os.path.getmtime(os.path.join(raw_data_dir, f)))
    file_path = os.path.join(raw_data_dir, latest_file)
    log.info(f"处理文件: {latest_file}")
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html')
        danmakus = soup.find_all('d')
        if not danmakus:
            log.warning("未解析到任何弹幕")
        csv_name = latest_file.replace('.html', '_preprocessed.csv').replace('.xml', '_preprocessed.csv')
        csv_path = os.path.join(pre_dir, csv_name)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['time', 'type', 'font_size', 'color', 'timestamp', 'pool', 'user_hash', 'row_id', 'content'])
            for d in danmakus:
                p = d.get('p', '')
                fields = p.split(',')
                if len(fields) >= 8:
                    writer.writerow(fields[:8] + [d.text])
        log.info(f"弹幕预处理完成，结果已保存到 {csv_path}")
class VideoDanmakuPreprocessing:
    def __init__(self):
        self.log = get_log("VideoDanmakuPreprocessing")

    def run_preprocessing(self):
        """运行视频弹幕预处理"""
        preprocess_latest_danmaku()
videoDanmakuPreprocessing= VideoDanmakuPreprocessing()
