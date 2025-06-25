"""
数据存储模块
负责数据的持久化存储和检索
"""

import os
import json
import sqlite3
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import pickle

import sys
import os
# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.logger import get_logger
from utils.database import get_database, SQLiteDB
from utils.helpers import ensure_dir, save_json, load_json

logger = get_logger(__name__)


class BaseStorage:
    """存储基类"""
    
    def __init__(self, config_path: str = "../../config/db_config.yaml"):
        """
        初始化存储
        
        Args:
            config_path: 配置文件路径
        """
        self.db = get_database('sqlite')
        self.data_dir = "../../data/storage"
        ensure_dir(self.data_dir)
    
    def save(self, data: Any, key: str) -> bool:
        """
        保存数据
        
        Args:
            data: 要保存的数据
            key: 数据标识符
            
        Returns:
            bool: 是否保存成功
        """
        raise NotImplementedError("子类必须实现save方法")
    
    def load(self, key: str) -> Any:
        """
        加载数据
        
        Args:
            key: 数据标识符
            
        Returns:
            Any: 加载的数据
        """
        raise NotImplementedError("子类必须实现load方法")
    
    def delete(self, key: str) -> bool:
        """
        删除数据
        
        Args:
            key: 数据标识符
            
        Returns:
            bool: 是否删除成功
        """
        raise NotImplementedError("子类必须实现delete方法")
    
    def list_keys(self) -> List[str]:
        """
        列出所有数据标识符
        
        Returns:
            List[str]: 数据标识符列表
        """
        raise NotImplementedError("子类必须实现list_keys方法")


class FileStorage(BaseStorage):
    """文件存储类"""
    
    def __init__(self, data_dir: str = "../../data/storage/files"):
        """
        初始化文件存储
        
        Args:
            data_dir: 数据目录
        """
        super().__init__()
        self.data_dir = data_dir
        ensure_dir(self.data_dir)
        self.index_file = os.path.join(self.data_dir, "index.json")
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """
        加载索引文件
        
        Returns:
            Dict: 索引信息
        """
        if os.path.exists(self.index_file):
            try:
                return load_json(self.index_file)
            except Exception as e:
                logger.error(f"加载索引文件失败: {str(e)}")
        return {"files": {}}
    
    def _save_index(self) -> None:
        """保存索引文件"""
        try:
            save_json(self.index_file, self.index)
        except Exception as e:
            logger.error(f"保存索引文件失败: {str(e)}")
    
    def save(self, data: Any, key: str) -> bool:
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            key: 数据标识符
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 生成文件名
            file_name = f"{key}.json"
            file_path = os.path.join(self.data_dir, file_name)
            
            # 保存数据
            save_json(file_path, data)
            
            # 更新索引
            self.index["files"][key] = {
                "file_name": file_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._save_index()
            
            logger.info(f"数据已保存到文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存数据到文件失败: {str(e)}")
            return False
    
    def load(self, key: str) -> Any:
        """
        从文件加载数据
        
        Args:
            key: 数据标识符
            
        Returns:
            Any: 加载的数据，失败返回None
        """
        if key not in self.index["files"]:
            logger.warning(f"数据不存在: {key}")
            return None
        
        try:
            file_name = self.index["files"][key]["file_name"]
            file_path = os.path.join(self.data_dir, file_name)
            
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                return None
            
            return load_json(file_path)
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        删除数据文件
        
        Args:
            key: 数据标识符
            
        Returns:
            bool: 是否删除成功
        """
        if key not in self.index["files"]:
            logger.warning(f"数据不存在: {key}")
            return False
        
        try:
            file_name = self.index["files"][key]["file_name"]
            file_path = os.path.join(self.data_dir, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 更新索引
            del self.index["files"][key]
            self._save_index()
            
            logger.info(f"数据已删除: {key}")
            return True
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_keys(self) -> List[str]:
        """
        列出所有数据标识符
        
        Returns:
            List[str]: 数据标识符列表
        """
        return list(self.index["files"].keys())


class SQLiteStorage(BaseStorage):
    """SQLite数据库存储类"""
    
    def __init__(self, db_path: str = "../../data/storage/project_data.db"):
        """
        初始化SQLite存储
        
        Args:
            db_path: 数据库文件路径
        """
        super().__init__()
        self.db_path = db_path
        ensure_dir(os.path.dirname(db_path))
        self.db = SQLiteDB(db_path)
        self._init_tables()
    
    def _init_tables(self) -> None:
        """初始化数据库表"""
        try:
            # 创建数据表
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS data_store (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    metadata TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            logger.info("数据库表初始化完成")
        except Exception as e:
            logger.error(f"初始化数据库表失败: {str(e)}")
    
    def save(self, data: Any, key: str, metadata: Dict = None) -> bool:
        """
        保存数据到SQLite
        
        Args:
            data: 要保存的数据
            key: 数据标识符
            metadata: 元数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 序列化数据
            serialized_data = pickle.dumps(data)
            metadata_json = json.dumps(metadata or {})
            now = datetime.now().isoformat()
            
            # 检查是否已存在
            existing = self.db.query("SELECT key FROM data_store WHERE key = ?", (key,))
            
            if existing:
                # 更新
                self.db.execute(
                    "UPDATE data_store SET data = ?, metadata = ?, updated_at = ? WHERE key = ?",
                    (serialized_data, metadata_json, now, key)
                )
            else:
                # 插入
                self.db.execute(
                    "INSERT INTO data_store (key, data, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (key, serialized_data, metadata_json, now, now)
                )
            
            logger.info(f"数据已保存到SQLite: {key}")
            return True
        except Exception as e:
            logger.error(f"保存数据到SQLite失败: {str(e)}")
            return False
    
    def load(self, key: str) -> Tuple[Any, Dict]:
        """
        从SQLite加载数据
        
        Args:
            key: 数据标识符
            
        Returns:
            Tuple[Any, Dict]: (数据, 元数据)，失败返回(None, {})
        """
        try:
            result = self.db.query(
                "SELECT data, metadata FROM data_store WHERE key = ?",
                (key,)
            )
            
            if not result:
                logger.warning(f"数据不存在: {key}")
                return None, {}
            
            serialized_data, metadata_json = result[0]
            
            # 反序列化数据
            data = pickle.loads(serialized_data)
            metadata = json.loads(metadata_json)
            
            return data, metadata
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return None, {}
    
    def delete(self, key: str) -> bool:
        """
        删除SQLite中的数据
        
        Args:
            key: 数据标识符
            
        Returns:
            bool: 是否删除成功
        """
        try:
            self.db.execute("DELETE FROM data_store WHERE key = ?", (key,))
            logger.info(f"数据已删除: {key}")
            return True
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_keys(self) -> List[str]:
        """
        列出所有数据标识符
        
        Returns:
            List[str]: 数据标识符列表
        """
        try:
            results = self.db.query("SELECT key FROM data_store")
            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"列出数据标识符失败: {str(e)}")
            return []
    
    def search_by_metadata(self, query: Dict) -> List[str]:
        """
        根据元数据搜索数据
        
        Args:
            query: 查询条件
            
        Returns:
            List[str]: 匹配的数据标识符列表
        """
        try:
            results = self.db.query("SELECT key, metadata FROM data_store")
            matched_keys = []
            
            for key, metadata_json in results:
                metadata = json.loads(metadata_json)
                match = True
                
                for k, v in query.items():
                    if k not in metadata or metadata[k] != v:
                        match = False
                        break
                
                if match:
                    matched_keys.append(key)
            
            return matched_keys
        except Exception as e:
            logger.error(f"搜索数据失败: {str(e)}")
            return []


class DataManager:
    """数据管理器，提供统一的数据存储和检索接口"""
    
    def __init__(self):
        """初始化数据管理器"""
        self.file_storage = FileStorage()
        self.db_storage = SQLiteStorage()
    
    def save_raw_data(self, data: Any, source: str, timestamp: str = None) -> str:
        """
        保存原始数据
        
        Args:
            data: 原始数据
            source: 数据来源
            timestamp: 时间戳，默认为当前时间
            
        Returns:
            str: 数据标识符
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        key = f"raw_{source}_{timestamp}"
        metadata = {
            "type": "raw",
            "source": source,
            "timestamp": timestamp
        }
        
        success = self.db_storage.save(data, key, metadata)
        
        if success:
            return key
        return None
    
    def save_processed_data(self, data: Any, source: str, processor: str, timestamp: str = None) -> str:
        """
        保存处理后的数据
        
        Args:
            data: 处理后的数据
            source: 数据来源
            processor: 处理器名称
            timestamp: 时间戳，默认为当前时间
            
        Returns:
            str: 数据标识符
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        key = f"processed_{source}_{processor}_{timestamp}"
        metadata = {
            "type": "processed",
            "source": source,
            "processor": processor,
            "timestamp": timestamp
        }
        
        success = self.db_storage.save(data, key, metadata)
        
        if success:
            return key
        return None
    
    def save_analysis_result(self, data: Any, source: str, analysis_type: str, timestamp: str = None) -> str:
        """
        保存分析结果
        
        Args:
            data: 分析结果
            source: 数据来源
            analysis_type: 分析类型
            timestamp: 时间戳，默认为当前时间
            
        Returns:
            str: 数据标识符
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        key = f"analysis_{source}_{analysis_type}_{timestamp}"
        metadata = {
            "type": "analysis",
            "source": source,
            "analysis_type": analysis_type,
            "timestamp": timestamp
        }
        
        success = self.db_storage.save(data, key, metadata)
        
        if success:
            return key
        return None
    
    def load_data(self, key: str) -> Tuple[Any, Dict]:
        """
        加载数据
        
        Args:
            key: 数据标识符
            
        Returns:
            Tuple[Any, Dict]: (数据, 元数据)
        """
        return self.db_storage.load(key)
    
    def delete_data(self, key: str) -> bool:
        """
        删除数据
        
        Args:
            key: 数据标识符
            
        Returns:
            bool: 是否删除成功
        """
        return self.db_storage.delete(key)
    
    def list_all_data(self) -> List[str]:
        """
        列出所有数据
        
        Returns:
            List[str]: 数据标识符列表
        """
        return self.db_storage.list_keys()
    
    def search_data(self, data_type: str = None, source: str = None) -> List[str]:
        """
        搜索数据
        
        Args:
            data_type: 数据类型 (raw, processed, analysis)
            source: 数据来源
            
        Returns:
            List[str]: 匹配的数据标识符列表
        """
        query = {}
        if data_type:
            query["type"] = data_type
        if source:
            query["source"] = source
        
        return self.db_storage.search_by_metadata(query)
    
    def export_to_csv(self, data: pd.DataFrame, filename: str) -> str:
        """
        导出数据到CSV文件
        
        Args:
            data: 要导出的数据
            filename: 文件名
            
        Returns:
            str: 文件路径
        """
        export_dir = "../../data/output"
        ensure_dir(export_dir)
        
        file_path = os.path.join(export_dir, filename)
        data.to_csv(file_path, index=False, encoding='utf-8')
        
        logger.info(f"数据已导出到CSV: {file_path}")
        return file_path


# 示例用法
if __name__ == "__main__":
    # 测试文件存储
    file_storage = FileStorage()
    test_data = {"name": "测试数据", "value": 123}
    
    # 保存数据
    file_storage.save(test_data, "test_key")
    
    # 加载数据
    loaded_data = file_storage.load("test_key")
    print("从文件加载的数据:", loaded_data)
    
    # 测试SQLite存储
    db_storage = SQLiteStorage()
    
    # 保存数据
    db_storage.save(test_data, "test_db_key", {"source": "test"})
    
    # 加载数据
    loaded_db_data, metadata = db_storage.load("test_db_key")
    print("从SQLite加载的数据:", loaded_db_data)
    print("元数据:", metadata)
    
    # 测试数据管理器
    data_manager = DataManager()
    
    # 保存原始数据
    raw_key = data_manager.save_raw_data({"raw": "data"}, "test_source")
    print("原始数据键:", raw_key)
    
    # 保存处理后的数据
    processed_key = data_manager.save_processed_data({"processed": "data"}, "test_source", "test_processor")
    print("处理后数据键:", processed_key)
    
    # 列出所有数据
    all_keys = data_manager.list_all_data()
    print("所有数据键:", all_keys)