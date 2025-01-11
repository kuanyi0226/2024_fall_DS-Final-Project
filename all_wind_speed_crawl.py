import requests
import json
import os

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
