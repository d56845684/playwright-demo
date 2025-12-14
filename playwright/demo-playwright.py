# demo_playwright.py
import os
from playwright.sync_api import sync_playwright
import time
BASE = "http://127.0.0.1:5000"
DOWNLOAD_DIR = "downloads"

USERNAME = "demo"
PASSWORD = "demo123"

# 你要 demo 的查詢條件
Q_COUNTY = "新竹縣"
Q_DISTRICT = ""   # "" 表示不限
Q_CHECKIN = "2025-12-20"
Q_NIGHTS = "1"          # 1=2天1夜
Q_TENTS = "2"           # 入住帳數

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        # 1) Login
        page.goto(f"{BASE}/login")
        page.fill('input[name="username"]', USERNAME)
        time.sleep(3)
        page.fill('input[name="password"]', PASSWORD)
        time.sleep(3)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE}/reserve")
        time.sleep(5)

        # 2) Fill reserve form
        page.select_option('select[name="county"]', label=Q_COUNTY)
        time.sleep(1)

        if Q_DISTRICT:
            page.select_option('select[name="district"]', label=Q_DISTRICT)
        else:
            page.select_option('select[name="district"]', value="")
        time.sleep(1)

        page.fill('input[name="checkin"]', Q_CHECKIN)
        time.sleep(1)
        page.select_option('select[name="nights"]', value=Q_NIGHTS)
        time.sleep(1)
        page.fill('input[name="tents"]', Q_TENTS)
        time.sleep(1)

        page.click('button:has-text("立即搜尋")')
        page.wait_for_load_state("networkidle")

        # 3) Scrape results (簡單印出營區名稱)
        camps = page.locator("ul > li > b").all_text_contents()
        print(f"Found camps: {len(camps)}")
        for i, name in enumerate(camps, 1):
            print(f"{i:02d}. {name}")

        # 4) Download CSV
        with page.expect_download(timeout=10000) as d:
            page.click('a[href^="/download"]')
        download = d.value

        save_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
        download.save_as(save_path)
        print(f"Downloaded: {save_path}")
        time.sleep(300)
        browser.close()

if __name__ == "__main__":
    main()