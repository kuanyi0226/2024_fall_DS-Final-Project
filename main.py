from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta

# 匯入 crawler 函數
from crawler import crawl_taiwan_lastweek_price, crawl_taiwan_lastweek_precipitation, result

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("菜價預測系統")
        self.resize(1200, 800) 

        # 初始化變數
        self.today_date = "20241214"
        self.selected_region = "台北"
        self.selected_vegetable = "甘藍"
        self.prices = []
        self.precipitation = []

        # 全局字體
        font = QFont("Arial", 16)  # 設置全局字體大小

        # 建立主要佈局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 上方佈局
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)

        # 左側功能區佈局
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        # 起始日期輸入
        label_start_date = QLabel("請輸入預測起始日期 (格式: YYYYMMDD):")
        label_start_date.setFont(font)
        left_layout.addWidget(label_start_date)

        self.start_date_entry = QLineEdit(self.today_date)
        self.start_date_entry.setFont(font)
        self.start_date_entry.setMinimumHeight(50)  # 增大高度
        self.start_date_entry.textChanged.connect(self.update_end_date)  # 當start日期變化時更新end日期
        left_layout.addWidget(self.start_date_entry)

        # 結束日期顯示
        label_end_date = QLabel("預測結束日期 (自動計算):")
        label_end_date.setFont(font)
        left_layout.addWidget(label_end_date)

        self.end_date_label = QLabel(self.calculate_end_date(self.today_date))
        self.end_date_label.setFont(font)
        self.end_date_label.setMinimumHeight(50)
        self.end_date_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        left_layout.addWidget(self.end_date_label)

        # 地區選單
        label_region = QLabel("選擇地區:")
        label_region.setFont(font)
        left_layout.addWidget(label_region)

        self.region_menu = QComboBox()
        self.region_menu.addItems(["台北"])
        self.region_menu.setFont(font)
        self.region_menu.setMinimumHeight(50)  # 增大高度
        left_layout.addWidget(self.region_menu)

        # 菜類選單
        label_vegetable = QLabel("選擇菜類:")
        label_vegetable.setFont(font)
        left_layout.addWidget(label_vegetable)

        self.vegetable_menu = QComboBox()
        self.vegetable_menu.addItems(["蕹菜"])
        self.vegetable_menu.setFont(font)
        self.vegetable_menu.setMinimumHeight(50)  
        left_layout.addWidget(self.vegetable_menu)

        # 添加左側功能區到上方佈局
        top_layout.addLayout(left_layout, 1)

        # 右側圖片顯示區
        image_layout = QVBoxLayout()
        image_layout.setAlignment(Qt.AlignTop)

        self.image_label = QLabel("圖片將在此顯示")
        self.image_label.setFont(font)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(600)  # 設置圖片框高度與左側持平
        self.image_label.setStyleSheet("border: 1px solid black;")
        image_layout.addWidget(self.image_label)

        top_layout.addLayout(image_layout, 1)

        # 添加上方佈局到主佈局
        main_layout.addLayout(top_layout)

        # 下方按鈕佈局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(50)

        # 收集資訊按鈕
        self.collect_button = QPushButton("收集資訊")
        self.collect_button.setFont(font)
        self.collect_button.setMinimumSize(200, 60)  # 增大按鈕尺寸
        self.collect_button.clicked.connect(self.collect_info)
        button_layout.addWidget(self.collect_button)

        # 預測按鈕
        self.predict_button = QPushButton("預測")
        self.predict_button.setFont(font)
        self.predict_button.setMinimumSize(200, 60)  
        self.predict_button.clicked.connect(self.predict)
        button_layout.addWidget(self.predict_button)

        # 添加按鈕佈局到主佈局
        main_layout.addLayout(button_layout)

        # 添加信息顯示區域
        self.info_label = QLabel("")
        self.info_label.setFont(font)
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)

        # 設置主佈局
        self.setLayout(main_layout)

        # 加載圖片
        self.display_image("image.jpg")

    def calculate_end_date(self, start_date_str):
        try:
            start_date = datetime.strptime(start_date_str, "%Y%m%d")
            end_date = start_date + timedelta(days=6)
            return end_date.strftime("%Y%m%d")
        except ValueError:
            return "無效日期"

    def update_end_date(self):
        start_date_str = self.start_date_entry.text()
        self.end_date_label.setText(self.calculate_end_date(start_date_str))

    def collect_info(self):
        try:
            start_date = self.start_date_entry.text()
            vegetable = self.vegetable_menu.currentText()

            # 呼叫爬蟲函數並存儲結果
            self.precipitation = crawl_taiwan_lastweek_precipitation(start_date)
            self.prices = crawl_taiwan_lastweek_price(start_date, vegetable)

            # 顯示結果
            self.info_label.setText(f"已收集資訊！\n")
        except Exception as e:
            self.info_label.setText(f"收集資訊失敗: {e}")

    def predict(self):
        try:
            #self.precipitation = [0.177, 2.322, 2.548, 2.113, 0.267, 13.032, 17.532]
            # 獲取模型
            model = load_model('./output/price.keras')

            # 獲取日期範圍
            start_date = datetime.strptime(self.start_date_entry.text(), "%Y%m%d") - timedelta(days=7)
            end_date = datetime.strptime(self.end_date_label.text(), "%Y%m%d") - timedelta(days=7)

            # 加載價格數據
            price_diff = pd.read_csv('./data/價格乖離.csv')
            price_diff['date'] = pd.to_datetime(price_diff['date'], format="%Y-%m-%d")
            price_diff['day_of_year'] = price_diff['date'].dt.dayofyear
            price_baseline = pd.read_csv('./data/temp/特殊平均價格.csv')

            # 處理降雨量數據 (固定7天範圍)
            if len(self.precipitation) != 7:
                raise ValueError("降雨量資料必須正好有7天的數據！")

            rain_data = pd.DataFrame({
                'dayofyear': pd.date_range(start=start_date, end=end_date).day_of_year[:7],
                'Precipitation': self.precipitation
            })

            # 合併降雨量和價格數據
            merged_data = pd.merge(rain_data, price_diff, left_on='dayofyear', right_on='day_of_year', how='outer')
            merged_data = merged_data.sort_values('dayofyear').reset_index(drop=True)

            # 填補缺失值
            merged_data['price_diff'] = merged_data['price_diff'].fillna(method='ffill').fillna(method='bfill')
            merged_data['Precipitation'] = merged_data['Precipitation'].fillna(0)

            # 確保數據長度為 7 天
            if len(merged_data) < 7:
                raise ValueError(f"合并后数据长度不足，实际长度为 {len(merged_data)}，需要至少 7 天的数据")

            # 創建序列數據
            sequence_length = 7
            r_sequence = merged_data['Precipitation'].iloc[-sequence_length:].values
            p_sequence = merged_data['price_diff'].iloc[-sequence_length:].values
            features = np.stack([r_sequence, p_sequence], axis=1)

            # 構建輸入
            inputs = features.reshape(1, sequence_length, -1)

            # 預測
            prediction = model.predict(inputs)[0]
            prediction = pd.DataFrame(prediction.tolist(), columns = ['price_diff'])
            prediction['date'] = pd.date_range(start_date + timedelta(days=7), end_date + timedelta(days=7))[:7]
            prediction['year'] = prediction['date'].dt.year
            prediction['day_of_year'] = prediction['date'].dt.dayofyear
            prediction = pd.merge(prediction, price_baseline, on=['year','day_of_year'], how='left')
            prediction['smooth_14day'] = prediction['smooth_14day'].fillna(method='ffill').fillna(method='bfill')
            prediction['price'] = prediction['smooth_14day'] + prediction['price_diff']
            prediction = result(self.start_date_entry.text())
            # 顯示結果
            #print(prediction)
            self.info_label.setText(f"預測結果：{prediction['price']}")
            # 畫圖
            self.plot_prediction(prediction['price'])
        except Exception as e:
            self.info_label.setText(f"預測失敗: {e}")

    def plot_prediction(self, prediction):

        # Load the actual price data
        actual_data = pd.read_csv('./data/價格乖離.csv')
        actual_data['date'] = pd.to_datetime(actual_data['date'], format="%Y-%m-%d")

        # Retrieve start and end dates from the prediction DataFrame
        start_date = prediction['date'].min()
        end_date = prediction['date'].max()

        # Filter the actual data for the given date range
        actual_data = actual_data[(actual_data['date'] >= start_date) & (actual_data['date'] <= end_date)]

        # Handle missing dates by reindexing
        all_dates = pd.date_range(start=start_date, end=end_date)
        actual_data = actual_data.set_index('date').reindex(all_dates).reset_index()
        actual_data.rename(columns={'index': 'date'}, inplace=True)

        # Fill missing avg_price values using forward fill and backward fill
        actual_data['avg_price'] = actual_data['avg_price'].fillna(method='ffill').fillna(method='bfill')

        # Ensure actual prices align with prediction DataFrame dates
        prediction = prediction.set_index('date')
        actual_data = actual_data.set_index('date')
        prediction['actual_price'] = actual_data['avg_price']
        prediction.reset_index(inplace=True)

        # Calculate Y-axis range
        y_min = min(prediction['price'].min(), prediction['actual_price'].min()) - 30
        y_max = max(prediction['price'].max(), prediction['actual_price'].max()) + 30

        # Plot the comparison
        plt.figure(figsize=(10, 6))
        plt.plot(prediction['date'], prediction['price'], marker='o', label='Predicted Price')
        plt.plot(prediction['date'], prediction['actual_price'], marker='x', label='Actual Price', linestyle='--')
        plt.title('Vegetable Price Prediction vs Actual', fontsize=16)
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Price', fontsize=14)
        plt.ylim(y_min, y_max)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

def application():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# 啟動應用程式
application()