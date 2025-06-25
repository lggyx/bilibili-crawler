"""
日志工具模块
提供项目中统一的日志记录功能
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """
    日志记录器类
    提供统一的日志记录接口，支持控制台和文件输出
    """
    
    def __init__(self, name="project_logger", log_level=logging.INFO, log_to_file=True, log_dir="../logs"):
        """
        初始化日志记录器
        
        Args:
            name (str): 日志记录器名称
            log_level (int): 日志级别，默认为INFO
            log_to_file (bool): 是否将日志写入文件
            log_dir (str): 日志文件目录
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 添加文件处理器（如果需要）
        if log_to_file:
            # 确保日志目录存在
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            
            # 创建日志文件名，包含日期
            log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            
            # 添加文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def get_logger(self):
        """获取日志记录器实例"""
        return self.logger


# 创建默认日志记录器实例
default_logger = Logger().get_logger()


def get_logger(name=None, log_level=None, log_to_file=True, log_dir="../logs"):
    """
    获取日志记录器的便捷函数
    
    Args:
        name (str, optional): 日志记录器名称，默认使用调用模块的名称
        log_level (int, optional): 日志级别，默认为INFO
        log_to_file (bool): 是否将日志写入文件
        log_dir (str): 日志文件目录
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    if name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = module.__name__ if module else "unnamed_module"
    
    if log_level is None:
        # 从环境变量获取日志级别，默认为INFO
        log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
    
    return Logger(name, log_level, log_to_file, log_dir).get_logger()


if __name__ == "__main__":
    # 测试日志记录器
    logger = get_logger("test_logger")
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")