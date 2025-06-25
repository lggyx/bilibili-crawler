"""
爬虫模块
负责从目标网站抓取数据
"""

import time
import random
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin
import yaml

from bs4 import BeautifulSoup
from requests.exceptions import RequestException

import sys
import os
# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.logger import get_logger
from utils.helpers import ensure_dir, save_json, load_yaml

logger = get_logger(__name__)


class BaseCrawler:
    """爬虫基类，提供基本的爬取功能"""
    
    def __init__(self, config_path: str = "../../config/crawler_config.yaml"):
        """
        初始化爬虫
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 设置代理
        if self.config.get("proxies", {}).get("use_proxy", False):
            self.proxies = self.config["proxies"]["proxy_list"]
        else:
            self.proxies = []
        
        # 创建存储目录
        self.storage_path = self.config.get("storage", {}).get("path", "../../data/raw/")
        ensure_dir(self.storage_path)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 配置信息
        """
        try:
            return load_yaml(config_path)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return {}
    
    def _get_random_proxy(self) -> Optional[Dict]:
        """
        随机获取一个代理
        
        Returns:
            Optional[Dict]: 代理配置，如果没有代理则返回None
        """
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def _get_headers(self, url: str) -> Dict:
        """
        获取请求头
        
        Args:
            url: 请求URL
            
        Returns:
            Dict: 请求头
        """
        # 可以根据不同的网站定制请求头
        headers = self.headers.copy()
        headers["Referer"] = url
        return headers
    
    def get(self, url: str, params: Dict = None, retry: int = 3) -> Optional[requests.Response]:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: 请求参数
            retry: 重试次数
            
        Returns:
            Optional[requests.Response]: 响应对象，失败返回None
        """
        for i in range(retry + 1):
            try:
                # 随机延迟，避免请求过于频繁
                delay = self.config.get("crawler", {}).get("delay", 1)
                time.sleep(delay * (1 + random.random()))
                
                # 设置代理
                proxy = self._get_random_proxy()
                proxies = proxy if proxy else None
                
                # 发送请求
                response = self.session.get(
                    url,
                    params=params,
                    headers=self._get_headers(url),
                    proxies=proxies,
                    timeout=self.config.get("crawler", {}).get("timeout", 30)
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"请求失败，状态码: {response.status_code}，URL: {url}")
            
            except RequestException as e:
                logger.error(f"请求异常: {str(e)}，URL: {url}")
                if i < retry:
                    logger.info(f"重试 ({i+1}/{retry})...")
                    time.sleep((i + 1) * 2)  # 指数退避
        
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        解析HTML
        
        Args:
            html: HTML内容
            
        Returns:
            BeautifulSoup: 解析后的对象
        """
        return BeautifulSoup(html, "html.parser")
    
    def save_data(self, data: Any, filename: str) -> str:
        """
        保存数据
        
        Args:
            data: 要保存的数据
            filename: 文件名
            
        Returns:
            str: 保存的文件路径
        """
        file_path = os.path.join(self.storage_path, filename)
        save_json(file_path, data)
        logger.info(f"数据已保存到: {file_path}")
        return file_path
    
    def crawl(self, url: str) -> Dict:
        """
        爬取URL
        
        Args:
            url: 目标URL
            
        Returns:
            Dict: 爬取的数据
        """
        logger.info(f"开始爬取: {url}")
        response = self.get(url)
        
        if not response:
            logger.error(f"爬取失败: {url}")
            return {}
        
        # 默认实现只返回响应内容，子类应该重写此方法以提取有用数据
        return {
            "url": url,
            "status": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "timestamp": time.time(),
            "html": response.text
        }


class WebsiteCrawler(BaseCrawler):
    """特定网站的爬虫实现"""
    
    def __init__(self, site_name: str, config_path: str = "../../config/crawler_config.yaml"):
        """
        初始化网站爬虫
        
        Args:
            site_name: 网站名称，应与配置文件中的名称匹配
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        
        # 获取特定网站的配置
        site_configs = self.config.get("target_sites", [])
        self.site_config = next((site for site in site_configs if site["name"] == site_name), None)
        
        if not self.site_config:
            logger.error(f"未找到网站配置: {site_name}")
            raise ValueError(f"未找到网站配置: {site_name}")
        
        # 设置网站特定的请求头
        if "headers" in self.site_config:
            self.headers.update(self.site_config["headers"])
        
        self.base_url = self.site_config["url"]
        self.visited_urls = set()
        self.max_depth = self.config.get("crawler", {}).get("max_depth", 3)
        self.max_pages = self.config.get("crawler", {}).get("max_pages", 100)
    
    def crawl_site(self, start_url: str = None, max_depth: int = None, max_pages: int = None) -> List[Dict]:
        """
        爬取整个网站
        
        Args:
            start_url: 起始URL，默认使用配置中的URL
            max_depth: 最大爬取深度，默认使用配置中的值
            max_pages: 最大爬取页面数，默认使用配置中的值
            
        Returns:
            List[Dict]: 爬取的数据列表
        """
        if start_url is None:
            start_url = self.base_url
        
        if max_depth is None:
            max_depth = self.max_depth
        
        if max_pages is None:
            max_pages = self.max_pages
        
        logger.info(f"开始爬取网站: {self.site_config['name']}, 起始URL: {start_url}")
        
        results = []
        queue = [(start_url, 0)]  # (url, depth)
        self.visited_urls = set()
        
        while queue and len(results) < max_pages:
            url, depth = queue.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # 爬取页面
            data = self.crawl(url)
            if data:
                results.append(data)
                logger.info(f"已爬取 {len(results)}/{max_pages} 页面")
                
                # 如果未达到最大深度，提取并添加链接到队列
                if depth < max_depth:
                    links = self.extract_links(data.get("html", ""), url)
                    for link in links:
                        if link not in self.visited_urls:
                            queue.append((link, depth + 1))
        
        logger.info(f"网站爬取完成，共爬取 {len(results)} 页面")
        return results
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        从HTML中提取链接
        
        Args:
            html: HTML内容
            base_url: 基础URL，用于转换相对链接
            
        Returns:
            List[str]: 提取的链接列表
        """
        soup = self.parse_html(html)
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # 转换相对链接为绝对链接
            absolute_url = urljoin(base_url, href)
            
            # 过滤链接，只保留同一域名下的链接
            if absolute_url.startswith(self.base_url):
                links.append(absolute_url)
        
        return links
    
    def parse_page(self, html: str) -> Dict:
        """
        解析页面内容，提取有用信息
        子类应该重写此方法以适应特定网站的结构
        
        Args:
            html: HTML内容
            
        Returns:
            Dict: 解析后的数据
        """
        # 默认实现，子类应该重写
        soup = self.parse_html(html)
        
        # 提取标题
        title = soup.title.text.strip() if soup.title else ""
        
        # 提取正文（简单实现，实际应根据网站结构调整）
        main_content = ""
        for p in soup.find_all("p"):
            main_content += p.text.strip() + "\n"
        
        return {
            "title": title,
            "content": main_content
        }


# 示例用法
if __name__ == "__main__":
    # 创建爬虫实例
    try:
        crawler = WebsiteCrawler("示例网站1")
        # 爬取单个页面
        data = crawler.crawl(crawler.base_url)
        print(f"爬取结果: {data.keys()}")
        
        # 保存数据
        crawler.save_data(data, "example_page.json")
        
        # 爬取整个网站（注意：这可能需要很长时间）
        # results = crawler.crawl_site(max_pages=5)
        # crawler.save_data(results, "example_site.json")
    except Exception as e:
        logger.error(f"爬虫运行失败: {str(e)}")