#!/usr/bin/env python3
"""
TaskHub 完整功能演示脚本

这个脚本展示了 Bilibili 任务管理中心 TaskHub 的所有功能，包括：
1. 任务注册（单个和批量）
2. 任务查询和检索
3. 任务状态更新
4. 软删除和恢复功能
5. 统计信息查询
6. 高级使用场景演示

适合开发者学习和了解 TaskHub 的完整用法。
"""

import sys
from pathlib import Path
from typing import List
from datetime import datetime
from loguru import logger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from modules.bilibili.task_hub import TaskHub

def demo_task_registration(task_hub: TaskHub) -> List[int]:
    """演示任务注册功能"""
    logger.info("📝 === 任务注册功能演示 ===")
    
    # 1. 单个任务注册
    logger.info("1️⃣ 单个任务注册:")
    task_id1 = task_hub.register_task(
        url="https://www.bilibili.com/video/BV1234567890_DEMO1",
        title="TaskHub 演示视频 1",
        duration=300
    )
    logger.success(f"   任务注册成功，ID: {task_id1}")
    
    # 2. 重复注册测试（应该返回已存在的ID）
    logger.info("2️⃣ 重复注册测试:")
    task_id1_dup = task_hub.register_task(
        url="https://www.bilibili.com/video/BV1234567890_DEMO1",
        title="重复的标题",
        duration=999
    )
    logger.success(f"   重复注册返回已存在ID: {task_id1_dup}")
    
    # 3. 批量任务注册
    logger.info("3️⃣ 批量任务注册:")
    video_list = [
        {
            "url": "https://www.bilibili.com/video/BV1111111111_DEMO2",
            "title": "批量演示视频 1",
            "duration": 180
        },
        {
            "url": "https://www.bilibili.com/video/BV2222222222_DEMO3", 
            "title": "批量演示视频 2",
            "duration": 240
        },
        {
            "url": "https://www.bilibili.com/video/BV3333333333_DEMO4",
            "title": "批量演示视频 3",
            "duration": 360
        }
    ]
    
    batch_ids = task_hub.batch_register_tasks(video_list)
    logger.success(f"   批量注册成功，IDs: {batch_ids}")
    
    # 4. 根据URL获取任务ID
    logger.info("4️⃣ 根据URL获取任务ID:")
    found_id = task_hub.get_task_id_by_url("https://www.bilibili.com/video/BV1111111111_DEMO2")
    logger.success(f"   找到任务ID: {found_id}")
    
    return [task_id1] + batch_ids


def demo_task_retrieval(task_hub: TaskHub, demo_task_ids: List[int]):
    """演示任务提取功能"""
    logger.info("🔍 === 任务提取功能演示 ===")
    
    # 1. 获取待处理任务
    logger.info("1️⃣ 获取待处理任务:")
    pending_tasks = task_hub.get_pending_tasks(limit=5)
    logger.success(f"   待处理任务数量: {len(pending_tasks)}")
    for task in pending_tasks[:3]:  # 只显示前3个
        logger.info(f"      ID: {task['id']}, URL: {task['url'][:50]}..., 状态: {task['status']}")
    
    # 2. 根据ID获取任务详情
    logger.info("2️⃣ 根据ID获取任务详情:")
    if demo_task_ids:
        task_detail = task_hub.get_task_by_id(demo_task_ids[0])
        if task_detail:
            logger.success("   任务详情:")
            logger.info(f"      ID: {task_detail['id']}")
            logger.info(f"      URL: {task_detail['url']}")
            logger.info(f"      标题: {task_detail['title']}")
            logger.info(f"      时长: {task_detail['duration']}秒")
            logger.info(f"      状态: {task_detail['status']}")
            logger.info(f"      创建时间: {task_detail['created_at']}")
    
    # 3. 根据状态获取任务列表
    logger.info("3️⃣ 根据状态获取任务列表:")
    status_0_tasks = task_hub.get_tasks_by_status(status=0, limit=3)
    logger.success(f"   状态为0(待下载)的任务: {len(status_0_tasks)}个")
    
    status_1_tasks = task_hub.get_tasks_by_status(status=1, limit=3)
    logger.success(f"   状态为1(成功)的任务: {len(status_1_tasks)}个")


def demo_task_status_update(task_hub: TaskHub, demo_task_ids: List[int]):
    """演示任务状态更新功能"""
    logger.info("✏️ === 任务状态更新功能演示 ===")
    
    if len(demo_task_ids) < 3:
        logger.warning("   演示任务数量不足，跳过状态更新演示")
        return
    
    # 1. 通用状态更新
    logger.info("1️⃣ 通用状态更新:")
    success = task_hub.update_task_status(
        task_id=demo_task_ids[0],
        status=2,  # 处理中
        download_type=1,
        log="开始处理任务"
    )
    logger.success(f"   状态更新结果: {success}")
    
    # 2. 标记任务为成功
    logger.info("2️⃣ 标记任务为成功:")
    success = task_hub.mark_task_success(
        task_id=demo_task_ids[1],
        download_type=0,
        log="下载完成，质量: 1080P"
    )
    logger.success(f"   标记成功结果: {success}")
    
    # 3. 标记任务为失败
    logger.info("3️⃣ 标记任务为失败:")
    success = task_hub.mark_task_failed(
        task_id=demo_task_ids[2],
        error_log="下载失败: 网络超时"
    )
    logger.success(f"   标记失败结果: {success}")
    
    # 4. 标记任务为处理中
    logger.info("4️⃣ 标记任务为处理中:")
    if len(demo_task_ids) > 3:
        success = task_hub.mark_task_processing(
            task_id=demo_task_ids[3],
            log="正在解析视频信息"
        )
        logger.success(f"   标记处理中结果: {success}")


def demo_soft_delete_features(task_hub: TaskHub) -> List[int]:
    """演示软删除功能"""
    logger.info("🗑️ === 软删除功能专项演示 ===")
    
    # 1. 注册一些测试任务用于软删除演示
    logger.info("📝 步骤1: 注册软删除测试任务")
    test_urls = [
        "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_1",
        "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_2", 
        "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_3",
        "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_4"
    ]
    
    task_ids = []
    for i, url in enumerate(test_urls, 1):
        task_id = task_hub.register_task(
            url=url,
            title=f"软删除测试任务 {i}",
            duration=300
        )
        task_ids.append(task_id)
        logger.success(f"   注册任务 {i}: ID={task_id}")
    
    logger.info(f"📊 注册了 {len(task_ids)} 个测试任务: {task_ids}")
    
    # 2. 查看初始统计
    logger.info("📈 步骤2: 查看初始统计")
    stats = task_hub.get_task_statistics()
    logger.info(f"   总任务数: {stats['total']}")
    logger.info(f"   活跃任务数: {stats['active']}")
    logger.info(f"   已删除任务数: {stats['deleted']}")
    logger.info(f"   待处理: {stats['pending']}")
    
    # 3. 单个任务软删除
    logger.info("🗑️ 步骤3: 单个任务软删除")
    delete_task_id = task_ids[0]
    success = task_hub.delete_task(delete_task_id, "单个删除演示")
    if success:
        logger.success(f"   软删除任务 ID {delete_task_id}: {success}")
    else:
        logger.error(f"   软删除任务 ID {delete_task_id}: {success}")
    
    # 4. 批量任务软删除
    logger.info("🗑️ 步骤4: 批量任务软删除")
    batch_delete_ids = task_ids[1:3]  # 删除第2和第3个任务
    result = task_hub.batch_delete_tasks(batch_delete_ids, "批量删除演示")
    total_attempted = len(batch_delete_ids)
    logger.success(f"   批量删除结果: 成功 {result['success']}/{total_attempted} 个任务")
    if result['failed'] > 0:
        logger.warning(f"   失败: {result['failed']} 个任务")
    if result['already_deleted'] > 0:
        logger.info(f"   已删除: {result['already_deleted']} 个任务")
    if result['not_found'] > 0:
        logger.error(f"   不存在: {result['not_found']} 个任务")
    
    # 5. 查看已删除任务
    logger.info("👀 步骤5: 查看已删除任务")
    deleted_tasks = task_hub.get_deleted_tasks()
    logger.success(f"   已删除任务数量: {len(deleted_tasks)}")
    for task in deleted_tasks:
        logger.info(f"      ID: {task['id']}, URL: {task['url'][:50]}..., 删除时间: {task['modified_at']}")
    
    # 6. 查看更新后的统计
    logger.info("📈 步骤6: 查看删除后统计")
    stats = task_hub.get_task_statistics()
    logger.info(f"   总任务数: {stats['total']}")
    logger.info(f"   活跃任务数: {stats['active']}")
    logger.info(f"   已删除任务数: {stats['deleted']}")
    logger.info(f"   待处理: {stats['pending']}")
    
    # 7. 恢复一个任务
    logger.info("♻️ 步骤7: 恢复任务")
    if deleted_tasks:
        restore_task_id = deleted_tasks[0]['id']
        success = task_hub.restore_task(restore_task_id, 0)  # 恢复为待处理状态
        if success:
            logger.success(f"   恢复任务 ID {restore_task_id}: {success}")
        else:
            logger.error(f"   恢复任务 ID {restore_task_id}: {success}")
        
        # 查看恢复后的统计
        logger.info("📈 步骤8: 查看恢复后统计")
        stats = task_hub.get_task_statistics()
        logger.info(f"   总任务数: {stats['total']}")
        logger.info(f"   活跃任务数: {stats['active']}")
        logger.info(f"   已删除任务数: {stats['deleted']}")
        logger.info(f"   待处理: {stats['pending']}")
    
    return [delete_task_id] + batch_delete_ids


def demo_statistics_and_queries(task_hub: TaskHub):
    """演示统计和查询功能"""
    logger.info("📊 === 统计和查询功能演示 ===")
    
    # 1. 获取任务统计信息
    logger.info("1️⃣ 任务统计信息:")
    stats = task_hub.get_task_statistics()
    logger.success("   统计结果:")
    logger.info(f"      总任务数: {stats['total']}")
    logger.info(f"      活跃任务数: {stats['active']}")
    logger.info(f"      待处理: {stats['pending']}")
    logger.info(f"      成功: {stats['success']}")
    logger.info(f"      失败: {stats['failed']}")
    logger.info(f"      处理中: {stats['processing']}")
    logger.info(f"      已删除: {stats['deleted']}")
    logger.info(f"      其他状态: {stats['other']}")
    
    # 2. 获取最近任务
    logger.info("2️⃣ 获取最近24小时内的任务:")
    recent_tasks = task_hub.get_recent_tasks(hours=24, limit=5)
    logger.success(f"   最近任务数量: {len(recent_tasks)}")
    for task in recent_tasks[:3]:  # 只显示前3个
        logger.info(f"      ID: {task['id']}, 状态: {task['status']}, 创建时间: {task['created_at']}")


def demo_advanced_usage(task_hub: TaskHub):
    """演示高级使用场景"""
    logger.info("🚀 === 高级使用场景演示 ===")
    
    # 1. 任务处理工作流演示
    logger.info("1️⃣ 完整任务处理工作流:")
    
    # 注册新任务
    workflow_task_id = task_hub.register_task(
        url="https://www.bilibili.com/video/BV_WORKFLOW_DEMO",
        title="工作流演示视频",
        duration=600
    )
    logger.info(f"   📝 步骤1: 注册任务 ID: {workflow_task_id}")
    
    # 获取任务详情
    task_detail = task_hub.get_task_by_id(workflow_task_id)
    logger.info(f"   🔍 步骤2: 获取任务详情 - {task_detail['title']}")
    
    # 标记为处理中
    task_hub.mark_task_processing(workflow_task_id, "开始下载")
    logger.info("   ⏳ 步骤3: 标记为处理中")
    
    # 模拟处理完成，标记为成功
    task_hub.mark_task_success(workflow_task_id, download_type=1, log="下载完成，文件大小: 256MB")
    logger.info("   ✅ 步骤4: 标记为成功")
    
    # 2. 批量处理演示
    logger.info("2️⃣ 批量处理演示:")
    
    # 获取所有待处理任务
    pending_tasks = task_hub.get_pending_tasks(limit=10)
    logger.info(f"   📋 获取到 {len(pending_tasks)} 个待处理任务")
    
    # 模拟批量处理
    processed_count = 0
    for task in pending_tasks[:2]:  # 只处理前2个作为演示
        task_hub.mark_task_processing(task['id'], "批量处理中")
        processed_count += 1
    logger.info(f"   ⚡ 批量标记 {processed_count} 个任务为处理中")


def cleanup_demo_data(task_hub: TaskHub):
    """清理演示数据"""
    logger.info("🧹 === 清理演示数据 ===")
    
    try:
        with task_hub.get_connection() as conn:
            with conn.cursor() as cur:
                # 删除所有演示任务
                demo_urls = [
                    "https://www.bilibili.com/video/BV1234567890_DEMO1",
                    "https://www.bilibili.com/video/BV1111111111_DEMO2",
                    "https://www.bilibili.com/video/BV2222222222_DEMO3",
                    "https://www.bilibili.com/video/BV3333333333_DEMO4",
                    "https://www.bilibili.com/video/BV_WORKFLOW_DEMO",
                    "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_1",
                    "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_2",
                    "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_3",
                    "https://www.bilibili.com/video/BV_SOFT_DELETE_TEST_4"
                ]
                
                deleted_count = 0
                for url in demo_urls:
                    cur.execute(f"DELETE FROM {task_hub.table_name} WHERE url = %s", (url,))
                    if cur.rowcount > 0:
                        deleted_count += cur.rowcount
                
                conn.commit()
                logger.success(f"   清理完成，删除了 {deleted_count} 个演示任务")
                
    except Exception as e:
        logger.error(f"   清理演示数据时出现错误: {e}")


def main():
    """主函数 - TaskHub 完整功能演示"""
    logger.info("🎯 TaskHub 完整功能演示")
    logger.info("=" * 60)
    
    # 初始化 TaskHub
    logger.info("🔧 初始化 TaskHub...")
    task_hub = TaskHub()
    
    try:
        # 使用默认配置文件和演示环境
        task_hub.initialize(environment='playground_table')
        logger.success("   TaskHub 初始化成功")
    except Exception as e:
        logger.error(f"   TaskHub 初始化失败: {e}")
        logger.error("   请检查配置文件是否存在且格式正确")
        return
    
    # 测试连接
    logger.info("🔗 测试数据库连接...")
    if task_hub.test_connection():
        logger.success("   数据库连接正常")
    else:
        logger.error("   数据库连接失败")
        return
    
    try:
        # 演示各种功能
        logger.info("\n" + "="*60)
        demo_task_ids = demo_task_registration(task_hub)
        
        logger.info("\n" + "="*60)
        demo_task_retrieval(task_hub, demo_task_ids)
        
        logger.info("\n" + "="*60)
        demo_task_status_update(task_hub, demo_task_ids)
        
        logger.info("\n" + "="*60)
        # 演示软删除功能
        deleted_task_ids = demo_soft_delete_features(task_hub)
        
        logger.info("\n" + "="*60)
        # 演示统计和高级功能
        demo_statistics_and_queries(task_hub)
        
        logger.info("\n" + "="*60)
        demo_advanced_usage(task_hub)
        
        logger.info("\n" + "="*60)
        # 清理演示数据
        cleanup_demo_data(task_hub)
        
        logger.success("\n🎉 TaskHub 功能演示完成！")
        logger.info("=" * 60)
        logger.info("💡 TaskHub 功能特点:")
        logger.info("   1. TaskHub 使用单例模式，整个应用中只有一个实例")
        logger.info("   2. 支持通过配置文件和环境参数灵活初始化")
        logger.info("   3. 所有数据库操作都有异常处理和日志记录")
        logger.info("   4. 支持事务管理，确保数据一致性")
        logger.info("   5. 提供丰富的查询和统计功能")
        logger.info("   6. 支持软删除功能，保护数据完整性")
        logger.info("   7. 数据不会真正删除，只是状态变为 -99")
        logger.info("   8. 可以随时恢复已删除的任务")
        logger.info("   9. 统计信息会区分活跃和已删除任务")
        logger.info("   10. 支持单个和批量删除操作")
        logger.info("   11. 适合在生产环境中使用")
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        logger.error("请检查数据库连接和表结构是否正确")


if __name__ == "__main__":
    main()