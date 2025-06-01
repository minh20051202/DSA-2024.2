"""
Điểm khởi đầu chính cho ứng dụng Thuật Toán Đơn Giản Hóa Nợ

Script này khởi chạy giao diện đồ họa để quản lý và đơn giản hóa các khoản nợ.
"""

import sys
import os
import tkinter as tk
from src.ui.gui import DebtSimplifierGUI
# Thêm thư mục dự án vào đường dẫn
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Hàm chính để chạy ứng dụng giao diện đồ họa Đơn Giản Hóa Nợ"""
    # Tạo cửa sổ gốc
    root = tk.Tk()
    # Thử đặt biểu tượng nếu có sẵn
    root.title("Debt Simplification Algorithm")
    try:
        if os.path.exists("icon.ico"):
            root.iconbitmap("icon.ico")
    except Exception:
        pass  # Bỏ qua lỗi biểu tượng
    # Khởi tạo ứng dụng
    app = DebtSimplifierGUI(root)
    # Bắt đầu vòng lặp sự kiện chính
    root.mainloop()
    sys.exit(1)

if __name__ == "__main__":
    main() 