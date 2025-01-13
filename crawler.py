from datetime import datetime, timedelta
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, JavascriptException
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

def crawl_taipei_temp(start_year, end_year):
    # 設定 Selenium 的 WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 啟動無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        # 打開目標網站
        try:
            url = "https://codis.cwa.gov.tw/StationData"
            driver.get(url)
            print("成功進入網站")
        except Exception as e:
            print(f"無法打開網站：{e}")
            driver.save_screenshot("error_open_website.png")
            return

        # 輸入站名並選擇
        try:
            input_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[list="station_name"]'))
            )
            input_box.send_keys("臺北 (466920)")  # 輸入站名
            time.sleep(2)  # 等待下拉選單顯示
            input_box.send_keys(Keys.RETURN)  # 模擬回車鍵選擇站名
            print("成功輸入站名並選擇")
        except TimeoutException:
            print("無法加載站名站號輸入框")
            driver.save_screenshot("error_input_box.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        # 點擊地圖上的紅色標籤
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "leaflet-marker-icon"))
            )
            driver.find_element(By.CLASS_NAME, "leaflet-marker-icon").click()
            print("成功點擊地圖上的紅色標籤")
        except TimeoutException:
            print("無法點擊地圖上的紅色標籤")
            driver.save_screenshot("error_map_marker.png")
            return

        # 點擊 "資料圖表展示"
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.show_stn_tool"))
            )
            driver.find_element(By.CSS_SELECTOR, "button.show_stn_tool").click()
            print("成功點擊 '資料圖表展示'")
        except TimeoutException:
            print("無法點擊 '資料圖表展示'")
            driver.save_screenshot("error_data_display.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return


        # 點擊 "單項逐日年報表"
        try:
            # 確保按鈕可見並可點擊
            daily_report_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'單項逐日年報表')]"))
            )
            daily_report_button.click()
            print("成功點擊 '單項逐日年報表'")
        except TimeoutException:
            print("無法點擊 '單項逐日年報表'")
            driver.save_screenshot("error_daily_report.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        try:
            # 等待觀測要素下拉選單加載
            element_dropdown = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-control"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element_dropdown)  # 滾動到元素可見
            time.sleep(1)  # 等待滾動完成

            # 使用 JavaScript 選擇目標選項
            driver.execute_script("""
                let select = arguments[0];
                Array.from(select.options).forEach(option => {
                    if (option.text.includes('最低氣溫(℃)')) {
                        option.selected = true; // 選擇正確選項
                        select.dispatchEvent(new Event('change')); // 觸發改變事件
                    }
                });
            """, element_dropdown)

            # 驗證選擇是否成功
            selected_option = driver.execute_script("""
                let select = arguments[0];
                return select.options[select.selectedIndex].text; // 獲取當前選中的選項文字
            """, element_dropdown)

            if '最低氣溫(℃)' in selected_option:
                print(f"成功選擇 '最低氣溫(℃) / 最低氣溫時間(LST)' -> {selected_option}")
            else:
                raise Exception(f"選擇失敗，當前選項為: {selected_option}")

        except Exception as e:
            print(f"無法選擇觀測要素: {e}")
        finally:
            # 無論成功或失敗都截圖
            screenshot_file = "select_element_status.png"
            driver.save_screenshot(screenshot_file)
            print(f"觀測要素選擇狀態截圖已保存: {screenshot_file}")


        # 創建 CSV 文件保存數據
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'taipei_temp_2015_2024.csv')

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "Date", "Lowest Temperature (℃)", "Time (LST)"])

            # 逐年爬取數據
            for year in range(start_year, end_year + 1):
                try:
                    # 選擇年份
                    year_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input.vdatetime-input"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", year_input)  # 滾動到元素可見
                    year_input.clear()
                    year_input.send_keys(str(year))
                    year_input.send_keys(Keys.RETURN)
                    time.sleep(2)  # 等待表格刷新
                    print(f"成功選擇年份 {year}")

                    # 提取表格數據
                    table = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
                    )
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    # 檢查表格是否有數據
                    if len(rows) <= 1:  # 只有表頭，沒有數據
                        print(f"年份 {year} 無數據")
                        continue

                    for row in rows[1:]:  # 跳過表頭
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            date = cells[0].text.strip()  # 日期
                            temp_data = cells[1].text.strip().split("/")
                            if len(temp_data) == 2:
                                lowest_temp = temp_data[0].strip()  # 最低氣溫
                                time_lst = temp_data[1].strip()  # 最低氣溫時間
                                writer.writerow([year, date, lowest_temp, time_lst])
                    print(f"成功爬取年份 {year} 的數據")
                except TimeoutException as e:
                    print(f"無法提取年份 {year} 的數據: {e}")
                    driver.save_screenshot(f"error_year_{year}.png")
                    continue

        print(f"資料已成功儲存到 {output_file}")

    finally:
        # 關閉瀏覽器
        driver.quit()

def crawl_taipei_precipitation(start_year, end_year):
    # 設定 Selenium 的 WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 啟動無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        # 打開目標網站
        try:
            url = "https://codis.cwa.gov.tw/StationData"
            driver.get(url)
            print("成功進入網站")
        except Exception as e:
            print(f"無法打開網站：{e}")
            driver.save_screenshot("error_open_website.png")
            return

        # 輸入站名並選擇
        try:
            input_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[list="station_name"]'))
            )
            input_box.send_keys("臺北 (466920)")  # 輸入站名
            time.sleep(2)  # 等待下拉選單顯示
            input_box.send_keys(Keys.RETURN)  # 模擬回車鍵選擇站名
            print("成功輸入站名並選擇")
        except TimeoutException:
            print("無法加載站名站號輸入框")
            driver.save_screenshot("error_input_box.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        # 點擊地圖上的紅色標籤
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "leaflet-marker-icon"))
            )
            driver.find_element(By.CLASS_NAME, "leaflet-marker-icon").click()
            print("成功點擊地圖上的紅色標籤")
        except TimeoutException:
            print("無法點擊地圖上的紅色標籤")
            driver.save_screenshot("error_map_marker.png")
            return

        # 點擊 "資料圖表展示"
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.show_stn_tool"))
            )
            driver.find_element(By.CSS_SELECTOR, "button.show_stn_tool").click()
            print("成功點擊 '資料圖表展示'")
        except TimeoutException:
            print("無法點擊 '資料圖表展示'")
            driver.save_screenshot("error_data_display.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return


        # 點擊 "單項逐日年報表"
        try:
            # 確保按鈕可見並可點擊
            daily_report_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'單項逐日年報表')]"))
            )
            daily_report_button.click()
            print("成功點擊 '單項逐日年報表'")
        except TimeoutException:
            print("無法點擊 '單項逐日年報表'")
            driver.save_screenshot("error_daily_report.png")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return

        try:
            # 等待觀測要素下拉選單加載
            element_dropdown = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.form-control"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element_dropdown)  # 滾動到元素可見
            time.sleep(1)  # 等待滾動完成

            # 使用 JavaScript 選擇目標選項
            driver.execute_script("""
                let select = arguments[0];
                Array.from(select.options).forEach(option => {
                    if (option.text.includes('降水量(mm)')) {
                        option.selected = true; // 選擇正確選項
                        select.dispatchEvent(new Event('change')); // 觸發改變事件
                    }
                });
            """, element_dropdown)

            # 驗證選擇是否成功
            selected_option = driver.execute_script("""
                let select = arguments[0];
                return select.options[select.selectedIndex].text; // 獲取當前選中的選項文字
            """, element_dropdown)

            if '降水量(mm)' in selected_option:
                print(f"成功選擇 '降水量(mm)' -> {selected_option}")
            else:
                raise Exception(f"選擇失敗，當前選項為: {selected_option}")

        except Exception as e:
            print(f"無法選擇觀測要素: {e}")
        finally:
            # 無論成功或失敗都截圖
            screenshot_file = "select_element_status.png"
            driver.save_screenshot(screenshot_file)
            print(f"觀測要素選擇狀態截圖已保存: {screenshot_file}")


        # 創建 CSV 文件保存數據
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'taipei_temp_2015_2024.csv')

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "Date", "Precipitation(mm)"])

            # 逐年爬取數據
            for year in range(start_year, end_year + 1):
                try:
                    # 選擇年份
                    year_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input.vdatetime-input"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", year_input)  # 滾動到元素可見
                    year_input.clear()
                    year_input.send_keys(str(year))
                    year_input.send_keys(Keys.RETURN)
                    time.sleep(2)  # 等待表格刷新
                    print(f"成功選擇年份 {year}")

                    # 提取表格數據
                    table = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
                    )
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    # 檢查表格是否有數據
                    if len(rows) <= 1:  # 只有表頭，沒有數據
                        print(f"年份 {year} 無數據")
                        continue

                    for row in rows[1:]:  # 跳過表頭
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            date = cells[0].text.strip()  # 日期
                            temp_data = cells[1].text.strip().split("/")
                            if len(temp_data) == 2:
                                lowest_temp = temp_data[0].strip()  
                                time_lst = temp_data[1].strip()  
                                writer.writerow([year, date, lowest_temp, time_lst])
                    print(f"成功爬取年份 {year} 的數據")
                except TimeoutException as e:
                    print(f"無法提取年份 {year} 的數據: {e}")
                    driver.save_screenshot(f"error_year_{year}.png")
                    continue

        print(f"資料已成功儲存到 {output_file}")
    
    finally:
        # 關閉瀏覽器
        driver.quit()

def crawl_taiwan_lastweek_precipitation(date):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        # 打開目標網站
        url = "https://www.cwa.gov.tw/V8/C/D/DailyPrecipitation.html"
        driver.get(url)
        print("成功打開網站")

        # 定義排除的測站 ID
        exclude_stations = {"467620", "467990", "467110", "467350", "467300"}
        all_data = []  # 用於存儲所有測站的數據矩陣
        days_to_extract = 7  # 提取的天數

        # 計算目標日期範圍
        target_dates = []
        for i in range(days_to_extract):
            target_date = datetime.strptime(date, "%Y%m%d") - timedelta(days=i + 1)
            target_dates.append((target_date.year, target_date.month, target_date.day))

        # 獲取所有測站選單中的選項
        try:
            station_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "SID"))
            )
            station_options = Select(station_dropdown).options
        except Exception as e:
            print(f"無法獲取測站選單: {e}")
            driver.save_screenshot("station_dropdown_error.png")
            return

        for station_option in station_options:
            station_id = station_option.get_attribute("value")
            station_name = station_option.text

            if station_id in exclude_stations:
                print(f"跳過外島測站: {station_name} ({station_id})")
                continue

            try:
                # 選擇測站
                Select(station_dropdown).select_by_value(station_id)
                print(f"成功選擇測站: {station_name} ({station_id})")
                time.sleep(0.1)  # 等待測站數據加載

                # 確保年份選單可見並選擇年份
                try:
                    year_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "Year"))
                    )
                    target_year = int(date[:4])
                    Select(year_dropdown).select_by_visible_text(str(target_year))
                    print(f"成功選擇年份: {target_year}")
                    time.sleep(2)  # 等待年份數據加載
                except Exception as e:
                    print(f"無法選擇年份: {e}")
                    driver.save_screenshot("year_selection_error.png")
                    continue

                # 提取表格數據
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "table-striped"))
                )
                rows = table.find_elements(By.TAG_NAME, "tr")[1:-1]  # 排除表頭和總和值行
                station_data = []

                for year, month, day in target_dates:
                    try:
                        column_index = month  # 月份對應的列
                        row_index = day - 1  # 日期對應的行 (0-based)

                        # 確保行和列存在
                        if row_index >= len(rows):
                            print(f"日期 {day} 超出範圍，跳過。")
                            station_data.append(-1)
                            continue

                        row = rows[row_index]
                        cells = row.find_elements(By.TAG_NAME, "td")

                        if column_index - 1 >= len(cells):
                            print(f"月份 {month} 超出範圍，跳過。")
                            station_data.append(-1)
                            continue

                        # 提取單元格數據
                        cell = cells[column_index - 1]
                        text = cell.text.strip()

                        if text == "-":
                            station_data.append(0)
                        elif text == "T":
                            station_data.append(0)
                        elif text == "X":
                            station_data.append(-1)
                        else:
                            try:
                                station_data.append(float(text))
                            except ValueError:
                                station_data.append(-1)

                    except Exception as e:
                        print(f"提取日期 {year}-{month}-{day} 數據失敗: {e}")
                        station_data.append(-1)

                # 驗證提取的數據是否完整
                if len(station_data) != days_to_extract:
                    print(f"測站 {station_name} 數據不完整，跳過。")
                    continue

                all_data.append(station_data)
                print(f"成功提取測站 {station_name} 的數據。")
                print(f"測站 {station_name} 在目標 7 天的降水量: {station_data}")

            except Exception as e:
                print(f"提取測站 {station_name} 數據失敗: {e}")
                driver.save_screenshot(f"{station_name}_error.png")
                continue

        # 計算每一天的平均降水量（排除值為 -1 的數據）
        average_precipitation = []
        for day_index in range(days_to_extract):
            daily_values = [station[day_index] for station in all_data if station[day_index] != -1]
            if daily_values:
                day_average = sum(daily_values) / len(daily_values)
            else:
                day_average = 0
            average_precipitation.append(day_average)

        print("成功計算每一天的平均降水量")
        #print(average_precipitation)
        return average_precipitation[::-1]#invert，變回順向日期 

    finally:
        driver.quit()


if __name__ == "__main__":
    #crawl the typhoon data for training
    #crawl_typhoon()
    #fix_typhoon()
    #crawl_taipei_temp(2015,2024)
    #crawl_taipei_precipitation(2015,2024)

    # result = crawl_taiwan_lastweek_precipitation("20240108")
    # print(result)
    print('crawler done')
