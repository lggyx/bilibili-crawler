## 项目结构
```
.
├── doc/                    # 文档目录
├── src/                    # 源代码目录
│   ├── crawler/           # 数据采集模块
│   ├── preprocessor/      # 数据预处理模块
│   ├── storage/          # 数据存储模块
│   ├── analyzer/         # 数据分析模块
│   └── visualizer/       # 数据可视化模块
├── data/                   # 数据目录
│   ├── raw/              # 原始数据
│   ├── processed/        # 处理后的数据
│   └── output/           # 输出结果
├── tests/                  # 测试代码目录
│   ├── test_crawler/
│   ├── test_preprocessor/
│   ├── test_storage/
│   ├── test_analyzer/
│   └── test_visualizer/
├── notebooks/              # Jupyter notebooks目录
│   ├── data_exploration/
│   ├── analysis/
│   └── visualization/
├── config/                 # 配置文件目录
│   ├── crawler_config.yaml
│   ├── db_config.yaml
│   └── analysis_config.yaml
├── utils/                  # 工具函数目录
│   ├── logger.py
│   ├── database.py
│   └── helpers.py
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明文档
```