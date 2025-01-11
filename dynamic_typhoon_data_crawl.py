import requests
import json

# 請求 URL
url = "https://rdc28.cwa.gov.tw/TDB/public/wind_gust_statistics/search"

# 請求標頭
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

# POST 數據
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
    "stno": "466990",
}

# 發送 POST 請求
response = requests.post(url, headers=headers, data=data)

# 確認請求成功
if response.status_code == 200:
    print("請求成功，正在儲存 JSON 檔案...")
    
    # 將結果轉換為 JSON 格式
    result = response.json()
    
    # 儲存為本地 JSON 檔案
    output_file = "typhoon_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"數據已儲存到 {output_file}")
else:
    print(f"請求失敗，狀態碼：{response.status_code}")
