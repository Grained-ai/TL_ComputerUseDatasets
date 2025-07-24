import sys
import time
from pathlib import Path

import undetected_chromedriver as uc
from modules.website_analysis.model import Page
from loguru import logger

USER_DATA_DIR = "/tmp/uc-profile"  # 可换成任意路径

class TraverseWebsite:
    def __init__(self):
        self.storage = Path('storage')/str(int(time.time()*1000))
        self.analysis_tree = {}

    @staticmethod
    def create_uc_driver():
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless")  # 如需无头模式
        options.add_argument("--start-maximized")

        try:
            driver = uc.Chrome(
                options=options,
                version_main=137,  # 改成你的 Chrome 主版本
                driver_executable_path='/Users/anthonyf/Desktop/Tools/chromedriver/chromedriver'
            )
            return driver
        except Exception as e:
            logger.error(f"创建ChromeDriver失败: {e}")
            logger.info("请确保:")
            logger.info("1. Chrome浏览器已安装")
            logger.info("2. ChromeDriver版本与Chrome版本匹配")
            logger.info("3. 或者更新ChromeDriver路径")
            raise

    def analyze_page(self, page_ins: Page):
        logger.info(f"🚀 开始分析页面: {page_ins.url}")
        logger.info(f"📋 页面配置 - ID: {page_ins.id}, 需要登录: {page_ins.need_login}, 懒加载: {page_ins.if_lazy_load}")
        
        # 创建浏览器驱动
        logger.info("🔧 正在创建ChromeDriver...")
        driver = self.create_uc_driver()
        logger.success("✅ ChromeDriver创建成功")
        
        # 访问页面
        logger.info(f"🌐 正在访问页面: {page_ins.url}")
        driver.get(page_ins.url)
        logger.success("✅ 页面访问成功")

        # 等待页面加载
        logger.info("⏳ 等待页面初始加载完成 (2秒)...")
        time.sleep(2)
        logger.success("✅ 页面初始加载完成")

        # 如果需要处理懒加载
        if page_ins.if_lazy_load:
            logger.info("📜 检测到懒加载配置，开始处理懒加载内容...")

            # 滚动到页面底部触发懒加载
            logger.info("⬇️ 滚动到页面底部触发懒加载...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            logger.info("⏳ 等待懒加载内容加载 (2秒)...")
            time.sleep(2)
            logger.success("✅ 懒加载内容加载完成")

            # 滚动回顶部
            logger.info("⬆️ 滚动回页面顶部...")
            driver.execute_script("window.scrollTo(0, 0);")

            logger.info("⏳ 等待页面稳定 (1秒)...")
            time.sleep(1)
            logger.success("✅ 懒加载处理完成")

        # 生成截图路径并保存
        if not page_ins.screenshot:
            logger.info("📸 开始生成截图...")
            screenshot_path = page_ins.generate_screenshot_path(self.storage)
            logger.info(f"📁 截图路径: {screenshot_path}")

            driver.save_screenshot(str(screenshot_path))
            page_ins.screenshot = screenshot_path
            logger.success(f"✅ 截图已保存到: {screenshot_path}")
        else:
            logger.info("📸 页面已有截图，跳过截图生成")



        logger.success(f"🎉 页面分析完成: {page_ins.url}")
        return page_ins



if __name__ == "__main__":
    # 创建测试实例
    ins = TraverseWebsite()
    
    # 创建测试网站实例
    test_website = Page(
        id="test_001",
        url="https://www.baidu.com",
        need_login=False,
        is_main_page=True,
        if_lazy_load=False
    )
    
    logger.info(f"开始分析网站: {test_website.url}")
    logger.info(f"网站ID: {test_website.id}")
    
    # 分析页面并截图
    result = ins.analyze_page(test_website)
    
    if result.screenshot:
        logger.success(f"分析完成，截图路径: {result.screenshot}")
    else:
        logger.warning("分析完成，但未生成截图")
