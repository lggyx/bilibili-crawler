import configparser
import os

def load_config(config_path=None):
    """
    读取config.ini配置文件，返回ConfigParser对象
    :param config_path: 配置文件路径，默认为当前目录下的config.ini
    :return: configparser.ConfigParser对象
    """
    config = configparser.ConfigParser()
    if config_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config.ini')
    config.read(config_path, encoding='utf-8')
    return config