from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
import uuid
import json
from datetime import datetime


@dataclass
class Page:
    id: str
    url: str
    need_login: bool = False
    is_main_page: bool = False
    screenshot: Optional[Path] = None
    if_lazy_load: bool = False
    
    def __post_init__(self):
        """初始化后自动生成ID（如果未提供）"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def generate_screenshot_path(self, base_dir: Path) -> Path:
        """
        基于website.url和website.id生成hash关系的截图存储路径
        
        Args:
            base_dir: 基础存储目录
            
        Returns:
            Path: 截图文件的完整路径
        """
        # 创建基于URL和ID的hash
        hash_input = f"{self.url}_{self.id}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        
        # 使用hash的前两位作为子目录，避免单个目录文件过多
        sub_dir = hash_value[:2]
        filename = f"{hash_value}.png"
        
        screenshot_path = base_dir / "screenshots" / sub_dir / filename
        
        # 确保目录存在
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        return screenshot_path
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将Page实例转换为字典格式，用于JSON序列化
        
        Returns:
            Dict[str, Any]: 包含所有字段的字典
        """
        data = asdict(self)
        
        # 处理Path类型的字段
        if self.screenshot:
            data['screenshot'] = str(self.screenshot)
        
        # 添加时间戳
        data['created_at'] = datetime.now().isoformat()
        
        return data
    
    def to_json(self, indent: int = 2) -> str:
        """
        将Page实例转换为JSON字符串
        
        Args:
            indent: JSON缩进级别
            
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save_to_file(self, file_path: Path) -> None:
        """
        将Page实例保存到JSON文件
        
        Args:
            file_path: 保存文件的路径
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Page':
        """
        从字典创建Page实例
        
        Args:
            data: 包含Page数据的字典
            
        Returns:
            Page: Page实例
        """
        # 创建数据副本，避免修改原始数据
        page_data = data.copy()
        
        # 移除非Page字段的数据
        page_data.pop('created_at', None)
        
        # 处理Path类型的字段
        if 'screenshot' in page_data and page_data['screenshot']:
            page_data['screenshot'] = Path(page_data['screenshot'])
        
        return cls(**page_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Page':
        """
        从JSON字符串创建Page实例
        
        Args:
            json_str: JSON字符串
            
        Returns:
            Page: Page实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'Page':
        """
        从JSON文件加载Page实例
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            Page: Page实例
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            json_str = f.read()
        
        return cls.from_json(json_str)


# 使用示例和测试
if __name__ == "__main__":
    from loguru import logger
    
    # 创建测试Page实例
    test_page = Page(
        id="test_001",
        url="https://www.example.com",
        need_login=False,
        is_main_page=True,
        if_lazy_load=False
    )
    
    # 生成截图路径
    base_dir = Path("./storage")
    screenshot_path = test_page.generate_screenshot_path(base_dir)
    test_page.screenshot = screenshot_path
    
    logger.info(f"创建Page实例: {test_page}")
    logger.info(f"截图路径: {screenshot_path}")
    
    # 测试JSON序列化
    json_str = test_page.to_json()
    logger.info(f"JSON字符串:\n{json_str}")
    
    # 测试保存到文件
    json_file_path = Path("./storage/test_page.json")
    test_page.save_to_file(json_file_path)
    logger.success(f"已保存到文件: {json_file_path}")
    
    # 测试从文件加载
    try:
        loaded_page = Page.load_from_file(json_file_path)
        logger.success(f"从文件加载成功: {loaded_page}")
        
        # 验证数据一致性
        assert loaded_page.id == test_page.id
        assert loaded_page.url == test_page.url
        assert loaded_page.need_login == test_page.need_login
        assert loaded_page.is_main_page == test_page.is_main_page
        assert loaded_page.if_lazy_load == test_page.if_lazy_load
        assert str(loaded_page.screenshot) == str(test_page.screenshot)
        
        logger.success("✅ 数据一致性验证通过！")
        
    except Exception as e:
        logger.error(f"加载失败: {e}")
    
    # 测试从JSON字符串创建
    try:
        page_from_json = Page.from_json(json_str)
        logger.success(f"从JSON字符串创建成功: {page_from_json}")
    except Exception as e:
        logger.error(f"从JSON创建失败: {e}")

