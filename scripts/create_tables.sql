-- Bilibili 任务分发系统数据库建表脚本
-- 创建 bilibili_tasks 表及相关索引和触发器

-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS bilibili_tasks CASCADE;
DROP FUNCTION IF EXISTS update_modified_at_column() CASCADE;

-- 创建主表：bilibili_tasks
CREATE TABLE bilibili_tasks (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    title VARCHAR(200),
    duration INTEGER,  -- 视频时长（秒）
    status INTEGER DEFAULT 0,  -- 任务状态码：
                               -- 0: 待下载
                               -- 1: 下载成功  
                               -- -1: 下载失败
                               -- 2: 处理中
                               -- -99: 已删除（软删除）
    download_type INTEGER DEFAULT 0,  -- 下载方式：0,1,2,3等
    log TEXT,  -- 下载备注/日志/删除原因
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX idx_bilibili_tasks_status ON bilibili_tasks(status);
CREATE INDEX idx_bilibili_tasks_created_at ON bilibili_tasks(created_at);
CREATE INDEX idx_bilibili_tasks_url ON bilibili_tasks(url);

-- 创建触发器函数：自动更新 modified_at 字段
CREATE OR REPLACE FUNCTION update_modified_at_column() RETURNS TRIGGER AS $BODY$ BEGIN NEW.modified_at = CURRENT_TIMESTAMP; RETURN NEW; END; $BODY$ language 'plpgsql';

-- 创建触发器：在更新记录时自动更新 modified_at
CREATE TRIGGER update_bilibili_tasks_modified_at 
    BEFORE UPDATE ON bilibili_tasks 
    FOR EACH ROW EXECUTE FUNCTION update_modified_at_column();

-- 插入一些示例数据用于测试
INSERT INTO bilibili_tasks (url, title, duration, status, download_type, log) VALUES
('https://www.bilibili.com/video/BV1234567890', '测试视频1', 300, 0, 0, '待下载'),
('https://www.bilibili.com/video/BV0987654321', '测试视频2', 450, 1, 0, '下载成功'),
('https://www.bilibili.com/video/BV1111111111', '测试视频3', 600, -1, 0, '下载失败：网络错误');