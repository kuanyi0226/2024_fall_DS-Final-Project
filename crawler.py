from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import os
import time

def crawl_typhoon():
    # 檢查 CSV 是否存在
    input_file = 'data/typhoon_data.csv'
    if os.path.exists(input_file):
        return
        
    # 設定 Selenium 的 WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 啟動無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    # 打開目標網站
    url = "https://rdc28.cwa.gov.tw/TDB/public/typhoon_list/"
    driver.get(url)

    # 等待表格加載完成
    time.sleep(5)

    # 找到表格元素
    try:
        table = driver.find_element(By.ID, 'typhoon_list_table')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # 提取表格內容
        data = []
        for i, row in enumerate(rows):
            cells = row.find_elements(By.TAG_NAME, 'th' if i == 0 else 'td')
            row_data = []
            for cell in cells:
                text = cell.text.strip()
                # 處理換行符號：颱風生命期間用 ~，颱風名稱移除換行
                if i > 0:  # 跳過標題行
                    if "颱風生命期間" in row_data:  # 假設對應到特定欄位
                        text = text.replace("\n", "~")
                    elif "颱風名稱" in row_data:
                        text = text.replace("\n", " ")
                row_data.append(text)
            if row_data:
                data.append(row_data)

        # 確保數據不為空
        if not data:
            print("表格為空，請檢查網站是否有變動")
            return

        # 移除多餘空白欄位
        cleaned_data = []
        for row in data:
            if row and row[0] == '':  # 移除多餘的第一欄空白
                cleaned_data.append(row[1:])
            else:
                cleaned_data.append(row)

        # 儲存數據為 CSV
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'typhoon_data.csv')

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_data)

        print(f"資料已成功儲存到 {output_file}")

    finally:
        # 關閉瀏覽器
        driver.quit()

def fix_typhoon():
    # 檢查 CSV 是否存在
    input_file = 'data/typhoon_data.csv'
    if not os.path.exists(input_file):
        print("CSV 文件不存在，正在執行爬蟲...")
        crawl_typhoon()
        if not os.path.exists(input_file):  # 再次檢查是否已生成 CSV
            print("爬蟲執行失敗，無法修正 CSV 文件。")
            return

    # 讀取 CSV 文件並進行修改
    fixed_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                # 處理表頭，刪除空欄位標籤
                row = [col for col in row if col.strip()]
                fixed_data.append(row)
            else:
                row = [
                    col.replace('\n', '~') if idx == 3 else  # 替換「颱風生命期間」欄位的換行符號
                    col.replace('\n', '').strip() if idx == 2 else  # 移除「颱風名稱」欄位的換行和空白
                    col
                    for idx, col in enumerate(row)
                ]
                # 刪除空的欄位
                row = [col for col in row if col.strip()]
                fixed_data.append(row)

    # 將修正後的數據保存回 CSV
    with open(input_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(fixed_data)

    print(f"已成功修正格式錯誤的 CSV 文件：{input_file}")

# 如果直接執行此檔案，會執行爬蟲功能
if __name__ == "__main__":
    #crawl the typhoon data for training
    crawl_typhoon()
    fix_typhoon()
