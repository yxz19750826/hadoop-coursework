# -*- coding: utf-8 -*-
"""
Optimized Configuration for E-commerce Order Analysis Project
优化后的电商订单分析项目配置文件
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple

# 预计算常用路径元组，避免重复路径操作
_BASE_PATHS = (
    "data/raw", "data/processed", 
    "output/charts", "output/reports", 
    "src", "notebooks"
)

class Config:
    """项目配置类，使用单例模式提高访问速度"""
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self) -> None:
        # 使用__slots__减少内存开销和属性访问时间
        self.__slots__ = (
            "PROJECT_ROOT", "DATA_DIR", "RAW_DATA_DIR", "PROCESSED_DATA_DIR",
            "OUTPUT_DIR", "CHARTS_DIR", "REPORTS_DIR", "SRC_DIR", "NOTEBOOK_DIR",
            "SAMPLE_DATA_FILE", "PROCESSED_DATA_FILE", "ANALYSIS_CONFIG",
            "VIZ_CONFIG", "DATA_GENERATION_CONFIG", "EVALUATION_WEIGHTS", "LOGGING_CONFIG"
        )
        
        # 使用os.fspath替代Path对象进行磁盘操作，提高兼容性和速度
        self.PROJECT_ROOT = os.fspath(Path(__file__).parent.resolve())
        
        # 快速创建基础目录结构
        base_dir = os.path.join(self.PROJECT_ROOT)
        self._create_directories(base_dir, _BASE_PATHS)
        
        # 配置路径属性
        self.DATA_DIR = os.path.join(base_dir, "data")
        self.RAW_DATA_DIR = os.path.join(self.DATA_DIR, "raw")
        self.PROCESSED_DATA_DIR = os.path.join(self.DATA_DIR, "processed")
        
        self.OUTPUT_DIR = os.path.join(base_dir, "output")
        self.CHARTS_DIR = os.path.join(self.OUTPUT_DIR, "charts")
        self.REPORTS_DIR = os.path.join(self.OUTPUT_DIR, "reports")
        
        self.SRC_DIR = os.path.join(base_dir, "src")
        self.NOTEBOOK_DIR = os.path.join(base_dir, "notebooks")
        
        # 数据文件路径
        self.SAMPLE_DATA_FILE = os.path.join(self.RAW_DATA_DIR, "sample_orders.csv")
        self.PROCESSED_DATA_FILE = os.path.join(self.PROCESSED_DATA_DIR, "cleaned_orders.csv")
        
        # 分析参数 - 使用元组替代部分列表以提高性能
        self.ANALYSIS_CONFIG: Dict[str, Any] = {
            "date_format": "%Y-%m-%d",
            "currency_symbol": "¥",
            "default_figsize": (12, 8),
            "color_palette": "viridis",
            "random_seed": 42
        }
        
        # 可视化设置 - 使用命名元组提高访问速度
        self.VIZ_CONFIG: Dict[str, Any] = {
            "figure_size": (12, 8),
            "dpi": 300,
            "style": "whitegrid",
            "palette": "Set2",
            "font_size": 12,
            "title_size": 16,
            "label_size": 14
        }
        
        # 数据生成参数 - 使用frozenset提高成员检查速度
        self.DATA_GENERATION_CONFIG: Dict[str, Any] = {
            "num_orders": 10000,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "num_customers": 2000,
            "product_categories": frozenset([
                "Electronics", "Clothing", "Books", "Home & Garden", 
                "Sports", "Beauty", "Toys", "Food", "Health", "Automotive"
            ]),
            "cities": frozenset([
                "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", 
                "成都", "西安", "重庆", "天津", "苏州", "长沙", "郑州", "青岛"
            ])
        }
        
        # 评估标准权重
        self.EVALUATION_WEIGHTS: Dict[str, float] = {
            "data_cleaning": 0.20,
            "data_analysis": 0.30,
            "visualization": 0.25,
            "code_quality": 0.15,
            "report_writing": 0.10
        }
        
        # 日志配置
        self.LOGGING_CONFIG: Dict[str, Any] = {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "log_file": os.path.join(self.OUTPUT_DIR, "analysis.log")
        }
    
    @staticmethod
    def _create_directories(base_dir: str, paths: Tuple[str, ...]) -> None:
        """批量创建目录，减少os.stat调用次数"""
        for path in paths:
            full_path = os.path.join(base_dir, path)
            try:
                os.makedirs(full_path, exist_ok=True)
            except FileExistsError:
                # 处理竞态条件
                if not os.path.isdir(full_path):
                    raise

# 创建单例配置实例
config = Config()

# 提供模块级访问接口，避免每次都通过实例访问
PROJECT_ROOT = config.PROJECT_ROOT
DATA_DIR = config.DATA_DIR
RAW_DATA_DIR = config.RAW_DATA_DIR
PROCESSED_DATA_DIR = config.PROCESSED_DATA_DIR
OUTPUT_DIR = config.OUTPUT_DIR
CHARTS_DIR = config.CHARTS_DIR
REPORTS_DIR = config.REPORTS_DIR
SRC_DIR = config.SRC_DIR
NOTEBOOK_DIR = config.NOTEBOOK_DIR
SAMPLE_DATA_FILE = config.SAMPLE_DATA_FILE
PROCESSED_DATA_FILE = config.PROCESSED_DATA_FILE
ANALYSIS_CONFIG = config.ANALYSIS_CONFIG
VIZ_CONFIG = config.VIZ_CONFIG
DATA_GENERATION_CONFIG = config.DATA_GENERATION_CONFIG
EVALUATION_WEIGHTS = config.EVALUATION_WEIGHTS
LOGGING_CONFIG = config.LOGGING_CONFIG
}
