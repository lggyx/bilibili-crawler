"""
数据库工具模块
提供统一的数据库操作接口，支持SQLite、MySQL和MongoDB
"""

import os
from typing import Any, Dict, List, Optional, Union
import yaml
from pathlib import Path

import sqlite3
from contextlib import contextmanager

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from .logger import get_logger

logger = get_logger(__name__)


class DatabaseConfig:
    """数据库配置加载类"""
    
    @staticmethod
    def load_config(config_path: str = "../config/db_config.yaml") -> Dict:
        """
        加载数据库配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 配置信息字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载数据库配置文件失败: {str(e)}")
            return {}


class SQLiteDB:
    """SQLite数据库操作类"""
    
    def __init__(self, db_path: str):
        """
        初始化SQLite数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """创建数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """
        执行SQL语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                conn.commit()
            except Exception as e:
                logger.error(f"执行SQL语句失败: {str(e)}")
                conn.rollback()
                raise
    
    def query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[tuple]: 查询结果列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                return cursor.fetchall()
            except Exception as e:
                logger.error(f"执行查询失败: {str(e)}")
                raise


class MySQLDB:
    """MySQL数据库操作类"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """
        初始化MySQL数据库连接
        
        Args:
            host: 数据库主机地址
            port: 端口号
            user: 用户名
            password: 密码
            database: 数据库名
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("请安装pymysql包以使用MySQL功能")
        
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
    
    @contextmanager
    def get_connection(self):
        """创建数据库连接的上下文管理器"""
        conn = pymysql.connect(**self.config)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> None:
        """
        执行SQL语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    conn.commit()
                except Exception as e:
                    logger.error(f"执行SQL语句失败: {str(e)}")
                    conn.rollback()
                    raise
    
    def query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[tuple]: 查询结果列表
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    return cursor.fetchall()
                except Exception as e:
                    logger.error(f"执行查询失败: {str(e)}")
                    raise


class MongoDB:
    """MongoDB数据库操作类"""
    
    def __init__(self, host: str, port: int, database: str, username: str = None, password: str = None):
        """
        初始化MongoDB连接
        
        Args:
            host: 数据库主机地址
            port: 端口号
            database: 数据库名
            username: 用户名（可选）
            password: 密码（可选）
        """
        if not MONGODB_AVAILABLE:
            raise ImportError("请安装pymongo包以使用MongoDB功能")
        
        self.client = None
        self.db = None
        self.config = {
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password
        }
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            if self.config['username'] and self.config['password']:
                self.client = pymongo.MongoClient(
                    host=self.config['host'],
                    port=self.config['port'],
                    username=self.config['username'],
                    password=self.config['password']
                )
            else:
                self.client = pymongo.MongoClient(
                    host=self.config['host'],
                    port=self.config['port']
                )
            self.db = self.client[self.config['database']]
        except Exception as e:
            logger.error(f"MongoDB连接失败: {str(e)}")
            raise
    
    def insert_one(self, collection: str, document: Dict) -> str:
        """
        插入单个文档
        
        Args:
            collection: 集合名称
            document: 要插入的文档
            
        Returns:
            str: 插入文档的ID
        """
        try:
            result = self.db[collection].insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"插入文档失败: {str(e)}")
            raise
    
    def find(self, collection: str, query: Dict = None) -> List[Dict]:
        """
        查询文档
        
        Args:
            collection: 集合名称
            query: 查询条件
            
        Returns:
            List[Dict]: 查询结果列表
        """
        try:
            return list(self.db[collection].find(query or {}))
        except Exception as e:
            logger.error(f"查询文档失败: {str(e)}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()


def get_database(db_type: str = 'sqlite') -> Union[SQLiteDB, MySQLDB, MongoDB]:
    """
    获取数据库实例的工厂函数
    
    Args:
        db_type: 数据库类型 ('sqlite', 'mysql', 'mongodb')
        
    Returns:
        Union[SQLiteDB, MySQLDB, MongoDB]: 数据库实例
    """
    config = DatabaseConfig.load_config()
    
    if db_type == 'sqlite':
        db_path = config.get('sqlite', {}).get('db_path', '../data/storage/project_data.db')
        return SQLiteDB(db_path)
    
    elif db_type == 'mysql':
        if not config.get('mysql', {}).get('enabled', False):
            raise ValueError("MySQL未启用，请检查配置文件")
        mysql_config = config['mysql']
        return MySQLDB(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database']
        )
    
    elif db_type == 'mongodb':
        if not config.get('mongodb', {}).get('enabled', False):
            raise ValueError("MongoDB未启用，请检查配置文件")
        mongodb_config = config['mongodb']
        return MongoDB(
            host=mongodb_config['host'],
            port=mongodb_config['port'],
            database=mongodb_config['database'],
            username=mongodb_config.get('username'),
            password=mongodb_config.get('password')
        )
    
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")


if __name__ == "__main__":
    # 测试SQLite数据库
    try:
        db = get_database('sqlite')
        db.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        db.execute("INSERT INTO test (name, value) VALUES (?, ?)", ("test1", 100))
        results = db.query("SELECT * FROM test")
        print("SQLite测试结果:", results)
    except Exception as e:
        print(f"SQLite测试失败: {str(e)}")