# B站数据采集与分析系统

这是一个用于采集和分析B站数据的综合系统，包括音频榜单、视频信息和视频排行等数据的爬取、清洗和分析功能。

## 项目结构

```
bilibili-crawler/
├── analyzer/            # 数据分析模块
│   └── audio/          # 音频数据分析
├── cleaner/            # 数据清洗模块
│   └── audio/          # 音频数据清洗
├── config/             # 配置模块
├── crawler/            # 爬虫模块
│   ├── audio/         # 音频数据爬虫
│   ├── video/         # 视频数据爬虫
│   └── video_ranking/ # 视频排行爬虫
├── data/               # 数据存储
│   ├── cookies/       # Cookie配置
│   ├── logs/          # 日志文件
│   ├── processed/     # 处理后的数据
│   ├── raw/          # 原始数据
│   └── reports/      # 分析报告
├── doc/                # 项目文档
├── tests/              # 测试模块
├── utils/              # 工具模块
├── main.py            # 主程序入口
└── requirements.txt    # 项目依赖
```

## 功能特点

### 1. 数据采集
- 音频榜单数据爬取
  - 获取音频榜单每期列表
  - 查询音频榜单单期信息
  - 获取音频榜单单期内容
- 视频信息采集
- 视频分区数据爬取
- 动态排行榜采集

### 2. 数据清洗
- 数据字段标准化
  - 保留关键字段：音乐ID、标题、歌手、专辑、热度、排名等
  - 视频相关信息：AID、BVID、封面、标题、创作者、时长、播放量
- 数据格式统一化
- 冗余数据过滤
- 异常值处理

### 3. 数据分析
- 音频榜单分析
  - 热度趋势分析
  - 歌手分布分析
  - 创作者表现分析
  - 特征相关性分析
  - 歌曲类型分析
- 可视化报告生成

## 环境要求

- chromedriver
  - [Chrome for Testing availability](https://googlechromelabs.github.io/chrome-for-testing/#beta)
  - 打开网址下载对应Chrome和ChromeDriver，添加到系统环境变量PATH里面

- Python >= 3.7
- 依赖包：
  - pandas >= 1.3.0
  - numpy >= 1.20.0
  - matplotlib >= 3.4.0
  - seaborn >= 0.11.0
  - argparse >= 1.4.0
  - python-dateutil >= 2.8.2
  - pathlib >= 1.0.1
  - json5 >= 0.9.6

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd bilibili-crawler
```

2. 创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 命令行帮助：
```bash
python main.py --help
```
> 运行前确存在cookie，如果不存在可以运行`python main.py --mode login`进行登录
## API说明

### 音频榜单API

1. 获取音频榜单每期列表
```python
get_audio_rank_all_period(list_type, csrf)
```
- `list_type`: 榜单类型（1：热榜，2：原创榜）
- `csrf`: CSRF Token（可选）

2. 查询音频榜单单期信息
```python
get_audio_rank_detail(list_id, csrf)
```
- `list_id`: 榜单ID
- `csrf`: CSRF Token（可选）

3. 获取音频榜单单期内容
```python
get_audio_rank_music_list(list_id, csrf)
```
- `list_id`: 榜单ID
- `csrf`: CSRF Token（可选）

## 数据处理流程

### 1. 数据采集
```python
rank_crawler()
```
- 获取音乐热榜所有期数
- 遍历每期榜单获取详细信息
- 数据保存至raw目录

### 2. 数据清洗
```python
rank_cleaner()
```
保留字段：
- music_id：音乐ID
- music_title：音乐标题
- singer：歌手
- album：专辑
- heat：热度
- rank：排名
- creation_aid：视频AID
- creation_bvid：视频BVID
- creation_cover：视频封面
- creation_title：视频标题
- creation_nickname：创作者昵称
- creation_duration：视频时长
- creation_play：播放量

### 3. 数据分析
运行音频榜单分析：
```bash
python main.py --mode music_rank
```

参数说明：
- `--data_dir`：处理后的数据目录路径（默认：./data/processed）
- `--output_dir`：分析报告输出目录路径（默认：./data/reports）

## 数据格式说明

### 原始数据格式
```json
{
    "data": {
        "list": [
            {
                "music_id": "123456",
                "music_title": "歌曲标题",
                "singer": "歌手名",
                "album": "专辑名",
                "creation_title": "视频标题",
                "creation_nickname": "创作者昵称",
                "creation_play": 10000,
                "heat": 5000,
                "rank": 1,
                "creation_aid": "xxx",
                "creation_bvid": "BVxxx",
                "creation_cover": "http://xxx",
                "creation_duration": 180
            }
        ]
    }
}
```

### 清洗后数据格式
与原始数据格式相同，但只保留指定的关键字段。

## 项目模块说明

### 1. analyzer（分析模块）
- audio_rank_analyzer.py：音频榜单数据分析实现
- run_audio_analysis.py：音频分析运行脚本

### 2. cleaner（清洗模块）
- rank_cleaner.py：榜单数据清洗处理
  - 字段过滤
  - 数据格式化
  - 异常处理

### 3. crawler（爬虫模块）
- audio/rank_crawler.py：音频榜单爬虫
  - 获取榜单期数
  - 获取榜单详情
  - 数据存储
- video/info_crawler.py：视频信息爬虫
- video/video_zone_crawler.py：视频分区爬虫
- video_ranking/dynamic_crawler.py：动态排行爬虫

### 4. utils（工具模块）
- cookie_utils.py：Cookie处理工具
- request_utils.py：网络请求工具
- storage_utils.py：数据存储工具
- time_utils.py：时间处理工具

## 注意事项

1. 运行爬虫前请确保：
   - 已配置正确的Cookie信息
   - 网络连接正常
   - 遵守B站的爬虫规则和速率限制
   - 每次请求间隔建议3秒以上

2. 数据分析注意：
   - 确保输入数据格式正确
   - 数据量较大时可能需要较长处理时间
   - 图表生成需要中文字体支持

## 日志说明

系统日志存储在 `data/logs` 目录下，格式为：
```
bilibili-crawler-YYYY-MM-DD_HH.log
```

## 问题反馈

如遇到问题或有改进建议，请提交Issue或Pull Request。

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。