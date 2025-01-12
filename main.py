from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
from datetime import datetime

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("菜價預測系統")
        self.resize(1000, 800)  # 窗口大小保持為 1000x800
        
        # 初始化變數
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.selected_region = "台北"
        self.selected_vegetable = "甘藍"
        
        # 全局字體
        font = QFont("Arial", 16)  # 設置全局字體大小
        
        # 建立介面元件
        layout = QVBoxLayout()
        layout.setSpacing(30)  # 元件之間的間距加大
        layout.setContentsMargins(50, 50, 50, 50)  # 設置內邊距
        
        # 日期輸入
        label_date = QLabel("請輸入今天日期 (格式: ?年?月?號):")
        label_date.setFont(font)
        layout.addWidget(label_date)
        
        self.date_entry = QLineEdit(self.today_date)
        self.date_entry.setFont(font)
        self.date_entry.setMinimumHeight(50)  # 增大高度
        layout.addWidget(self.date_entry)
        
        # 地區選單
        label_region = QLabel("選擇地區:")
        label_region.setFont(font)
        layout.addWidget(label_region)
        
        self.region_menu = QComboBox()
        self.region_menu.addItems(["台北"])
        self.region_menu.setFont(font)
        self.region_menu.setMinimumHeight(50)  # 增大高度
        layout.addWidget(self.region_menu)
        
        # 菜類選單
        label_vegetable = QLabel("選擇菜類:")
        label_vegetable.setFont(font)
        layout.addWidget(label_vegetable)
        
        self.vegetable_menu = QComboBox()
        self.vegetable_menu.addItems(["甘藍"])
        self.vegetable_menu.setFont(font)
        self.vegetable_menu.setMinimumHeight(50)  # 增大高度
        layout.addWidget(self.vegetable_menu)
        
        # 收集資訊按鈕
        self.collect_button = QPushButton("收集今日資訊")
        self.collect_button.setFont(font)
        self.collect_button.setMinimumSize(200, 60)  # 增大按鈕尺寸
        layout.addWidget(self.collect_button, alignment=Qt.AlignCenter)
        self.collect_button.clicked.connect(self.collect_info)
        
        # 預測按鈕
        self.predict_button = QPushButton("預測")
        self.predict_button.setFont(font)
        self.predict_button.setMinimumSize(200, 60)  # 增大按鈕尺寸
        layout.addWidget(self.predict_button, alignment=Qt.AlignCenter)
        self.predict_button.clicked.connect(self.predict)
        
        self.setLayout(layout)
    
    def collect_info(self):
        print("今日日期:", self.date_entry.text())
        print("選擇地區:", self.region_menu.currentText())
        print("選擇菜類:", self.vegetable_menu.currentText())
        print("已收集今日資訊！")
    
    def predict(self):
        print("進行預測...")
        print("日期:", self.date_entry.text())
        print("地區:", self.region_menu.currentText())
        print("菜類:", self.vegetable_menu.currentText())
        print("預測完成！")

def application():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# 啟動應用程式
application()

