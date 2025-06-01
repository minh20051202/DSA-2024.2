# DSA-2024.2 Final Project - Hệ thống đơn giản hóa nợ(Tối ưu dòng tiền)

### Tổng Quan

Hệ thống đơn giản hóa nợ toàn diện triển khai các khái niệm Cấu trúc Dữ liệu và Giải thuật nâng cao. Hệ thống cung cấp giao diện đồ họa để quản lý và tối ưu hóa việc thanh toán nợ trong nhóm.

### Cấu Trúc Dự Án

```
.
├── src/
│   ├── algorithms/
│   │   ├── basic_transactions/     # Thuật toán thanh toán nợ cơ bản
│   │   └── advanced_transactions/  # Thuật toán nâng cao với tính năng tài chính
│   ├── core_types/                # Các mô hình dữ liệu cốt lõi
│   ├── data_structures/           # Triển khai CTDL tùy chỉnh
│   ├── database/                  # Lưu trữ dữ liệu
│   ├── ui/                        # Triển khai giao diện đồ họa
│   └── utils/                     # Các hàm tiện ích
├── tests/                         # Bộ kiểm thử
└── benchmarks/                    # Đánh giá hiệu năng
```

### Tính Năng

1. **Nhiều Thuật Toán**

   - Giao Dịch Cơ Bản:
     - Thuật toán Tham lam
     - Quy hoạch Động
     - Phát hiện Chu trình
     - Min-Cost Max-Flow
   - Giao Dịch Nâng Cao:
     - Hỗ trợ Lãi suất
     - Quản lý Ngày đến hạn
     - Tính toán Phí phạt

2. **Cấu Trúc Dữ Liệu Tùy Chỉnh**

   - Mảng
   - Danh sách Liên kết
   - Bảng Băm
   - Đồ thị
   - Hàng đợi Ưu tiên
   - Tuple

3. **Giao Diện Người Dùng**

   - Giao diện Tkinter hiện đại
   - Quản lý Giao dịch
   - Hiển thị Kết quả
   - Hiển thị Dữ liệu dạng Bảng

4. **Quản Lý Dữ Liệu**
   - Lưu trữ Cơ sở dữ liệu SQLite
   - Quản lý Bộ Giao dịch
   - Nhập/Xuất Dữ liệu

### Yêu Cầu

- Python ≥ 3.6
- tk ≥ 0.1.0
- tabulate ≥ 0.9.0

### Cài Đặt

```bash
# Sao chép kho mã nguồn
git clone https://github.com/minh20051202/DSA-2024.2
cd DSA-2024.2

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### Sử Dụng

```bash
# Chạy ứng dụng GUI
python main.py

# Hoặc chạy(nếu dùng Linux/Ubuntu/WSL2)
python3 main.py
```

### Phát Triển

```bash
# Chạy kiểm thử
python -m pytest tests/

# Chạy kiểm thử một thuật toán
python -m unittest tests/basic_transactions/test_greedy.py

# Chạy đánh giá hiệu năng
python -m pytest benchmarks/
```
