# Bilibili 音乐榜单与视频弹幕数据采集与分析项目

## 项目简介
本项目实现了对 Bilibili 音乐榜单与视频弹幕数据的全流程采集、预处理、特征工程、建模分析、可视化和自动化报告生成。支持命令行和 Jupyter Notebook 两种分析体验，所有可视化图片均自动嵌入报告，适配中文环境。

## 主要功能
- 自动登录 Bilibili 并采集音乐榜单与视频弹幕数据（支持BVID/AID）
- 数据预处理与清洗，弹幕自动查找最新数据
- 特征选择（卡方检验等）、高级特征工程（弹幕长度、情感极性等）
- KMeans 聚类分析、情感分析（SnowNLP）
- 多种业务相关可视化（TOP榜、热力图、词云、弹幕分布、用户活跃度等）
- 自动生成结构化分析报告（Jupyter Notebook，图片自动嵌入，分节清晰，含业务解读）
- 一键全流程命令行运行，分析报告自动打开并自动运行全部代码块

## 目录结构
```
├── main.py                        # 主程序入口，命令行参数控制全流程
├── README.md                      # 项目说明文档
├── data/
│   ├── preprocessed/              # 预处理后数据
│   ├── preprocessing/             # 原始及中间数据
│   ├── reporter/                  # 可视化图片与分析报告输出
│   └── raw/                       # 原始爬取数据
├── src/
│   ├── analyzer/                  # 分析与可视化模块（含 music_rank、video_danmaku 分析与报告）
│   ├── crawler/                   # 爬虫与登录模块
│   ├── preprocessing/             # 数据预处理模块
│   └── utils/                     # 工具函数
└── logs/                          # 日志文件
```

## 环境依赖
- Python 3.8+
- 主要依赖包：pandas, numpy, matplotlib, seaborn, wordcloud, scikit-learn, jupyter, nbconvert, snownlp
- 安装依赖：
  ```bash
  pip install -r requirements.txt
  ```
- EdgeDriver 下载放到driver文件夹中：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
## 使用方法

### 1. 命令行一键全流程
- 音乐榜单分析：
  ```bash
  python main.py --type music_rank --crawl --preprocess --analyze
  ```
- 视频弹幕分析（需指定视频id，支持BVID或AID）：
  ```bash
  python main.py --type video_danmaku --id BVxxxxxxxxx --crawl --preprocess --analyze
  ```
  或
  ```bash
  python main.py --type video_danmaku --id 123456789 --crawl --preprocess --analyze
  ```
- 支持单步运行：`--login`、`--crawl`、`--preprocess`、`--analyze` 可任意组合
- analyze 阶段自动生成并打开对应 Jupyter 分析报告，并自动运行全部代码块

### 2. 参数说明
- `--type`：指定分析类型，必选，支持 `music_rank`（音乐榜单）、`video_danmaku`（视频弹幕）、`login`（登录）
- `--id`：视频弹幕分析时需指定视频id（BVID或AID），音乐榜单无需此参数
- `--crawl`：执行数据采集
- `--preprocess`：执行数据预处理
- `--analyze`：执行分析并生成可视化报告
- `--login`：执行B站登录（仅`--type login`时有效）

### 3. 分析报告自动生成与查看
- analyze 阶段会自动生成并打开对应的 Jupyter Notebook 分析报告（music_rank 或 video_danmaku），并自动运行全部代码块，所有图片自动嵌入。
- 报告路径：
  - 音乐榜单：`src/analyzer/music_rank_analysis_report.ipynb`
  - 视频弹幕：`src/analyzer/video_danmaku_analysis_report.ipynb`

### 4. 典型用法示例
- 只采集和分析音乐榜单：
  ```bash
  python main.py --type music_rank --crawl --preprocess --analyze
  ```
- 只分析最新弹幕（假设已采集和预处理）：
  ```bash
  python main.py --type video_danmaku --id BVxxxxxxxxx --analyze
  ```
- 只登录：
  ```bash
  python main.py --type login
  ```

## 注意事项
- 首次运行建议先安装依赖并检查 Python 版本
- 若需自定义分析或可视化，可直接修改 `src/analyzer/music_rank_analysis_report.ipynb`、`src/analyzer/video_danmaku_analysis_report.ipynb` 或相关 Python 脚本
- 日志文件位于 `logs/`，便于排查问题
- 若 Notebook 图表中文乱码，请确保本地已安装 SimHei 或 Microsoft YaHei 字体，并在分析报告开头设置：
  ```python
  import matplotlib
  matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
  matplotlib.rcParams['axes.unicode_minus'] = False
  ```
- analyze 阶段自动运行 Notebook 全部代码块，支持一键生成完整分析报告

