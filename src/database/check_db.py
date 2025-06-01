import sqlite3
import os

# Đường dẫn đến file debt_simplifier.db
# check_db.py đã ở trong src/database, nên chỉ cần trỏ trực tiếp đến debt_simplifier.db
db_path = os.path.join(os.path.dirname(__file__), "debt_simplifier.db")

try:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Kiểm tra bảng datasets
        print("=== Bảng Datasets ===")
        cursor.execute("SELECT * FROM datasets")
        datasets = cursor.fetchall()
        if not datasets:
            print("Không có bộ giao dịch nào.")
        else:
            print("ID | Tên | Ngày tạo")
            print("-" * 30)
            for dataset in datasets:
                print(f"{dataset[0]} | {dataset[1]} | {dataset[2]}")

        # Kiểm tra bảng transactions
        print("\n=== Bảng Transactions ===")
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        if not transactions:
            print("Không có giao dịch nào.")
        else:
            print("ID | Dataset ID | Type | Debtor | Creditor | Amount | Borrow Date | Due Date | Interest Rate | Penalty Fee")
            print("-" * 80)
            for tx in transactions:
                print(f"{tx[0]} | {tx[1]} | {tx[2]} | {tx[3]} | {tx[4]} | {tx[5]} | {tx[6] or ''} | {tx[7] or ''} | {tx[8] or ''} | {tx[9] or ''}")

except sqlite3.Error as e:
    print(f"Lỗi khi truy xuất cơ sở dữ liệu: {e}")