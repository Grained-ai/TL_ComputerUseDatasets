#!/usr/bin/env python3
"""
创建 bilibili_tasks_demo 表的脚本
"""

import sys
from pathlib import Path
from loguru import logger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.bilibili.task_hub import TaskHub


def create_demo_table():
    """创建演示表"""
    print("🔧 创建 bilibili_tasks_demo 表")
    print("=" * 50)
    
    # 初始化 TaskHub
    print("🔧 初始化 TaskHub...")
    task_hub = TaskHub()
    
    try:
        # 使用默认配置文件和生产环境（用于连接数据库）
        task_hub.initialize(environment='prod_table')
        print("✅ TaskHub 初始化成功")
    except Exception as e:
        print(f"❌ TaskHub 初始化失败: {e}")
        print("   请检查配置文件是否存在且格式正确")
        return False
    
    if not task_hub.test_connection():
        print("❌ 数据库连接失败")
        return False
    
    print("✅ 数据库连接正常")
    
    # 读取 SQL 脚本
    sql_file = Path(__file__).parent / "create_demo_table.sql"
    if not sql_file.exists():
        print(f"❌ SQL 脚本文件不存在: {sql_file}")
        return False
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("\n🚀 执行建表脚本...")
        
        # 执行 SQL 脚本
        with task_hub.get_connection() as conn:
            with conn.cursor() as cur:
                # 分割并执行每个 SQL 语句
                statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
                
                for i, statement in enumerate(statements, 1):
                    if statement.upper().startswith('SELECT'):
                        # 对于 SELECT 语句，获取结果
                        cur.execute(statement)
                        results = cur.fetchall()
                        if results:
                            print(f"   📊 查询结果: {results}")
                    else:
                        # 对于其他语句，直接执行
                        cur.execute(statement)
                        print(f"   ✅ 执行语句 {i}: {statement[:50]}...")
                
                conn.commit()
        
        print("\n🎉 bilibili_tasks_demo 表创建成功！")
        print("=" * 50)
        print("\n💡 表结构信息:")
        print("   - 表名: bilibili_tasks_demo")
        print("   - 主键: id (SERIAL, 独立序列)")
        print("   - 字段: 与 bilibili_tasks 完全相同")
        print("   - 索引: status, created_at, url")
        print("   - 触发器: 自动更新 modified_at")
        print("   - 测试数据: 3 条示例记录")
        
        return True
        
    except Exception as e:
        logger.error(f"创建演示表失败: {e}")
        print(f"\n❌ 创建失败: {e}")
        return False


if __name__ == "__main__":
    success = create_demo_table()
    sys.exit(0 if success else 1)