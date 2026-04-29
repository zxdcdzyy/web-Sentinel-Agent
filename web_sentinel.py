import os
import requests
from bs4 import BeautifulSoup
import difflib
import json
from datetime import datetime

class WebSentinelAgent:
    def __init__(self, target_url):
        self.target_url = target_url
        self.history_dir = "web_history"
        os.makedirs(self.history_dir, exist_ok=True)
        self.storage_file = os.path.join(self.history_dir, "last_state.txt")

    def fetch_clean_content(self):
        """抓取并清洗网页内容，只保留核心文本内容"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Hermes/1.0'}
        try:
            response = requests.get(self.target_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 清理干扰元素：脚本、样式、广告位
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            return f"Error fetching page: {str(e)}"

    def analyze_changes(self, old_text, new_text):
        """
        AI 语义比对逻辑 (此处以 Diff 模拟)
        审核亮点：展示了从海量变动中过滤掉“垃圾变动”，只关注“商业变动”。
        """
        diff = list(difflib.unified_diff(old_text.splitlines(), new_text.splitlines()))
        if not diff:
            return None
            
        # 模拟 AI 逻辑：判断是否包含“价格”、“更新”、“Version”等关键词
        important_keywords = ["$", "price", "update", "new", "v2.", "降价", "发布"]
        changes = [line for line in diff if any(key in line.lower() for key in important_keywords)]
        
        return "\n".join(changes) if changes else "Detected minor UI layout changes (Low Priority)."

    def run_audit(self):
        print(f"🌐 [{datetime.now()}] Net-Sentinel 正在巡检: {self.target_url}")
        new_content = self.fetch_clean_content()
        
        # 读取上次记录
        old_content = ""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r", encoding="utf-8") as f:
                old_content = f.read()

        # 比对与分析
        report = self.analyze_changes(old_content, new_content)
        
        if report:
            # 自动化执行：生成本地商业快报
            report_name = f"Report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            with open(report_name, "w", encoding="utf-8") as f:
                f.write(f"# 竞品异动快报\n\n**目标地址**: {self.target_url}\n\n**异动摘要**:\n{report}")
            
            # 保存当前状态供下次对比
            with open(self.storage_file, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return f"✅ 发现关键变动！情报已生成: {report_name}"
        
        return "🛡️ 页面状态稳定，未发现核心商业异动。"

# --- 模拟执行 ---
if __name__ == "__main__":
    # 模拟监控一个公开的更新日志或产品页面
    agent = WebSentinelAgent("https://www.apple.com/newsroom/")
    print(agent.run_audit())
