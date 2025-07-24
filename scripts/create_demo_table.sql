-- 创建 bilibili_tasks_demo 表
-- 结构与 bilibili_tasks 完全相同，但使用独立的序列

-- 删除已存在的演示表（如果存在）
DROP TABLE IF EXISTS bilibili_tasks_demo CASCADE;

-- 创建演示表：bilibili_tasks_demo
CREATE TABLE bilibili_tasks_demo (
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
CREATE INDEX idx_bilibili_tasks_demo_status ON bilibili_tasks_demo(status);
CREATE INDEX idx_bilibili_tasks_demo_created_at ON bilibili_tasks_demo(created_at);
CREATE INDEX idx_bilibili_tasks_demo_url ON bilibili_tasks_demo(url);

-- 创建触发器：在更新记录时自动更新 modified_at
-- 复用现有的触发器函数 update_modified_at_column()
CREATE TRIGGER update_bilibili_tasks_demo_modified_at 
    BEFORE UPDATE ON bilibili_tasks_demo 
    FOR EACH ROW EXECUTE FUNCTION update_modified_at_column();

-- 插入一些示例数据用于测试
INSERT INTO bilibili_tasks_demo (url, title, duration, status, download_type, log) VALUES
('https://www.bilibili.com/video/BV_DEMO_001', '演示视频1', 300, 0, 0, '待下载'),
('https://www.bilibili.com/video/BV_DEMO_002', '演示视频2', 450, 1, 0, '下载成功'),
('https://www.bilibili.com/video/BV_DEMO_003', '演示视频3', 600, -1, 0, '下载失败：网络错误');

-- 显示创建结果
SELECT 'bilibili_tasks_demo 表创建成功！' as result;
SELECT COUNT(*) as demo_records_count FROM bilibili_tasks_demo;