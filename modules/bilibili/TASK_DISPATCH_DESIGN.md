# Bilibili简化任务分发系统设计文档

## 🎯 项目概述

为bilibili模块设计一个简单的任务分发机制，包含URL获取和视频下载两个核心功能。

## 📋 需求分析

### 核心功能
1. **URL Fetcher**：获取bilibili视频URL，插入任务表
2. **Video Fetcher**：从任务表获取待下载任务，执行视频下载

### 工作流程
```
URL Fetcher → 插入任务表 → Video Fetcher → 下载视频 → 更新状态
```

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Bilibili简化任务系统                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐              ┌─────────────┐              │
│  │ URL Fetcher │              │Video Fetcher│              │
│  │             │              │             │              │
│  │ • 获取URL   │─────────────▶│ • 获取任务  │              │
│  │ • 获取标题  │              │ • 下载视频  │              │
│  │ • 获取时长  │              │ • 更新状态  │              │
│  │ • 插入任务  │              │ • 记录日志  │              │
│  └─────────────┘              └─────────────┘              │
│           │                           │                    │
│           └───────────┬───────────────┘                    │
│                       │                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL Database                       │ │
│  │                                                         │ │
│  │              ┌─────────────────┐                       │ │
│  │              │   video_tasks   │                       │ │
│  │              │                 │                       │ │
│  │              │ • id            │                       │ │
│  │              │ • url           │                       │ │
│  │              │ • title         │                       │ │
│  │              │ • duration      │                       │ │
│  │              │ • status        │                       │ │
│  │              │ • download_type │                       │ │
│  │              │ • log           │                       │ │
│  │              │ • created_at    │                       │ │
│  │              │ • modified_at   │                       │ │
│  │              └─────────────────┘                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ 数据库设计

### 核心表：video_tasks

```sql
CREATE TABLE video_tasks (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    title VARCHAR(200),
    duration INTEGER,  -- 视频时长（秒）
    status INTEGER DEFAULT 0,  -- 0:待下载, 1:下载成功, -1:下载失败
    download_type INTEGER DEFAULT 0,  -- 下载方式：0,1,2,3等
    log TEXT,  -- 下载备注/日志
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_video_tasks_status ON video_tasks(status);
CREATE INDEX idx_video_tasks_created_at ON video_tasks(created_at);
CREATE INDEX idx_video_tasks_url ON video_tasks(url);

-- 创建触发器自动更新modified_at
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_video_tasks_modified_at 
    BEFORE UPDATE ON video_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_modified_at_column();
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键，自增ID |
| url | VARCHAR(500) | bilibili视频URL，唯一约束 |
| title | VARCHAR(200) | 视频标题 |
| duration | INTEGER | 视频时长（秒） |
| status | INTEGER | 任务状态：0=待下载，1=成功，-1=失败 |
| download_type | INTEGER | 下载方式：0,1,2,3等不同策略 |
| log | TEXT | 下载备注和日志信息 |
| created_at | TIMESTAMP | 任务创建时间（自动） |
| modified_at | TIMESTAMP | 状态修改时间（自动更新） |

## 🔧 核心组件设计

### 1. TaskHub (任务管理中心) - 单例模式

```python
import psycopg2
import psycopg2.extras
from typing import Optional, Dict, List, Any
from datetime import datetime
import threading
from contextlib import contextmanager

class TaskHub:
    """任务管理中心 - 单例模式管理PostgreSQL连接和所有任务操作"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TaskHub, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_config: Optional[Dict[str, Any]] = None
            self.initialized = False
    
    def initialize(self, db_config: Dict[str, Any]):
        """初始化数据库配置"""
        if not self.initialized:
            self.db_config = db_config
            self.initialized = True
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['username'],
                password=self.db_config['password']
            )
            yield conn
        finally:
            if conn:
                conn.close()
    
    # ==================== 任务注册方法 ====================
    
    def register_task(self, url: str, title: str = None, duration: int = None) -> int:
        """注册单个任务到数据库"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO video_tasks (url, title, duration, status, created_at, modified_at)
                    VALUES (%s, %s, %s, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """, (url, title, duration))
                task_id = cur.fetchone()[0]
                conn.commit()
                return task_id
    
    def batch_register_tasks(self, video_list: List[Dict[str, Any]]) -> List[int]:
        """批量注册任务"""
        task_ids = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for video in video_list:
                    cur.execute("""
                        INSERT INTO video_tasks (url, title, duration, status, created_at, modified_at)
                        VALUES (%s, %s, %s, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ON CONFLICT (url) DO NOTHING
                        RETURNING id
                    """, (video.get('url'), video.get('title'), video.get('duration')))
                    result = cur.fetchone()
                    if result:
                        task_ids.append(result[0])
                conn.commit()
        return task_ids
    
    # ==================== 任务提取方法 ====================
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待处理任务（status=0）"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                    FROM video_tasks 
                    WHERE status = 0 
                    ORDER BY created_at ASC 
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务详情"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                    FROM video_tasks 
                    WHERE id = %s
                """, (task_id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def get_tasks_by_status(self, status: int, limit: int = 100) -> List[Dict[str, Any]]:
        """根据状态获取任务列表"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                    FROM video_tasks 
                    WHERE status = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (status, limit))
                return [dict(row) for row in cur.fetchall()]
    
    # ==================== 任务状态更新方法 ====================
    
    def update_task_status(self, task_id: int, status: int, 
                          download_type: int = None, log: str = None) -> bool:
        """更新任务状态"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE video_tasks 
                    SET status = %s, 
                        download_type = COALESCE(%s, download_type),
                        log = COALESCE(%s, log),
                        modified_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, download_type, log, task_id))
                success = cur.rowcount == 1
                conn.commit()
                return success
    
    def mark_task_success(self, task_id: int, download_type: int = 0, log: str = "下载成功") -> bool:
        """标记任务为成功状态"""
        return self.update_task_status(task_id, 1, download_type, log)
    
    def mark_task_failed(self, task_id: int, error_log: str) -> bool:
        """标记任务为失败状态"""
        return self.update_task_status(task_id, -1, None, error_log)
    
    # ==================== 统计和查询方法 ====================
    
    def get_task_statistics(self) -> Dict[str, int]:
        """获取任务统计信息"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN status = 0 THEN 1 END) as pending,
                        COUNT(CASE WHEN status = 1 THEN 1 END) as success,
                        COUNT(CASE WHEN status = -1 THEN 1 END) as failed
                    FROM video_tasks
                """)
                row = cur.fetchone()
                return {
                    'total': row[0],
                    'pending': row[1], 
                    'success': row[2],
                    'failed': row[3]
                }
    
    def cleanup_old_tasks(self, days: int = 30) -> int:
        """清理指定天数前的已完成任务"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM video_tasks 
                    WHERE status IN (1, -1) 
                    AND created_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                """, (days,))
                deleted_count = cur.rowcount
                conn.commit()
                return deleted_count
```

## 📝 实现计划

### Phase 1: 数据库设置 (1天)
- [ ] 创建PostgreSQL数据库表
- [ ] 设置数据库连接配置
- [ ] 编写数据库操作基础类

### Phase 2: URL Fetcher实现 (2天)
- [ ] 实现bilibili URL解析
- [ ] 实现视频信息获取
- [ ] 实现任务插入功能
- [ ] 添加批量处理支持

### Phase 3: Video Fetcher实现 (2天)
- [ ] 实现任务获取逻辑
- [ ] 实现视频下载功能
- [ ] 实现状态更新机制
- [ ] 添加错误处理和重试

### Phase 4: 测试和优化 (1天)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

## 🛠️ 技术栈

### 核心依赖
```python
# 数据库
psycopg2-binary>=2.9.0   # PostgreSQL数据库驱动

# 网络请求
requests>=2.28.0         # HTTP请求库

# 配置和日志
loguru>=0.7.0            # 日志记录
```

### 配置扩展
```yaml
# configs.yaml 新增部分
database:
  host: "localhost"
  port: 5432
  database: "bilibili_tasks"
  username: "postgres"
  password: "password"
  
bilibili:
  max_concurrent_downloads: 3
  retry_attempts: 3
  download_timeout: 300
```

## 📊 使用示例

### 1. 初始化TaskHub

```python
from task_hub import TaskHub

def main():
    # 获取TaskHub单例实例
    task_hub = TaskHub()
    
    # 初始化数据库连接
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'bilibili_tasks',
        'username': 'postgres',
        'password': 'password'
    }
    
    task_hub.initialize(db_config)

if __name__ == "__main__":
    main()
```

### 2. 直接使用TaskHub进行任务管理

```python
def task_management_example():
    # 获取TaskHub实例（单例）
    task_hub = TaskHub()
    
    # 注册任务
    task_id = task_hub.register_task(
        url="https://www.bilibili.com/video/BV1234567890",
        title="测试视频",
        duration=300
    )
    
    # 获取待处理任务
    pending_tasks = task_hub.get_pending_tasks(limit=5)
    print(f"待处理任务数量: {len(pending_tasks)}")
    
    # 更新任务状态
    success = task_hub.mark_task_success(task_id, download_type=0, log="下载完成")
    print(f"任务状态更新: {'成功' if success else '失败'}")
    
    # 获取统计信息
    stats = task_hub.get_task_statistics()
    print(f"任务统计: {stats}")
    
    # 清理旧任务
    cleaned = task_hub.cleanup_old_tasks(days=7)
    print(f"清理了 {cleaned} 个旧任务")
```

## 🎯 预期成果

1. **简单高效**：只有一张表，逻辑清晰
2. **自动化**：时间戳自动管理，状态自动更新
3. **可扩展**：支持多种下载方式和状态
4. **易维护**：代码结构简单，便于调试
5. **高性能**：异步处理，支持并发下载