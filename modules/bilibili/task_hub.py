"""
TaskHub - 任务管理中心

实现单例模式的PostgreSQL任务管理中心，提供统一的任务注册、提取和状态更新功能。
"""

import psycopg2
import psycopg2.extras
from typing import Optional, Dict, List, Any
from datetime import datetime
import threading
from contextlib import contextmanager
from pathlib import Path
import yaml
from loguru import logger


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
            self.table_name: str = 'bilibili_tasks'  # 默认表名
            self.initialized = False
            logger.info("TaskHub实例创建")
    
    def _validate_table_name(self, table_name: str) -> bool:
        """验证表名安全性，只允许字母、数字和下划线"""
        import re
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name))
    
    def _load_db_config(self, db_config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载数据库配置文件
        
        Args:
            db_config_path: 配置文件路径，默认为 configs/db_config.yaml
            
        Returns:
            数据库配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if db_config_path is None:
            # 默认配置文件路径
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / 'configs' / 'db_config.yaml'
        else:
            config_path = Path(db_config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'database' not in config:
                raise ValueError("配置文件中缺少 'database' 配置节")
                
            return config['database']
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ValueError(f"读取配置文件失败: {e}")
    
    def initialize(self, db_config_path: Optional[str] = None, environment: str = 'playground_table'):
        """初始化数据库配置
        
        Args:
            db_config_path: 数据库配置文件路径，默认为 configs/db_config.yaml
            environment: 环境参数，用于选择表名 ('playground_table' 或 'prod_table')
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误或环境参数无效
        """
        if not self.initialized:
            # 加载数据库配置
            db_config = self._load_db_config(db_config_path)
            
            # 检查环境参数是否存在于配置中
            if environment not in db_config:
                available_envs = [key for key in db_config.keys() if key.endswith('_table')]
                raise ValueError(f"配置文件中没有找到环境 '{environment}'。可用的环境: {available_envs}")
            
            # 获取表名
            table_name = db_config[environment]
            
            if not self._validate_table_name(table_name):
                raise ValueError(f"无效的表名: {table_name}")
            
            self.db_config = db_config
            self.table_name = table_name
            self.initialized = True
            logger.info(f"TaskHub初始化完成，数据库: {db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}, 表名: {table_name}, 环境: {environment}")
        else:
            logger.warning("TaskHub已经初始化，跳过重复初始化")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not self.initialized:
            raise RuntimeError("TaskHub未初始化，请先调用initialize()方法")
        
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
        except psycopg2.Error as e:
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    logger.info("数据库连接测试成功")
                    return result[0] == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    # ==================== 任务注册方法 ====================
    
    def register_task(self, url: str, title: str = None, duration: int = None) -> int:
        """注册单个任务到数据库"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        INSERT INTO {self.table_name} (url, title, duration, status, created_at, modified_at)
                        VALUES (%s, %s, %s, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (url, title, duration))
                    task_id = cur.fetchone()[0]
                    conn.commit()
                    logger.info(f"任务注册成功 - ID: {task_id}, URL: {url}")
                    return task_id
        except psycopg2.IntegrityError as e:
            if "duplicate key" in str(e):
                logger.warning(f"任务已存在，URL: {url}")
                # 返回已存在任务的ID
                return self.get_task_id_by_url(url)
            else:
                logger.error(f"任务注册失败: {e}")
                raise
        except Exception as e:
            logger.error(f"任务注册异常: {e}")
            raise
    
    def batch_register_tasks(self, video_list: List[Dict[str, Any]]) -> List[int]:
        """批量注册任务"""
        task_ids = []
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for video in video_list:
                        try:
                            cur.execute(f"""
                                INSERT INTO {self.table_name} (url, title, duration, status, created_at, modified_at)
                                VALUES (%s, %s, %s, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT (url) DO NOTHING
                                RETURNING id
                            """, (video.get('url'), video.get('title'), video.get('duration')))
                            result = cur.fetchone()
                            if result:
                                task_ids.append(result[0])
                        except Exception as e:
                            logger.error(f"批量注册单个任务失败: {video.get('url')}, 错误: {e}")
                            continue
                    conn.commit()
                    logger.info(f"批量注册任务完成，成功: {len(task_ids)}/{len(video_list)}")
        except Exception as e:
            logger.error(f"批量注册任务异常: {e}")
            raise
        return task_ids
    
    def get_task_id_by_url(self, url: str) -> Optional[int]:
        """根据URL获取任务ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id FROM {self.table_name} WHERE url = %s", (url,))
                    result = cur.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"根据URL获取任务ID失败: {e}")
            return None
    
    # ==================== 任务提取方法 ====================
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待处理任务（status=0）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(f"""
                        SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                        FROM {self.table_name} 
                        WHERE status = 0 
                        ORDER BY created_at ASC 
                        LIMIT %s
                    """, (limit,))
                    tasks = [dict(row) for row in cur.fetchall()]
                    logger.debug(f"获取待处理任务: {len(tasks)}个")
                    return tasks
        except Exception as e:
            logger.error(f"获取待处理任务失败: {e}")
            return []
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取任务详情"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(f"""
                        SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                        FROM {self.table_name} 
                        WHERE id = %s
                    """, (task_id,))
                    row = cur.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            logger.error(f"根据ID获取任务失败: {e}")
            return None
    
    def get_tasks_by_status(self, status: int, limit: int = 100) -> List[Dict[str, Any]]:
        """根据状态获取任务列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(f"""
                        SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                        FROM {self.table_name} 
                        WHERE status = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (status, limit))
                    tasks = [dict(row) for row in cur.fetchall()]
                    logger.debug(f"获取状态为{status}的任务: {len(tasks)}个")
                    return tasks
        except Exception as e:
            logger.error(f"根据状态获取任务失败: {e}")
            return []
    
    # ==================== 任务状态更新方法 ====================
    
    def update_task_status(self, task_id: int, status: int, 
                          download_type: int = None, log: str = None) -> bool:
        """更新任务状态"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        UPDATE {self.table_name} 
                        SET status = %s, 
                            download_type = COALESCE(%s, download_type),
                            log = COALESCE(%s, log),
                            modified_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (status, download_type, log, task_id))
                    success = cur.rowcount == 1
                    conn.commit()
                    if success:
                        logger.info(f"任务状态更新成功 - ID: {task_id}, 状态: {status}")
                    else:
                        logger.warning(f"任务状态更新失败，任务不存在 - ID: {task_id}")
                    return success
        except Exception as e:
            logger.error(f"更新任务状态异常: {e}")
            return False
    
    def mark_task_success(self, task_id: int, download_type: int = 0, log: str = "下载成功") -> bool:
        """标记任务为成功状态"""
        return self.update_task_status(task_id, 1, download_type, log)
    
    def mark_task_failed(self, task_id: int, error_log: str) -> bool:
        """标记任务为失败状态"""
        return self.update_task_status(task_id, -1, None, error_log)
    
    def mark_task_processing(self, task_id: int, log: str = "正在处理") -> bool:
        """标记任务为处理中状态（可选，用于防止重复处理）"""
        return self.update_task_status(task_id, 2, None, log)
    
    # ==================== 任务删除方法 ====================
    
    def delete_task(self, task_id: int, reason: str = "用户删除") -> bool:
        """软删除任务（将状态设置为-99）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 检查任务是否存在且未被删除
                    cur.execute(f"SELECT status FROM {self.table_name} WHERE id = %s", (task_id,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"删除失败，任务不存在 - ID: {task_id}")
                        return False
                    
                    if result[0] == -99:
                        logger.warning(f"删除失败，任务已被删除 - ID: {task_id}")
                        return False
                    
                    # 执行软删除
                    cur.execute(f"""
                        UPDATE {self.table_name} 
                        SET status = -99, 
                            log = %s,
                            modified_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (f"已删除: {reason}", task_id))
                    success = cur.rowcount == 1
                    conn.commit()
                    
                    if success:
                        logger.info(f"任务软删除成功 - ID: {task_id}, 原因: {reason}")
                    else:
                        logger.warning(f"任务软删除失败 - ID: {task_id}")
                    return success
        except Exception as e:
            logger.error(f"删除任务异常: {e}")
            return False
    
    def batch_delete_tasks(self, task_ids: List[int], reason: str = "批量删除") -> Dict[str, int]:
        """批量软删除任务"""
        result = {"success": 0, "failed": 0, "already_deleted": 0, "not_found": 0}
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for task_id in task_ids:
                        try:
                            # 检查任务状态
                            cur.execute(f"SELECT status FROM {self.table_name} WHERE id = %s", (task_id,))
                            task_result = cur.fetchone()
                            
                            if not task_result:
                                result["not_found"] += 1
                                continue
                            
                            if task_result[0] == -99:
                                result["already_deleted"] += 1
                                continue
                            
                            # 执行软删除
                            cur.execute(f"""
                                UPDATE {self.table_name} 
                                SET status = -99, 
                                    log = %s,
                                    modified_at = CURRENT_TIMESTAMP
                                WHERE id = %s
                            """, (f"已删除: {reason}", task_id))
                            
                            if cur.rowcount == 1:
                                result["success"] += 1
                            else:
                                result["failed"] += 1
                                
                        except Exception as e:
                            logger.error(f"批量删除单个任务失败 - ID: {task_id}, 错误: {e}")
                            result["failed"] += 1
                            continue
                    
                    conn.commit()
                    logger.info(f"批量删除任务完成 - 成功: {result['success']}, 失败: {result['failed']}, "
                              f"已删除: {result['already_deleted']}, 不存在: {result['not_found']}")
        except Exception as e:
            logger.error(f"批量删除任务异常: {e}")
            
        return result
    
    def restore_task(self, task_id: int, new_status: int = 0, log: str = "任务已恢复") -> bool:
        """恢复已删除的任务"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 检查任务是否存在且已被删除
                    cur.execute(f"SELECT status FROM {self.table_name} WHERE id = %s", (task_id,))
                    result = cur.fetchone()
                    if not result:
                        logger.warning(f"恢复失败，任务不存在 - ID: {task_id}")
                        return False
                    
                    if result[0] != -99:
                        logger.warning(f"恢复失败，任务未被删除 - ID: {task_id}, 当前状态: {result[0]}")
                        return False
                    
                    # 恢复任务
                    cur.execute(f"""
                        UPDATE {self.table_name} 
                        SET status = %s, 
                            log = %s,
                            modified_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_status, log, task_id))
                    success = cur.rowcount == 1
                    conn.commit()
                    
                    if success:
                        logger.info(f"任务恢复成功 - ID: {task_id}, 新状态: {new_status}")
                    else:
                        logger.warning(f"任务恢复失败 - ID: {task_id}")
                    return success
        except Exception as e:
            logger.error(f"恢复任务异常: {e}")
            return False
    
    def get_deleted_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取已删除的任务列表"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(f"""
                        SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                        FROM {self.table_name} 
                        WHERE status = -99 
                        ORDER BY modified_at DESC 
                        LIMIT %s
                    """, (limit,))
                    tasks = [dict(row) for row in cur.fetchall()]
                    logger.debug(f"获取已删除任务: {len(tasks)}个")
                    return tasks
        except Exception as e:
            logger.error(f"获取已删除任务失败: {e}")
            return []
    

    # ==================== 统计和查询方法 ====================
    
    def get_task_statistics(self) -> Dict[str, int]:
        """获取任务统计信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(CASE WHEN status = 0 THEN 1 END) as pending,
                            COUNT(CASE WHEN status = 1 THEN 1 END) as success,
                            COUNT(CASE WHEN status = -1 THEN 1 END) as failed,
                            COUNT(CASE WHEN status = 2 THEN 1 END) as processing,
                            COUNT(CASE WHEN status = -99 THEN 1 END) as deleted,
                            COUNT(CASE WHEN status NOT IN (0, 1, -1, 2, -99) THEN 1 END) as other
                        FROM {self.table_name}
                    """)
                    row = cur.fetchone()
                    stats = {
                        'total': row[0],
                        'pending': row[1], 
                        'success': row[2],
                        'failed': row[3],
                        'processing': row[4],
                        'deleted': row[5],
                        'other': row[6],
                        'active': row[0] - row[5]  # 总数减去已删除的
                    }
                    logger.debug(f"任务统计: {stats}")
                    return stats
        except Exception as e:
            logger.error(f"获取任务统计失败: {e}")
            return {'total': 0, 'pending': 0, 'success': 0, 'failed': 0, 'processing': 0, 'deleted': 0, 'other': 0, 'active': 0}
    

    def get_recent_tasks(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近指定小时内的任务"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(f"""
                        SELECT id, url, title, duration, status, download_type, log, created_at, modified_at
                        FROM {self.table_name} 
                        WHERE created_at >= NOW() - INTERVAL '%s hours'
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (hours, limit))
                    tasks = [dict(row) for row in cur.fetchall()]
                    logger.debug(f"获取最近{hours}小时任务: {len(tasks)}个")
                    return tasks
        except Exception as e:
            logger.error(f"获取最近任务失败: {e}")
            return []