# TaskHub 数据库演示使用说明

## 📋 概述

本目录包含了 Bilibili 任务分发系统的数据库相关脚本和配置文件，提供完整的 TaskHub 功能演示。

## 📁 文件说明

### 配置文件
- `db_config.yaml.demo` - 数据库配置示例文件
- `db_config.yaml` - 实际数据库配置文件（已包含连接信息）

### 脚本文件
- `create_tables.sql` - 生产环境数据库建表脚本
- `create_demo_table.sql` - 演示环境数据库建表脚本
- `create_demo_table.py` - 创建演示表的 Python 脚本
- `task_hub_demo.py` - **TaskHub 完整功能演示脚本**（推荐使用）

## 🚀 使用步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行 TaskHub 完整演示

```bash
cd /Users/anthonyf/projects/grainedAI/TL_ComputerUseDatasets
python scripts/task_hub_demo.py
```

### 3. TaskHub 演示脚本功能

`task_hub_demo.py` 是一个完整的 TaskHub 功能演示脚本，包含以下功能模块：

#### 📝 任务注册功能演示
- 单个任务注册
- 重复注册测试（防重复机制）
- 批量任务注册
- 根据URL获取任务ID

#### 🔍 任务提取功能演示
- 获取待处理任务
- 根据ID获取任务详情
- 根据状态获取任务列表

#### ✏️ 任务状态更新功能演示
- 通用状态更新
- 标记任务为成功
- 标记任务为失败
- 标记任务为处理中

#### 🗑️ 软删除功能专项演示
- 单个任务软删除
- 批量任务软删除
- 查看已删除任务
- 任务恢复功能
- 删除前后统计对比

#### 📊 统计和查询功能演示
- 获取任务统计信息
- 获取最近任务

#### 🚀 高级使用场景演示
- 完整任务处理工作流
- 批量处理演示

#### 🧹 自动清理演示数据
- 演示结束后自动清理测试数据

## 📊 数据库结构

### bilibili_tasks 表（生产环境）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键，自增ID |
| url | VARCHAR(500) | bilibili视频URL，唯一约束 |
| title | VARCHAR(200) | 视频标题 |
| duration | INTEGER | 视频时长（秒） |
| status | INTEGER | 任务状态：0=待下载，1=成功，-1=失败，2=处理中，-99=已删除 |
| download_type | INTEGER | 下载方式：0,1,2,3等不同策略 |
| log | TEXT | 下载备注和日志信息 |
| created_at | TIMESTAMP | 任务创建时间（自动） |
| modified_at | TIMESTAMP | 状态修改时间（自动更新） |

### bilibili_tasks_demo 表（演示环境）

演示表与生产表结构完全相同，但使用独立的主键序列，专门用于演示和测试。

### 软删除机制

- 任务不会被物理删除，而是将 `status` 设置为 `-99`
- 可以通过 `restore_task()` 方法恢复已删除的任务
- 统计功能会区分活跃任务和已删除任务

## 🔧 配置说明

数据库连接信息已配置为：
- 主机: 47.113.144.105:5432
- 数据库: bilibili_tasks
- 用户名: myuser
- 密码: mypassword
- 演示表: bilibili_tasks_demo

## ⚠️ 注意事项

1. 确保 PostgreSQL 服务器正在运行且可访问
2. 确保用户 `myuser` 有创建数据库和表的权限
3. 演示脚本使用 `bilibili_tasks_demo` 表，不会影响生产数据
4. 演示脚本会自动清理测试数据，保持环境整洁
5. 所有日志使用 `loguru.logger`，提供详细的操作记录
6. 所有路径操作使用 `pathlib.Path`，确保跨平台兼容性

## 💡 TaskHub 功能特点

1. **单例模式** - 整个应用中只有一个 TaskHub 实例
2. **灵活初始化** - 支持通过配置文件和环境参数灵活初始化
3. **异常处理** - 所有数据库操作都有完善的异常处理和日志记录
4. **事务管理** - 支持事务管理，确保数据一致性
5. **丰富查询** - 提供多种查询和统计功能
6. **软删除** - 支持软删除功能，保护数据完整性
7. **数据恢复** - 可以随时恢复已删除的任务
8. **批量操作** - 支持单个和批量操作
9. **生产就绪** - 适合在生产环境中使用

## 🔧 TaskHub 初始化方法

TaskHub 提供了灵活的初始化方式，支持通过配置文件和环境参数进行初始化：

### 基本用法

```python
from modules.bilibili.task_hub import TaskHub

# 创建 TaskHub 实例
task_hub = TaskHub()

# 使用默认配置文件和指定环境初始化
task_hub.initialize(environment='playground_table')  # 使用演示环境
# 或
task_hub.initialize(environment='prod_table')        # 使用生产环境
```

### 高级用法

```python
# 指定自定义配置文件路径
task_hub.initialize(
    db_config_path='path/to/custom/config.yaml',
    environment='playground_table'
)

# 使用默认配置文件路径（configs/db_config.yaml）
task_hub.initialize(environment='prod_table')
```

### 环境参数说明

- `playground_table`: 使用演示环境表 `bilibili_tasks_demo`
- `prod_table`: 使用生产环境表 `bilibili_tasks`

### 错误处理

如果指定的环境在配置文件中不存在，TaskHub 会抛出异常并提示可用的环境：

```python
try:
    task_hub.initialize(environment='nonexistent_table')
except Exception as e:
    print(f"错误: {e}")
    # 输出: 配置文件中没有找到环境 'nonexistent_table'。可用的环境: ['playground_table', 'prod_table']
```

## 🐛 故障排除

### 连接失败
- 检查网络连接
- 验证数据库服务器地址和端口
- 确认用户名和密码正确

### 权限错误
- 确保用户有足够的数据库权限
- 检查是否能连接到 `bilibili_tasks` 数据库

### 模块导入错误
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 确保 TaskHub 模块路径正确

### 演示表不存在
- 运行 `python scripts/create_demo_table.py` 创建演示表
- 或者让演示脚本自动处理表创建

## 📞 支持

如果遇到问题，请检查：
1. 数据库连接配置是否正确
2. 所有依赖是否已安装
3. PostgreSQL 服务是否正常运行
4. 演示表 `bilibili_tasks_demo` 是否存在

## 🎯 快速开始

```bash
# 1. 进入项目目录
cd /Users/anthonyf/projects/grainedAI/TL_ComputerUseDatasets

# 2. 创建演示表（如果需要）
python scripts/create_demo_table.py

# 3. 运行完整演示
python scripts/task_hub_demo.py
```

演示脚本会展示 TaskHub 的所有功能，包括任务注册、状态更新、软删除、统计查询等，是学习和了解 TaskHub 用法的最佳方式。