# B站音频榜单爬虫

这是一个用于爬取B站音频榜单数据并进行分析的Python项目。

## 功能特点

- 爬取B站音频榜单数据
- 数据清洗和预处理
- 数据分析和可视化
- 生成分析报告

## 项目结构

```
bilibili-crawler/
├── data/               # 数据目录
│   ├── raw/            # 原始数据
│   └── processed/      # 处理后的数据
├── logs/               # 日志目录
├── src/                # 源代码
│   ├── analysis/       # 数据分析模块
│   ├── config/         # 配置模块
│   ├── crawler/        # 爬虫模块
│   ├── preprocessing/  # 数据预处理模块
│   └── utils/          # 工具模块
├── main.py             # 主程序入口
└── README.md           # 项目说明
```

## 安装依赖

```bash
pip install requests pandas numpy matplotlib seaborn
```

## 使用方法

### 1. 配置

修改 `src/config/config.ini` 文件，根据需要调整配置参数。

### 2. 登录

由于B站API需要登录状态，您需要先在浏览器中登录B站，然后将Cookie保存到 `data/raw/cookies.json` 文件中。

您可以使用以下方法获取Cookie：

1. 在浏览器中登录B站
2. 打开开发者工具（F12）
3. 切换到Network标签页
4. 刷新页面
5. 选择任意一个请求，查看Headers中的Cookie
6. 将Cookie复制到 `data/raw/cookies.json` 文件中，格式如下：

```json
{
  "SESSDATA": "your-sessdata",
  "bili_jct": "your-bili-jct",
  "DedeUserID": "your-userid",
  "DedeUserID__ckMd5": "your-userid-ckmd5",
  "sid": "your-sid"
}
```

### 3. 运行

```bash
python main.py
```

程序将依次执行以下步骤：
1. 爬取B站音频榜单数据
2. 清洗和预处理数据
3. 分析数据并生成可视化图表
4. 生成分析报告

### 4. 查看结果

- 原始数据保存在 `data/raw/` 目录下
- 处理后的数据保存在 `data/processed/` 目录下
- 分析报告保存在 `data/processed/analysis_report.md` 文件中
- 可视化图表保存在 `data/processed/` 目录下

## 模块说明

### 爬虫模块

- `bilibili_login.py`: 处理B站登录认证
- `audio_rank_crawler.py`: 爬取B站音频榜单数据

### 数据预处理模块

- `data_cleaner.py`: 清洗和预处理爬取的数据

### 数据分析模块

- `data_analyzer.py`: 分析数据并生成可视化图表

### 工具模块

- `logger.py`: 日志记录工具

### 配置模块

- `config.py`: 配置管理
- `config.ini`: 配置文件

## 注意事项

- 请遵守B站的使用条款和API使用规范
- 请合理控制爬取频率，避免对B站服务器造成压力
- 本项目仅用于学习和研究，请勿用于商业用途

## 许可证

MIT License