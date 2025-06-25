"""
辅助工具模块
提供各种通用的辅助函数，如文件操作、日期处理、字符串处理等
"""

import os
import re
import json
import yaml
import hashlib
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

from .logger import get_logger

logger = get_logger(__name__)


# 文件操作相关函数
def ensure_dir(directory: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        str: 目录路径
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        recursive: 是否递归查找子目录
        
    Returns:
        List[str]: 文件路径列表
    """
    path = Path(directory)
    if recursive:
        return [str(p) for p in path.rglob(pattern) if p.is_file()]
    else:
        return [str(p) for p in path.glob(pattern) if p.is_file()]


def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    """
    读取文本文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
        
    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        raise


def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    写入文本文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        logger.error(f"写入文件失败: {str(e)}")
        raise


def load_json(file_path: str, encoding: str = 'utf-8') -> Dict:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
        
    Returns:
        Dict: JSON数据
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败: {str(e)}")
        raise


def save_json(file_path: str, data: Dict, encoding: str = 'utf-8', indent: int = 2) -> None:
    """
    保存数据为JSON文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
        encoding: 文件编码
        indent: 缩进空格数
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    except Exception as e:
        logger.error(f"保存JSON文件失败: {str(e)}")
        raise


def load_yaml(file_path: str, encoding: str = 'utf-8') -> Dict:
    """
    加载YAML文件
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
        
    Returns:
        Dict: YAML数据
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载YAML文件失败: {str(e)}")
        raise


def save_yaml(file_path: str, data: Dict, encoding: str = 'utf-8') -> None:
    """
    保存数据为YAML文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
        encoding: 文件编码
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        logger.error(f"保存YAML文件失败: {str(e)}")
        raise


# 日期时间处理函数
def get_current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前时间的格式化字符串
    
    Args:
        format_str: 日期时间格式
        
    Returns:
        str: 格式化的日期时间字符串
    """
    return datetime.now().strftime(format_str)


def get_date_range(start_date: str, end_date: str, date_format: str = "%Y-%m-%d") -> List[str]:
    """
    获取日期范围内的所有日期
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        date_format: 日期格式
        
    Returns:
        List[str]: 日期字符串列表
    """
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    
    date_list = []
    current = start
    
    while current <= end:
        date_list.append(current.strftime(date_format))
        current += timedelta(days=1)
    
    return date_list


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """
    尝试解析多种格式的日期字符串
    
    Args:
        date_str: 日期字符串
        formats: 日期格式列表，默认尝试常见格式
        
    Returns:
        Optional[datetime]: 解析后的日期时间对象，解析失败返回None
    """
    if formats is None:
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
            "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
            "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"无法解析日期字符串: {date_str}")
    return None


# 字符串处理函数
def generate_random_string(length: int = 8) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        str: 随机字符串
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def calculate_md5(text: str) -> str:
    """
    计算字符串的MD5哈希值
    
    Args:
        text: 输入字符串
        
    Returns:
        str: MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def extract_urls(text: str) -> List[str]:
    """
    从文本中提取URL
    
    Args:
        text: 输入文本
        
    Returns:
        List[str]: URL列表
    """
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+\.[^\s<>"\']+'
    return re.findall(url_pattern, text)


def clean_html(html: str) -> str:
    """
    清除HTML标签
    
    Args:
        html: HTML文本
        
    Returns:
        str: 清除标签后的文本
    """
    # 简单的HTML标签清除，复杂情况可以使用BeautifulSoup
    clean_pattern = re.compile('<.*?>')
    return re.sub(clean_pattern, '', html)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后添加的后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# 其他实用函数
def retry(func, max_attempts: int = 3, delay: int = 1, backoff: int = 2, exceptions: tuple = (Exception,)):
    """
    函数重试装饰器
    
    Args:
        func: 要重试的函数
        max_attempts: 最大尝试次数
        delay: 初始延迟秒数
        backoff: 延迟增长因子
        exceptions: 捕获的异常类型
        
    Returns:
        函数执行结果
    """
    import time
    
    def wrapper(*args, **kwargs):
        attempts = 0
        current_delay = delay
        
        while attempts < max_attempts:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                attempts += 1
                if attempts == max_attempts:
                    logger.error(f"函数 {func.__name__} 达到最大重试次数 {max_attempts}，最后一次错误: {str(e)}")
                    raise
                
                logger.warning(f"函数 {func.__name__} 执行失败 (尝试 {attempts}/{max_attempts})，错误: {str(e)}，{current_delay}秒后重试")
                time.sleep(current_delay)
                current_delay *= backoff
    
    return wrapper


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    将列表分割成固定大小的块
    
    Args:
        lst: 输入列表
        chunk_size: 块大小
        
    Returns:
        List[List]: 分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List) -> List:
    """
    扁平化嵌套列表
    
    Args:
        nested_list: 嵌套列表
        
    Returns:
        List: 扁平化后的列表
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


if __name__ == "__main__":
    # 测试辅助函数
    print("当前时间:", get_current_time())
    print("随机字符串:", generate_random_string(10))
    print("MD5哈希值:", calculate_md5("测试文本"))
    
    # 测试URL提取
    test_text = "请访问 https://example.com 或 www.example.org 获取更多信息"
    print("提取的URL:", extract_urls(test_text))
    
    # 测试HTML清理
    test_html = "<p>这是<b>一段</b>HTML<a href='#'>文本</a></p>"
    print("清理后的HTML:", clean_html(test_html))