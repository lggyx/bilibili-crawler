import logging
import os.path

from rich.logging import RichHandler
from datetime import datetime

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
path = os.path.dirname(__file__).split("\\src")[0] + "\\logs\\"

# 新增：确保日志目录存在
os.makedirs(path, exist_ok=True)

LOG_FILE = path + f"bilibili-crawler-{datetime.now().strftime('%Y-%m-%d_%H')}.log"  # 日志文件按小时保存

# 创建文件处理器
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
# 创建RichHandler处理器
rich_handler = RichHandler(rich_tracebacks=True, markup=True)

logging.basicConfig(
    level="INFO",
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[rich_handler, file_handler]
)

def get_log(name):
    return logging.getLogger(name)