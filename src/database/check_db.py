import sqlite3

# Đường dẫn đến file database (sử dụng raw string)
db_path = r"C:\Users\Admin\Desktop\2024.2\GTS\Baitap\DSA-2024.2-main\src\database\debt_simplifier.db"

try:
    # Kết nối đến database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lấy dữ liệu từ bảng giao_dich
    cursor.execute("SELECT nguoi_no, chu_no, so_tien FROM giao_dich")
    giao_dich_data = cursor.fetchall()
    print("Dữ liệu từ bảng giao_dich (Giao dịch gốc):")
    if giao_dich_data:
        for row in giao_dich_data:
            print(f"Người nợ: {row[0]}, Chủ nợ: {row[1]}, Số tiền: {row[2]}")
    else:
        print("Không có dữ liệu trong bảng giao_dich.")

    # Lấy dữ liệu từ bảng giao_dich_toi_uu
    cursor.execute("SELECT nguoi_no, chu_no, so_tien, phuong_phap FROM giao_dich_toi_uu")
    giao_dich_toi_uu_data = cursor.fetchall()
    print("\nDữ liệu từ bảng giao_dich_toi_uu (Giao dịch đã tối ưu):")
    if giao_dich_toi_uu_data:
        for row in giao_dich_toi_uu_data:
            print(f"Người nợ: {row[0]}, Chủ nợ: {row[1]}, Số tiền: {row[2]}, Phương pháp: {row[3]}")
    else:
        print("Không có dữ liệu trong bảng giao_dich_toi_uu.")

except sqlite3.Error as e:
    print(f"Lỗi khi kết nối hoặc truy vấn database: {e}")

finally:
    # Đóng kết nối
    if conn:
        conn.close()
        print("Đã đóng kết nối database.")