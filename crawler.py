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

import requests
import json
import os
def crawl_all_wind_speed(): #path我先暫時不改，還不太確定程式狀況
    # 測站清單
    station_codes = [
        "460010",
        "467060",
        "467080",
        "466990",
        "467540",
        "467610",
        "467620",
        "467660",
        "460020",
        "467530",
        "467480",
        "467490",
        "467770",
        "467550",
        "467650",
        "466850",
        "466880",
        "466900",
        "466910",
        "466920",
        "467570",
        "467571",
        "467110",
        "467300",
        "467350",
        "467990",
        "467410",
        "467411"
    ]

    # 請求 URL 和通用標頭
    url = "https://rdc28.cwa.gov.tw/TDB/public/wind_gust_statistics/search"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "DNT": "1",
        "Origin": "https://rdc28.cwa.gov.tw",
        "Referer": "https://rdc28.cwa.gov.tw/TDB/public/wind_gust_statistics/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    # 結果儲存資料夾
    output_dir = "station_data"
    os.makedirs(output_dir, exist_ok=True)

    # 迴圈請求每個測站的數據
    for station_code in station_codes:
        print(f"正在請求測站 {station_code} 的資料...")
        data = {
            "search_type": "DY",
            "wind_type[]": ["WSMax", "WSGust"],
            "WSMax_value": "0",
            "WSMax_value_ms": "5",
            "WSGust_value": "0",
            "WSGust_value_ms": "0",
            "radio_typhoon_year": "only_year",
            "accu_start_time": "1958",
            "accu_end_year": "2025",
            "measure_type": "CWA",
            "stno": station_code,
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # 如果有錯誤，觸發異常
            result = response.json()

            # 儲存為 JSON 檔案
            output_file = os.path.join(output_dir, f"{station_code}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"測站 {station_code} 的資料已保存到 {output_file}")
        except Exception as e:
            print(f"測站 {station_code} 的資料請求失敗：{e}")


    all_data = []

    for station_code in station_codes:
        print(f"正在請求測站 {station_code} 的資料...")
        data = {
            "search_type": "DY",
            "wind_type[]": ["WSMax", "WSGust"],
            "WSMax_value": "0",
            "WSMax_value_ms": "5",
            "WSGust_value": "0",
            "WSGust_value_ms": "0",
            "radio_typhoon_year": "only_year",
            "accu_start_time": "1958",
            "accu_end_year": "2025",
            "measure_type": "CWA",
            "stno": station_code,
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            all_data.extend(result)  # 合併數據
            print(f"測站 {station_code} 的資料已成功加入")
        except Exception as e:
            print(f"測站 {station_code} 的資料請求失敗：{e}")

    # 將合併數據保存為單個 JSON
    output_file = "all_stations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print(f"所有測站的資料已合併並保存到 {output_file}")


def crawl_all_rainfall(): #path我先暫時不改，還不太確定程式狀況
    import requests
    import json
    import os

    # 測站清單（可以自行擴展）
    station_codes = [
        "460010",
        "467060",
        "467080",
        "466990",
        "467540",
        "467610",
        "467620",
        "467660",
        "460020",
        "467530",
        "467480",
        "467490",
        "467770",
        "467550",
        "467650",
        "466850",
        "466880",
        "466900",
        "466910",
        "466920",
        "467570",
        "467571",
        "467110",
        "467300",
        "467350",
        "467990",
        "467410",
        "467411"
    ]

    # 請求 URL 和通用標頭
    url = "https://rdc28.cwa.gov.tw/TDB/public/precipitation_statistics/search"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "DNT": "1",
        "Origin": "https://rdc28.cwa.gov.tw",
        "Referer": "https://rdc28.cwa.gov.tw/TDB/public/precipitation_statistics/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    # 結果儲存資料夾
    output_dir = "rainfall_data"
    os.makedirs(output_dir, exist_ok=True)

    # 迴圈請求每個測站的數據
    for station_code in station_codes:
        print(f"正在請求測站 {station_code} 的雨量資料...")
        data = {
            "rain_average": "precp_accu_warning",
            "accu_value": "0.1",
            "radio_typhoon_year": "only_year",
            "accu_start_time": "1958",
            "accu_end_year": "2025",
            "measure_type": "CWA",
            "stno": station_code,
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # 如果有錯誤，觸發異常
            result = response.json()

            # 儲存為 JSON 檔案
            output_file = os.path.join(output_dir, f"{station_code}_rainfall.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"測站 {station_code} 的雨量資料已保存到 {output_file}")
        except Exception as e:
            print(f"測站 {station_code} 的雨量資料請求失敗：{e}")


    all_data = []

    for station_code in station_codes:
        print(f"正在請求測站 {station_code} 的雨量資料...")
        data = {
            "rain_average": "precp_accu_warning",
            "accu_value": "0.1",
            "radio_typhoon_year": "only_year",
            "accu_start_time": "1958",
            "accu_end_year": "2025",
            "measure_type": "CWA",
            "stno": station_code,
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            all_data.extend(result)  # 合併數據
            print(f"測站 {station_code} 的雨量資料已成功加入")
        except Exception as e:
            print(f"測站 {station_code} 的雨量資料請求失敗：{e}")

    # 儲存合併數據為單個 JSON 檔案
    output_file = "all_rainfall_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print(f"所有測站的雨量資料已合併並保存到 {output_file}")


# 如果直接執行此檔案，會執行爬蟲功能
if __name__ == "__main__":
    #crawl the typhoon data for training
    crawl_typhoon()
    fix_typhoon()
