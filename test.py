import pandas as pd

# 讀取 CSV 檔案
file_path = 'output.csv'
df = pd.read_csv(file_path)

# 確保 '日期' 欄位為日期格式
df['日期'] = pd.to_datetime(df['日期'])

# 將日期設為索引，方便補全缺失日期
df = df.set_index('日期')

# 重新建立日期範圍，包含所有缺失的日期
all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
df = df.reindex(all_dates)

# 重命名索引
df.index.name = '日期'

# 使用線性內插法補全缺失值
df['預測價'] = df['預測價'].interpolate(method='linear')

# 如果仍有缺失值，可以選擇填補為前一筆數值或零
df['預測價'] = df['預測價'].fillna(method='bfill').fillna(method='ffill')

# 將結果存回 CSV
output_path = 'output_filled.csv'
df.to_csv(output_path, encoding='utf-8-sig')

print(f"補全後的資料已儲存至 {output_path}")
