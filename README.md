# Bilibili 音乐榜单数据采集与分析项目

## 项目简介
本项目实现了对 Bilibili 音乐榜单数据的全流程采集、预处理、特征选择、建模分析、可视化和自动化报告生成。支持命令行和 Jupyter Notebook 两种分析体验，所有可视化图片均自动嵌入报告，适配中文环境。

## 主要功能
- 自动登录 Bilibili 并采集音乐榜单数据
- 数据预处理与清洗
- 特征选择（卡方检验等）
- KMeans 聚类分析
- 多种业务相关可视化（TOP榜、热力图、词云等）
- 自动生成结构化分析报告（Jupyter Notebook，图片自动嵌入）
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
│   ├── analyzer/                  # 分析与可视化模块
│   ├── crawler/                   # 爬虫与登录模块
│   ├── preprocessing/             # 数据预处理模块
│   └── utils/                     # 工具函数
└── logs/                          # 日志文件
```

## 环境依赖
- Python 3.8+
- 主要依赖包：pandas, numpy, matplotlib, seaborn, wordcloud, scikit-learn, jupyter, nbconvert
- 安装依赖：
  ```bash
  pip install -r requirements.txt
  ```

## 使用方法
1. **命令行一键全流程**
   ```bash
   python main.py --login --crawl --preprocess --analyze
   ```
   ```bash
   python main.py --crawl --preprocess --analyze
   ```
   - 支持单步运行：`--login`、`--crawl`、`--preprocess`、`--analyze` 可任意组合
   - analyze 阶段自动生成并打开 Jupyter 分析报告，且自动运行全部代码块

2. **分析报告说明**
   - 报告路径：`src/analyzer/analysis_report.ipynb`
   - 所有图片均自动嵌入，支持任意环境下查看
   - 图表配有详细业务解读

3. **可视化图片与中间数据**
   - 生成于 `data/reporter/` 目录
   - 预处理数据在 `data/preprocessed/`

## 注意事项
- 首次运行建议先安装依赖并检查 Python 版本
- 若需自定义分析或可视化，可直接修改 `src/analyzer/analysis_report.ipynb` 或相关 Python 脚本
- 日志文件位于 `logs/`，便于排查问题

