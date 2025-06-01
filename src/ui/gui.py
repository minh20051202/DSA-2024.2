import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from collections import defaultdict
import sqlite3
import os
import sys
from src.utils.financial_calculator import InterestType, PenaltyType

# Thêm đường dẫn để Python nhận diện thư mục src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import các core types và cấu trúc dữ liệu
from src.core_type.transaction import BasicTransaction, AdvancedTransaction
from src.data_structures.linked_list import LinkedList

# Import các thuật toán
try:
    from src.algorithms.basic_transactions.greedy import GreedySimplifier
    from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier
    from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier
    from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier
    from src.algorithms.advanced_transactions.greedy import AdvancedGreedySimplifier
    from src.algorithms.advanced_transactions.dynamic_programming import AdvancedDynamicProgrammingSimplifier
    from src.algorithms.advanced_transactions.cycle_detector import AdvancedDebtCycleSimplifier
    from src.algorithms.advanced_transactions.min_cost_max_flow import AdvancedMinCostMaxFlowSimplifier
except ImportError as e:
    print(f"Lỗi import thuật toán: {e}")
    raise

class DebtSimplifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Đơn giản hóa giao dịch")
        self.root.geometry("1800x950")
        self.root.minsize(1500, 850)
        self.transactions = LinkedList()
        self.mode_var = tk.StringVar(value="Cơ bản")
        self.algorithm_var = tk.StringVar(value="Greedy")
        self.dataset_name_var = tk.StringVar()
        self.current_dataset_id = None
        self.save_changes_button = None
        
        self.interest_mapping = {
            "Lãi đơn": InterestType.SIMPLE,
            "Lãi kép ngày": InterestType.COMPOUND_DAILY,
            "Lãi kép tháng": InterestType.COMPOUND_MONTHLY,
            "Lãi kép năm": InterestType.COMPOUND_YEARLY
        }
        self.reverse_interest_mapping = {v: k for k, v in self.interest_mapping.items()}

        self.penalty_mapping = {
            "Phạt cố định": PenaltyType.FIXED,
            "Phạt theo ngày": PenaltyType.DAILY,
            "Phạt % gốc": PenaltyType.PERCENTAGE
        }
        self.reverse_penalty_mapping = {v: k for k, v in self.penalty_mapping.items()}

        # --- Cấu hình cột cho Treeview ---
        self.core_columns_config = {
            "STT": {"text": "STT", "width": 50, "anchor": tk.CENTER, "minwidth": 50},
            "Người nợ": {"text": "Người nợ", "width": 120, "anchor": tk.W, "minwidth": 110},
            "Người cho vay": {"text": "Người cho vay", "width": 120, "anchor": tk.W, "minwidth": 110},
            "Số tiền": {"text": "Số tiền", "width": 100, "anchor": tk.E, "minwidth": 90},
        }
        self.advanced_only_extra_columns_config = {
            "Ngày vay": {"text": "Ngày vay", "width": 100, "anchor": tk.W, "minwidth": 90},
            "Ngày đến hạn": {"text": "Ngày đến hạn", "width": 100, "anchor": tk.W, "minwidth": 90},
            "Lãi suất (%)": {"text": "Lãi suất (%)", "width": 90, "anchor": tk.W, "minwidth": 80}, # Đổi tên hiển thị
            "Kiểu lãi": {"text": "Kiểu lãi", "width": 110, "anchor": tk.W, "minwidth": 100},       # CỘT MỚI
            "Phí phạt": {"text": "Phí phạt (%)", "width": 90, "anchor": tk.W, "minwidth": 80},
            "Kiểu phạt": {"text": "Kiểu phạt", "width": 110, "anchor": tk.W, "minwidth": 100}      # CỘT MỚI
        }
        self.type_column_config = {
            "Loại GD": {"text": "Loại GD", "width": 80, "anchor": tk.W, "minwidth": 70}
        }
        # Cập nhật thứ tự các cột
        self.all_treeview_columns_ordered = list(self.core_columns_config.keys()) + \
                                            list(self.advanced_only_extra_columns_config.keys()) + \
                                            list(self.type_column_config.keys())

        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.db_dir = os.path.join(self.base_dir, "..", "database")
        self.db_path = os.path.join(self.db_dir, "debt_simplifier.db")
        os.makedirs(self.db_dir, exist_ok=True)
        self.setup_database()
        self.setup_gui()

    def setup_database(self):
        """Khởi tạo cơ sở dữ liệu SQLite và các bảng cần thiết."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS datasets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_id INTEGER NOT NULL,
                        type TEXT NOT NULL, -- 'basic' or 'advanced'
                        debtor TEXT NOT NULL,
                        creditor TEXT NOT NULL,
                        amount REAL NOT NULL,
                        borrow_date TEXT,      -- YYYY-MM-DD
                        due_date TEXT,         -- YYYY-MM-DD
                        interest_rate REAL,    -- Dưới dạng thập phân, vd: 0.05 cho 5%
                        penalty_fee REAL,      -- Giá trị phí phạt
                        interest_type_name TEXT, -- Tên của enum, vd: 'SIMPLE', 'COMPOUND_DAILY'
                        penalty_type_name TEXT,  -- Tên của enum, vd: 'FIXED', 'PERCENTAGE'
                        FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                    )
                ''')
                # Kiểm tra và thêm cột nếu chưa có (cho các DB cũ)
                self.add_column_if_not_exists(cursor, "transactions", "interest_type_name", "TEXT")
                self.add_column_if_not_exists(cursor, "transactions", "penalty_type_name", "TEXT")

                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo cơ sở dữ liệu: {e}")

    def add_column_if_not_exists(self, cursor, table_name, column_name, column_type):
        """Hàm tiện ích để thêm cột vào bảng nếu cột đó chưa tồn tại."""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        if column_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                print(f"Đã thêm cột '{column_name}' vào bảng '{table_name}'.")
            except sqlite3.Error as e:
                print(f"Lỗi khi thêm cột '{column_name}': {e}")

    def setup_gui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Khung chọn chế độ
        mode_frame = ttk.LabelFrame(main_frame, text="Chọn chế độ", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(mode_frame, text="Cơ bản", variable=self.mode_var, value="Cơ bản",
                        command=self.toggle_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Nâng cao", variable=self.mode_var, value="Nâng cao",
                        command=self.toggle_mode).pack(side=tk.LEFT, padx=5)
        
        # --- Khung Thiết lập chung (bao gồm Ngày đánh giá) ---
        common_settings_frame = ttk.LabelFrame(main_frame, text="Thiết lập chung", padding=10)
        common_settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(common_settings_frame, text="Ngày thực hiện tối ưu hóa dòng tiền (dd/mm/yyyy):").pack(side=tk.LEFT, padx=5)
        self.eval_date_entry = ttk.Entry(common_settings_frame, width=15)
        self.eval_date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        self.eval_date_entry.pack(side=tk.LEFT, padx=5)

        # Khung quản lý bộ giao dịch
        dataset_frame = ttk.LabelFrame(main_frame, text="Quản lý bộ giao dịch", padding=10)
        dataset_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dataset_frame, text="Tên bộ giao dịch:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dataset_frame, textvariable=self.dataset_name_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(dataset_frame, text="Lưu bộ giao dịch", command=self.save_dataset).pack(side=tk.LEFT, padx=5)
        ttk.Button(dataset_frame, text="Tải bộ giao dịch", command=self.show_datasets).pack(side=tk.LEFT, padx=5)
        self.save_changes_button = ttk.Button(dataset_frame, text="Lưu thay đổi", 
                                              command=self.save_changes_to_dataset, 
                                              state=tk.DISABLED) # Ban đầu là DISABLED
        self.save_changes_button.pack(side=tk.LEFT, padx=5)


        # Khung nhập giao dịch
        input_frame = ttk.LabelFrame(main_frame, text="Nhập giao dịch", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_widgets = {}
        self.dropdown_widgets = {}

        labels_entries = [
            ("Người nợ", 20), 
            ("Người cho vay", 20), 
            ("Số tiền", 20),
            ("Ngày vay (dd/mm/yyyy)", 20), 
            ("Ngày đến hạn (dd/mm/yyyy)", 20),
            ("Lãi suất (%)", 10), # Key này cần khớp với config cột
            ("Phí phạt (%)", 10)      # Key này cần khớp với config cột
        ]
        current_entry_row = 0 
        for i, (label_text, width) in enumerate(labels_entries):
            row_for_this_entry_pair = i // 2 
            label_col = (i % 2) * 2
            entry_col = label_col + 1
            current_entry_row = row_for_this_entry_pair 

            lbl = ttk.Label(input_frame, text=label_text + ":")
            lbl.grid(row=row_for_this_entry_pair, column=label_col, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(input_frame, width=width)
            entry.grid(row=row_for_this_entry_pair, column=entry_col, padx=5, pady=3, sticky="ew")
            self.input_widgets[label_text] = (lbl, entry)
        
        dropdown_display_row = current_entry_row + 1 

        # --- KIỂU PHÍ PHẠT (bên trái) ---
        lbl_penalty_type = ttk.Label(input_frame, text="Kiểu phí phạt:")
        # Label ở cột 0, dòng dropdown_display_row
        lbl_penalty_type.grid(row=dropdown_display_row, column=0, padx=5, pady=3, sticky="w") 

        combo_penalty_type = ttk.Combobox(input_frame, state="readonly", width=18)
        combo_penalty_type['values'] = list(self.penalty_mapping.keys())
        combo_penalty_type.current(list(self.penalty_mapping.keys()).index("Phạt cố định")) # Mặc định
        # Combobox ở cột 1, dòng dropdown_display_row
        combo_penalty_type.grid(row=dropdown_display_row, column=1, padx=5, pady=3, sticky="ew") 
        self.dropdown_widgets['penalty_type'] = (lbl_penalty_type, combo_penalty_type)


        # --- KIỂU LÃI SUẤT (bên phải) ---
        lbl_interest_type = ttk.Label(input_frame, text="Kiểu lãi suất:")
        # Label ở cột 2, dòng dropdown_display_row
        lbl_interest_type.grid(row=dropdown_display_row, column=2, padx=5, pady=3, sticky="w") 

        combo_interest_type = ttk.Combobox(input_frame, state="readonly", width=18)
        combo_interest_type['values'] = list(self.interest_mapping.keys())
        combo_interest_type.current(list(self.interest_mapping.keys()).index("Lãi kép ngày")) # Mặc định
        # Combobox ở cột 3, dòng dropdown_display_row
        combo_interest_type.grid(row=dropdown_display_row, column=3, padx=5, pady=3, sticky="ew") 
        self.dropdown_widgets['interest_type'] = (lbl_interest_type, combo_interest_type)
        
        for i in range(4): # input_frame có 4 cột được sử dụng
            input_frame.columnconfigure(i, weight=1)

        # Khung nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_frame, text="Thêm giao dịch", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Tối ưu hóa", command=self.optimize_transactions).pack(side=tk.LEFT, padx=5)

        # Khung chọn thuật toán
        algo_frame = ttk.LabelFrame(main_frame, text="Chọn thuật toán", padding=10)
        algo_frame.pack(fill=tk.X, pady=(0, 10))
        algorithms = ["Greedy", "Dynamic Programming", "Cycle Detector", "Min-Cost Max-Flow"]
        for i, algo in enumerate(algorithms):
            ttk.Radiobutton(algo_frame, text=algo, variable=self.algorithm_var, value=algo).pack(side=tk.LEFT, padx=10)

        # Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.transaction_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transaction_tab, text="Danh sách giao dịch")
        self.setup_transaction_tab()  # Tạo Treeview và các cột
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Thống kê số dư ròng")
        self.setup_stats_tab()
        self.result_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.result_tab, text="Kết quả tối ưu")
        self.setup_result_tab()

        self.toggle_mode()


    def setup_transaction_tab(self):
        control_frame = ttk.Frame(self.transaction_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(control_frame, text="Sửa giao dịch được chọn", command=self.edit_selected_transaction).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Xóa giao dịch được chọn", command=self.delete_selected_transaction).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Xóa tất cả giao dịch", command=self.delete_all_transactions).pack(side=tk.LEFT,
                                                                                                         padx=5)
        list_frame = ttk.Frame(self.transaction_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.transaction_tree = ttk.Treeview(list_frame, columns=tuple(self.all_treeview_columns_ordered), show="headings", height=25)  # Tăng chiều cao

        all_column_configs = {
            **self.core_columns_config,
            **self.advanced_only_extra_columns_config,
            **self.type_column_config
        }

        for col_id in self.all_treeview_columns_ordered:
            if col_id in all_column_configs:
                config = all_column_configs[col_id]
                self.transaction_tree.heading(col_id, text=config["text"])
                self.transaction_tree.column(col_id, width=config["width"], anchor=config["anchor"], minwidth=config["minwidth"])
            else:
                print(f"Cảnh báo: Không tìm thấy cấu hình cho cột {col_id} khi thiết lập Treeview.")

        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tree = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        self.transaction_tree.configure(yscrollcommand=scrollbar_tree.set)

    def setup_result_tab(self):
        info_label = ttk.Label(self.result_tab,
                               text="Kết quả tối ưu hóa sẽ hiển thị ở đây sau khi bạn nhấn 'Tối ưu hóa'")
        info_label.pack(pady=10)
        result_frame = ttk.Frame(self.result_tab)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.result_text = tk.Text(result_frame, height=35, wrap=tk.WORD, font=("Consolas", 11))  # Tăng font size và chiều cao
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_result = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar_result.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar_result.set)
        export_frame = ttk.Frame(self.result_tab)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(export_frame, text="Sao chép kết quả", command=self.copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Xóa kết quả", command=self.clear_result).pack(side=tk.LEFT, padx=5)

    def setup_stats_tab(self):
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.stats_text = tk.Text(stats_frame, height=35, wrap=tk.WORD, font=("Consolas", 11))  # Tăng font size và chiều cao
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_stats = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.configure(yscrollcommand=scrollbar_stats.set)

    def toggle_mode_columns(self):
        mode = self.mode_var.get()

        core_cols = list(self.core_columns_config.keys())            # ["STT", "Người nợ", "Người cho vay", "Số tiền"]
        type_col = list(self.type_column_config.keys())              # ["Loại GD"]
        all_cols = self.all_treeview_columns_ordered                 # ["STT", "Người nợ", "Người cho vay", "Số tiền",
                                                                     #  "Ngày vay", "Ngày đến hạn", "Lãi suất", "Phí phạt", "Loại GD"]

        if mode == "Cơ bản":
            # Chỉ hiện cột cốt lõi + "Loại GD"
            display = core_cols + type_col
        else:  # "Nâng cao"
            # Hiện tất cả cột
            display = all_cols

        self.transaction_tree.config(displaycolumns=display)

        # Ngoài ra, reset width/minwidth để giữ kích thước đúng khi quay lại Nâng cao
        for col_id, config in self.core_columns_config.items():
            self.transaction_tree.column(col_id, width=config["width"], minwidth=config["minwidth"])
        for col_id, config in self.advanced_only_extra_columns_config.items():
            if mode == "Nâng cao":
                self.transaction_tree.column(col_id, width=config["width"], minwidth=config["minwidth"])
            else:
                self.transaction_tree.column(col_id, width=0, minwidth=0)
        # Cột "Loại GD" luôn hiển thị
        type_id = type_col[0]
        type_cfg = self.type_column_config[type_id]
        self.transaction_tree.column(type_id, width=type_cfg["width"], minwidth=type_cfg["minwidth"])


                
    def toggle_mode(self):
        mode = self.mode_var.get()

        # 1) Trước hết, vẫn duy trì việc ẩn/hiện cột Treeview
        self.toggle_mode_columns()

        # 2) Xác định 2 nhóm widget cần ẩn/hiện:
        #    - Các entry nâng cao (trong self.input_widgets)
        #    - Các dropdown (trong self.dropdown_widgets)
        advanced_fields = [
            "Ngày vay (dd/mm/yyyy)",
            "Ngày đến hạn (dd/mm/yyyy)",
            "Lãi suất (%)",
            "Phí phạt (%)"
        ]

        # a) Nếu ở Chế độ Cơ bản, ẩn các:
        #    + Label+Entry trong advanced_fields
        #    + Label+Combobox trong self.dropdown_widgets
        if mode == "Cơ bản":
            for field in advanced_fields:
                lbl, entry = self.input_widgets[field]
                lbl.grid_remove()
                entry.grid_remove()

            for key, (lbl_dd, combo_dd) in self.dropdown_widgets.items():
                lbl_dd.grid_remove()
                combo_dd.grid_remove()

        # b) Nếu ở Chế độ Nâng cao, hiện lại chúng
        else:  # mode == "Nâng cao"
            # Hiện các label+entry nâng cao
            for field in advanced_fields:
                lbl, entry = self.input_widgets[field]
                lbl.grid()
                entry.grid()
            # Hiện các label+combobox
            for key, (lbl_dd, combo_dd) in self.dropdown_widgets.items():
                lbl_dd.grid()
                combo_dd.grid()

        # 3) Cuối cùng, cập nhật lại nội dung Treeview (nếu cần)
        self.update_transaction_display()



    def save_dataset(self):
        """
        Lưu danh sách giao dịch hiện tại thành một BỘ DỮ LIỆU MỚI trong database.
        Sau khi lưu thành công, bộ dữ liệu này sẽ trở thành bộ hiện tại.
        """
        dataset_name = self.dataset_name_var.get().strip()
        if not dataset_name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên bộ giao dịch.")
            return
        if self.transactions.is_empty():
            messagebox.showwarning("Cảnh báo", "Không có giao dịch nào để lưu.")
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM datasets WHERE name = ?", (dataset_name,))
                if cursor.fetchone():
                    if not messagebox.askyesno("Xác nhận", f"Bộ giao dịch '{dataset_name}' đã tồn tại. Bạn có muốn ghi đè lên nó không?"):
                        return
                    # Nếu người dùng muốn ghi đè
                    cursor.execute("SELECT id FROM datasets WHERE name = ?", (dataset_name,))
                    existing_id = cursor.fetchone()[0]
                    cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (existing_id,))
                    cursor.execute("UPDATE datasets SET created_at = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), existing_id))
                    dataset_id = existing_id
                else:
                    # Nếu là bộ mới, chèn vào datasets
                    cursor.execute("INSERT INTO datasets (name, created_at) VALUES (?, ?)",
                                   (dataset_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    dataset_id = cursor.lastrowid
                
                # Cập nhật ID hiện tại của GUI
                self.current_dataset_id = dataset_id
                
                # Lưu các giao dịch với dataset_id vừa có
                for tx_node in self.transactions:
                    tx = tx_node
                    if isinstance(tx, BasicTransaction):
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (dataset_id, "basic", tx.debtor, tx.creditor, tx.amount))
                    else: # AdvancedTransaction
                        interest_type_name = tx.interest_type.name if tx.interest_type else None
                        penalty_type_name = tx.penalty_type.name if tx.penalty_type else None
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount, 
                                                    borrow_date, due_date, interest_rate, penalty_fee,
                                                    interest_type_name, penalty_type_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (dataset_id, "advanced", tx.debtor, tx.creditor, tx.amount,
                              tx.borrow_date.strftime("%Y-%m-%d"),
                              tx.due_date.strftime("%Y-%m-%d"),
                              tx.interest_rate, tx.penalty_rate,
                              interest_type_name, penalty_type_name))
                
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã lưu bộ giao dịch '{dataset_name}'!")
                self.save_changes_button.config(state=tk.NORMAL) # Kích hoạt nút "Lưu thay đổi"
        
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lưu bộ giao dịch: {e}")

    def show_datasets(self):
        """Hiển thị danh sách các bộ giao dịch đã lưu."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, created_at FROM datasets")
                datasets = cursor.fetchall()
                if not datasets:
                    messagebox.showinfo("Thông báo", "Không có bộ giao dịch nào đã lưu.")
                    return
                # Tạo cửa sổ chọn bộ giao dịch
                dataset_window = tk.Toplevel(self.root)
                dataset_window.title("Chọn bộ giao dịch")
                dataset_window.geometry("600x400")
                list_frame = ttk.Frame(dataset_window)
                list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                columns = ("ID", "Tên", "Ngày tạo")
                dataset_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
                dataset_tree.heading("ID", text="ID")
                dataset_tree.heading("Tên", text="Tên bộ giao dịch")
                dataset_tree.heading("Ngày tạo", text="Ngày tạo")
                dataset_tree.column("ID", width=50, anchor=tk.CENTER)
                dataset_tree.column("Tên", width=200, anchor=tk.W)
                dataset_tree.column("Ngày tạo", width=150, anchor=tk.W)
                dataset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=dataset_tree.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                dataset_tree.configure(yscrollcommand=scrollbar.set)
                for dataset in datasets:
                    dataset_tree.insert("", tk.END, values=dataset)
                # Nút tải và xóa
                btn_frame = ttk.Frame(dataset_window)
                btn_frame.pack(pady=10)
                ttk.Button(btn_frame, text="Tải bộ giao dịch",
                           command=lambda: self.load_dataset(dataset_tree, dataset_window)).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Xóa bộ giao dịch",
                           command=lambda: self.delete_dataset(dataset_tree)).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Đóng", command=dataset_window.destroy).pack(side=tk.LEFT, padx=5)
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bộ giao dịch: {e}")

    def load_dataset(self, tree, window_to_close=None):
        """Tải bộ giao dịch được chọn."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bộ giao dịch để tải.")
            return
        
        # Giá trị từ Treeview (trong cửa sổ chọn dataset)
        dataset_id_from_tree = tree.item(selected[0])["values"][0]
        dataset_name_from_tree = tree.item(selected[0])["values"][1]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Câu lệnh SELECT nên lấy tất cả các cột cần thiết
                # Thứ tự cột: 0:id, 1:dataset_id, 2:type, 3:debtor, 4:creditor, 5:amount, 
                # 6:borrow_date, 7:due_date, 8:interest_rate, 9:penalty_fee, 
                # 10:interest_type_name, 11:penalty_type_name
                cursor.execute("""
                    SELECT id, dataset_id, type, debtor, creditor, amount, 
                           borrow_date, due_date, interest_rate, penalty_fee, 
                           interest_type_name, penalty_type_name 
                    FROM transactions 
                    WHERE dataset_id = ?
                """, (dataset_id_from_tree,))
                transactions_data = cursor.fetchall()
                
                self.transactions = LinkedList() # Khởi tạo lại danh sách giao dịch
                loaded_mode = "Cơ bản" # Mặc định

                for tx_data_row in transactions_data:
                    # Truy cập theo chỉ số cột, bắt đầu từ 0
                    # transaction_pk_id = tx_data_row[0] # Không dùng trực tiếp nhưng có thể hữu ích
                    # dataset_id_fk = tx_data_row[1]   # Đã có dataset_id_from_tree
                    
                    tx_type_db = tx_data_row[2]
                    debtor_db = tx_data_row[3]
                    creditor_db = tx_data_row[4]
                    amount_db = tx_data_row[5]

                    if tx_type_db == "basic":
                        transaction = BasicTransaction(debtor_db, creditor_db, amount_db)
                    else: # tx_type_db == "advanced"
                        loaded_mode = "Nâng cao"
                        borrow_date_str_db = tx_data_row[6]
                        due_date_str_db = tx_data_row[7]
                        interest_rate_val_db = tx_data_row[8]
                        # Giả sử cột 'penalty_fee' trong DB tương ứng với 'penalty_rate' của AdvancedTransaction
                        penalty_rate_val_db = tx_data_row[9] 
                        interest_type_name_str_db = tx_data_row[10]
                        penalty_type_name_str_db = tx_data_row[11]

                        # Chuyển đổi ngày tháng (cần xử lý nếu có thể là None, mặc dù không nên với Advanced)
                        borrow_date_obj = datetime.strptime(borrow_date_str_db, "%Y-%m-%d").date() if borrow_date_str_db else None
                        due_date_obj = datetime.strptime(due_date_str_db, "%Y-%m-%d").date() if due_date_str_db else None

                        # Chuyển đổi tên enum từ DB về đối tượng enum
                        interest_type_enum = InterestType.SIMPLE # Mặc định nếu không tìm thấy
                        if interest_type_name_str_db and interest_type_name_str_db in InterestType.__members__:
                            interest_type_enum = InterestType[interest_type_name_str_db]
                        
                        penalty_type_enum = PenaltyType.FIXED # Mặc định nếu không tìm thấy
                        if penalty_type_name_str_db and penalty_type_name_str_db in PenaltyType.__members__:
                            penalty_type_enum = PenaltyType[penalty_type_name_str_db]

                        final_penalty_rate_for_tx = penalty_rate_val_db if penalty_rate_val_db is not None else 0.0

                        transaction = AdvancedTransaction(
                            debtor=debtor_db, 
                            creditor=creditor_db, 
                            amount=amount_db,
                            borrow_date=borrow_date_obj, 
                            due_date=due_date_obj,
                            interest_rate=interest_rate_val_db if interest_rate_val_db is not None else 0.0, 
                            penalty_rate=final_penalty_rate_for_tx,
                            interest_type=interest_type_enum,
                            penalty_type=penalty_type_enum
                        )
                    self.transactions.append(transaction)
                
                # --- Cập nhật GUI SAU KHI vòng lặp kết thúc ---
                self.current_dataset_id = dataset_id_from_tree
                self.dataset_name_var.set(dataset_name_from_tree)
                self.mode_var.set(loaded_mode)
                self.toggle_mode() # Sẽ gọi update_transaction_display

                if self.save_changes_button:
                    self.save_changes_button.config(state=tk.NORMAL)

                messagebox.showinfo("Thành công", f"Đã tải bộ giao dịch '{dataset_name_from_tree}'!")
                if window_to_close:
                    window_to_close.destroy()
                self.root.focus_force()

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu khi tải bộ giao dịch: {e}")
        except ValueError as ve: # Bắt lỗi strptime
             messagebox.showerror("Lỗi", f"Lỗi định dạng dữ liệu khi tải bộ giao dịch: {ve}")
        except KeyError as ke: # Bắt lỗi nếu tên enum không tìm thấy trong mapping (dù đã có fallback)
            messagebox.showerror("Lỗi", f"Lỗi kiểu dữ liệu không xác định khi tải: {ke}")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi không xác định khi tải bộ giao dịch: {ex}")
            import traceback
            traceback.print_exc()

    def delete_dataset(self, tree):
        """
        Xóa bộ giao dịch được chọn khỏi database. Nếu đó là bộ hiện tại, reset GUI.
        """
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bộ giao dịch để xóa.")
            return
            
        dataset_id_to_delete = tree.item(selected[0])["values"][0]
        dataset_name_to_delete = tree.item(selected[0])["values"][1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa bộ giao dịch '{dataset_name_to_delete}'? Thao tác này không thể hoàn tác."):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (dataset_id_to_delete,))
                    cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id_to_delete,))
                    conn.commit()
                    
                    if self.current_dataset_id == dataset_id_to_delete:
                        # Reset trạng thái GUI nếu bộ đang mở bị xóa
                        self.transactions = LinkedList()
                        self.current_dataset_id = None
                        self.dataset_name_var.set("")
                        self.update_transaction_display()
                        self.save_changes_button.config(state=tk.DISABLED) # Vô hiệu hóa nút
                        
                    messagebox.showinfo("Thành công", f"Đã xóa bộ giao dịch '{dataset_name_to_delete}'!")
                    tree.delete(selected[0])
            
            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa bộ giao dịch: {e}")

    def add_transaction(self):
        try:
            mode = self.mode_var.get()
            debtor   = self.input_widgets["Người nợ"][1].get().strip()
            creditor = self.input_widgets["Người cho vay"][1].get().strip()
            amount_str = self.input_widgets["Số tiền"][1].get().strip()
            if not amount_str:
                raise ValueError("Số tiền không được để trống.")
            amount = float(amount_str)

            # ... (other initial checks) ...

            if mode == "Cơ bản":
                tx = BasicTransaction(debtor=debtor, creditor=creditor, amount=amount) # Use float amount
            else:
                borrow_date_str = self.input_widgets["Ngày vay (dd/mm/yyyy)"][1].get().strip()
                due_date_str    = self.input_widgets["Ngày đến hạn (dd/mm/yyyy)"][1].get().strip()
                interest_str    = self.input_widgets["Lãi suất (%)"][1].get().strip()
                penalty_str     = self.input_widgets["Phí phạt (%)"][1].get().strip() 

                if not borrow_date_str or not due_date_str:
                    raise ValueError("Ngày vay và ngày đến hạn không được để trống.")
                if not interest_str:
                    raise ValueError("Lãi suất không được để trống.")
                if not penalty_str:
                    raise ValueError("Phí phạt không được để trống.")

                interest_label = self.dropdown_widgets['interest_type'][1].get()
                penalty_label  = self.dropdown_widgets['penalty_type'][1].get()
                interest_type = self.interest_mapping[interest_label]
                penalty_type  = self.penalty_mapping[penalty_label]

                interest_rate_val = float(interest_str) / 100.0 
                penalty_rate_val  = float(penalty_str)

                if penalty_type == PenaltyType.PERCENTAGE:
                    penalty_rate_val = penalty_rate_val / 100.0


                if interest_rate_val < 0 or penalty_rate_val < 0: # Check adjusted penalty_rate_val
                    raise ValueError("Lãi suất và phí phạt không được âm.")

                borrow_date = datetime.strptime(borrow_date_str, "%d/%m/%Y").date()
                due_date    = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                if due_date < borrow_date:
                    raise ValueError("Ngày đến hạn phải sau ngày vay.")

                tx = AdvancedTransaction(
                    debtor=debtor,
                    creditor=creditor,
                    amount=amount,
                    borrow_date=borrow_date,
                    due_date=due_date,
                    interest_rate=interest_rate_val,
                    penalty_rate=penalty_rate_val, # Use the potentially adjusted value
                    interest_type=interest_type,
                    penalty_type=penalty_type
                )

            # Thêm và cập nhật giao diện
            self.transactions.append(tx)
            messagebox.showinfo("Thành công", "Đã thêm giao dịch!")
            self.clear_entries()
            self.update_transaction_display()

        except ValueError as ve:
            messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {ve}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


    def clear_entries(self):
        # Xóa tất cả các entry
        for key, (lbl, entry) in self.input_widgets.items():
            entry.delete(0, tk.END)
        # Reset combobox về mặc định (tiếng Việt)
        default_interest = "Lãi kép ngày"
        default_penalty  = "Phạt cố định"
        self.dropdown_widgets['interest_type'][1].set(default_interest)
        self.dropdown_widgets['penalty_type'][1].set(default_penalty)

    def update_transaction_display(self):
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)

        if self.transactions.is_empty():
            # ... (code xử lý khi rỗng giữ nguyên) ...
            empty_row_values = [""] * len(self.all_treeview_columns_ordered)
            try:
                nguoi_no_col_id = list(self.core_columns_config.keys())[1]
                nguoi_no_index_in_all = self.all_treeview_columns_ordered.index(nguoi_no_col_id)
                empty_row_values[nguoi_no_index_in_all] = "Không có giao dịch nào"
            except (IndexError, ValueError):
                if len(empty_row_values) > 1: empty_row_values[1] = "Không có giao dịch nào"
                else: empty_row_values[0] = "Không có giao dịch nào"
            self.transaction_tree.insert("", tk.END, values=tuple(empty_row_values))
            return


        for i, tx_node in enumerate(self.transactions, 1):
            tx = tx_node

            row_data = {col_id: "" for col_id in self.all_treeview_columns_ordered}

            row_data["STT"] = str(i)
            row_data["Người nợ"] = tx.debtor
            row_data["Người cho vay"] = tx.creditor
            row_data["Số tiền"] = f"{tx.amount:,.2f}"

            if isinstance(tx, BasicTransaction):
                row_data["Loại GD"] = "Cơ bản"
            else:  # AdvancedTransaction
                row_data["Loại GD"] = "Nâng cao"
                row_data["Ngày vay"] = tx.borrow_date.strftime('%d/%m/%Y')
                row_data["Ngày đến hạn"] = tx.due_date.strftime('%d/%m/%Y')
                # Sử dụng key "Lãi suất (%)" nếu bạn đã đổi tên trong config cột
                row_data["Lãi suất (%)"] = f"{tx.interest_rate * 100:.2f}" # Không còn dấu %
                row_data["Phí phạt"] = f"{tx.penalty_rate:,.2f}"

                # Hiển thị kiểu lãi và kiểu phạt từ enum
                row_data["Kiểu lãi"] = self.reverse_interest_mapping.get(tx.interest_type, "N/A")
                row_data["Kiểu phạt"] = self.reverse_penalty_mapping.get(tx.penalty_type, "N/A")


            values_tuple = tuple(row_data[col_id] for col_id in self.all_treeview_columns_ordered)
            self.transaction_tree.insert("", tk.END, values=values_tuple)

    def edit_selected_transaction(self):
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một giao dịch để sửa.")
            return
        item = selected[0]
        # "values" từ treeview là tuple các string, bao gồm cả các cột ẩn (nhưng giá trị có thể rỗng)
        # STT luôn là giá trị đầu tiên
        try:
            index_in_tree = int(self.transaction_tree.item(item)["values"][0]) - 1
        except (ValueError, TypeError):
            messagebox.showerror("Lỗi", "Không thể lấy chỉ số giao dịch từ Treeview.")
            return

        # Lấy giao dịch từ danh sách `self.transactions` bằng chỉ số thực
        try:
             tx = self.transactions.get_at_index(index_in_tree)
        except IndexError:
            messagebox.showerror("Lỗi", "Chỉ số giao dịch không hợp lệ trong danh sách.")
            self.update_transaction_display() # Làm mới treeview nếu có sự không nhất quán
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Sửa giao dịch")
        edit_window.geometry("400x400" if isinstance(tx, AdvancedTransaction) else "400x250") # Điều chỉnh kích thước
        
        form_frame = ttk.Frame(edit_window, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        current_row = 0
        ttk.Label(form_frame, text="Người nợ:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
        debtor_entry = ttk.Entry(form_frame)
        debtor_entry.insert(0, tx.debtor)
        debtor_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

        ttk.Label(form_frame, text="Người cho vay:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
        creditor_entry = ttk.Entry(form_frame)
        creditor_entry.insert(0, tx.creditor)
        creditor_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

        ttk.Label(form_frame, text="Số tiền:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
        amount_entry = ttk.Entry(form_frame)
        amount_entry.insert(0, str(tx.amount))
        amount_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

        borrow_date_entry, due_date_entry, interest_entry, penalty_entry = None, None, None, None
        edit_interest_type_combo, edit_penalty_type_combo = None, None


        if isinstance(tx, AdvancedTransaction):
            ttk.Label(form_frame, text="Ngày vay (dd/mm/yyyy):").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
            borrow_date_entry = ttk.Entry(form_frame)
            borrow_date_entry.insert(0, tx.borrow_date.strftime("%d/%m/%Y"))
            borrow_date_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1
            
            ttk.Label(form_frame, text="Ngày đến hạn (dd/mm/yyyy):").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
            due_date_entry = ttk.Entry(form_frame)
            due_date_entry.insert(0, tx.due_date.strftime("%d/%m/%Y"))
            due_date_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

            ttk.Label(form_frame, text="Lãi suất:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
            interest_entry = ttk.Entry(form_frame)
            interest_entry.insert(0, str(tx.interest_rate * 100))
            interest_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

            ttk.Label(form_frame, text="Phí phạt (%):").grid(row=current_row, column=0, sticky="e", padx=5, pady=5) # Thêm (%) vào label
            penalty_entry = ttk.Entry(form_frame)
            
            initial_penalty_display_val = tx.penalty_rate # Sử dụng tx.penalty_rate
            if tx.penalty_type == PenaltyType.PERCENTAGE:
                initial_penalty_display_val = tx.penalty_rate * 100.0 # Nhân 100 nếu là %
            penalty_entry.insert(0, str(initial_penalty_display_val))
            penalty_entry.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

            current_row +=1 # Đảm bảo current_row được cập nhật đúng
            ttk.Label(form_frame, text="Kiểu lãi suất:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
            edit_interest_type_combo = ttk.Combobox(form_frame, state="readonly", values=list(self.interest_mapping.keys()), width=18)
            edit_interest_type_combo.set(self.reverse_interest_mapping.get(tx.interest_type, "Lãi đơn")) 
            edit_interest_type_combo.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1

            ttk.Label(form_frame, text="Kiểu phí phạt:").grid(row=current_row, column=0, sticky="e", padx=5, pady=5)
            edit_penalty_type_combo = ttk.Combobox(form_frame, state="readonly", values=list(self.penalty_mapping.keys()), width=18)
            edit_penalty_type_combo.set(self.reverse_penalty_mapping.get(tx.penalty_type, "Phạt cố định"))
            edit_penalty_type_combo.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5); current_row += 1
        
        form_frame.columnconfigure(1, weight=1)

        def save_changes():
            nonlocal tx # Để có thể gán lại nếu loại giao dịch thay đổi
            try:
                new_debtor = debtor_entry.get().strip()
                new_creditor = creditor_entry.get().strip()
                new_amount_str = amount_entry.get().strip()

                if not new_amount_str: raise ValueError("Số tiền không được để trống.")
                new_amount = float(new_amount_str)

                # ... (các kiểm tra debtor, creditor, amount khác) ...

                is_editing_advanced = isinstance(self.transactions.get_at_index(index_in_tree), AdvancedTransaction)
                # Hoặc dựa vào việc các entry nâng cao có được tạo không:
                # is_editing_advanced = (borrow_date_entry is not None)
                
                if is_editing_advanced:
                    # Đảm bảo các widget này đã được tạo nếu is_editing_advanced là True
                    if borrow_date_entry is None or due_date_entry is None or \
                       interest_entry is None or penalty_entry is None or \
                       edit_interest_type_combo is None or edit_penalty_type_combo is None:
                        messagebox.showerror("Lỗi lập trình", "Các trường sửa giao dịch nâng cao chưa được khởi tạo đúng.", parent=edit_window)
                        return

                    borrow_date_str = borrow_date_entry.get().strip()
                    due_date_str = due_date_entry.get().strip()
                    interest_rate_percent_str = interest_entry.get().strip() # Đây là % (ví dụ "5" cho 5%)
                    penalty_value_str = penalty_entry.get().strip() # Đây là giá trị từ ô "Phí phạt (%)"

                    if not all([borrow_date_str, due_date_str, interest_rate_percent_str, penalty_value_str]):
                         raise ValueError("Tất cả các trường nâng cao (ngày, lãi suất, phí phạt) phải được điền.")

                    borrow_date = datetime.strptime(borrow_date_str, "%d/%m/%Y").date()
                    due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                    if due_date < borrow_date: raise ValueError("Ngày đến hạn phải sau ngày vay.")
                    
                    interest_rate_decimal = float(interest_rate_percent_str) / 100.0 # Chuyển % sang thập phân

                    # Lấy kiểu lãi và kiểu phạt từ combobox
                    new_interest_label = edit_interest_type_combo.get()
                    new_penalty_label = edit_penalty_type_combo.get()
                    new_interest_type = self.interest_mapping[new_interest_label]
                    new_penalty_type = self.penalty_mapping[new_penalty_label]

                    # Xử lý giá trị phí phạt
                    penalty_rate_for_constructor = float(penalty_value_str)
                    if new_penalty_type == PenaltyType.PERCENTAGE:
                        # Nếu người dùng nhập "10" cho 10%, chuyển thành 0.10
                        penalty_rate_for_constructor = penalty_rate_for_constructor / 100.0
                    
                    if interest_rate_decimal < 0 or penalty_rate_for_constructor < 0: 
                        raise ValueError("Lãi suất và giá trị phí phạt không được âm.")
                    
                    updated_tx = AdvancedTransaction(
                        debtor=new_debtor,
                        creditor=new_creditor,
                        amount=new_amount,
                        borrow_date=borrow_date,
                        due_date=due_date,
                        interest_rate=interest_rate_decimal,
                        penalty_rate=penalty_rate_for_constructor, # Đã xử lý ở trên
                        interest_type=new_interest_type,
                        penalty_type=new_penalty_type
                    )
                else: # Đang sửa giao dịch cơ bản
                    updated_tx = BasicTransaction(
                        debtor=new_debtor, creditor=new_creditor, amount=new_amount
                    )
                
                self.transactions.set_at_index(index_in_tree, updated_tx)
                self.update_transaction_display()

                if self.current_dataset_id:
                    self.save_changes_to_dataset(show_success_message=False)
                    messagebox.showinfo("Thành công", "Đã cập nhật giao dịch và lưu thay đổi vào bộ hiện tại!")
                else:
                     messagebox.showinfo("Thành công", "Đã cập nhật giao dịch (chưa lưu vào bộ nào).")
                
                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {ve}", parent=edit_window)
            except Exception as e:
                import traceback
                traceback.print_exc() # In traceback đầy đủ ra console để debug
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi lưu: {e}", parent=edit_window)

        btn_frame = ttk.Frame(edit_window)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Hoàn tất", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hủy", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)


    def delete_selected_transaction(self):
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một giao dịch để xóa.")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giao dịch này?"):
            item = selected[0]
            try:
                # STT là giá trị đầu tiên trong tuple 'values'
                index_in_tree = int(self.transaction_tree.item(item)["values"][0]) - 1
                
                # Xóa khỏi danh sách `self.transactions`
                tx_to_delete = self.transactions.remove_at_index(index_in_tree) # Giả sử remove_at_index trả về item đã xóa
                
                self.update_transaction_display() # Cập nhật Treeview

                if self.current_dataset_id:
                    # Cách tiếp cận đơn giản: Lưu lại toàn bộ dataset
                    self.save_changes_to_dataset(show_success_message=False)
                    messagebox.showinfo("Thành công", "Đã xóa giao dịch và cập nhật bộ dữ liệu!")
                else:
                    messagebox.showinfo("Thành công", "Đã xóa giao dịch (chưa lưu vào bộ nào).")

            except (ValueError, TypeError):
                messagebox.showerror("Lỗi", "Không thể lấy chỉ số giao dịch để xóa.")
            except IndexError:
                messagebox.showerror("Lỗi", "Không thể xóa giao dịch, chỉ số không hợp lệ.")
                self.update_transaction_display() # Đồng bộ lại treeview
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi xóa: {e}")


    def delete_all_transactions(self):
        if self.transactions.is_empty():
            messagebox.showinfo("Thông báo", "Không có giao dịch nào để xóa.")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tất cả giao dịch?"):
            self.transactions = LinkedList()
            self.update_transaction_display()
            self.clear_result()
            
            if self.current_dataset_id:
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (self.current_dataset_id,))
                        conn.commit()
                    messagebox.showinfo("Thành công", "Đã xóa tất cả giao dịch và cập nhật bộ dữ liệu!")
                except sqlite3.Error as e:
                     messagebox.showerror("Lỗi", f"Không thể xóa giao dịch khỏi cơ sở dữ liệu: {e}")
            else:
                messagebox.showinfo("Thành công", "Đã xóa tất cả giao dịch!")


    def copy_result(self):
        result_content = self.result_text.get(1.0, tk.END).strip()
        if result_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(result_content)
            messagebox.showinfo("Thành công", "Đã sao chép kết quả vào clipboard!")
        else:
            messagebox.showwarning("Cảnh báo", "Không có kết quả để sao chép.")

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)

    def optimize_transactions(self):
        try:
            mode = self.mode_var.get()
            algorithm_name = self.algorithm_var.get()
            self.result_text.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)

            # Lấy ngày đánh giá từ Entry
            eval_date_str = self.eval_date_entry.get()
            try:
                current_date_for_calc = datetime.strptime(eval_date_str, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày đánh giá không hợp lệ. Vui lòng nhập theo định dạng dd/mm/yyyy.")
                return

            self.result_text.insert(tk.END, f"🎯 KẾT QUẢ TỐI ƯU HÓA ({algorithm_name} - Chế độ: {mode} - Ngày ĐG: {current_date_for_calc.strftime('%d/%m/%Y')}):\n")
            self.result_text.insert(tk.END, "-" * 60 + "\n")

            if self.transactions.is_empty():
                self.result_text.insert(tk.END, "❌ Không có giao dịch nào để tối ưu hóa.\n")
                self.stats_text.insert(tk.END, "❌ Không có giao dịch nào để thống kê.\n")
                self.notebook.select(self.result_tab)
                return

            original_count = 0
            temp_node_count = self.transactions.head
            while temp_node_count:
                original_count += 1
                temp_node_count = temp_node_count.next

            result_transactions_list = LinkedList()

            if mode == "Cơ bản":
                basic_transactions_for_opt = LinkedList()
                temp_node_basic = self.transactions.head
                while temp_node_basic:
                    tx = temp_node_basic.data
                    if isinstance(tx, AdvancedTransaction):
                        debt_breakdown = tx.get_debt_breakdown(current_date_for_calc)
                        actual_amount = debt_breakdown['total']
                        basic_tx = BasicTransaction(tx.debtor, tx.creditor, round(actual_amount, 2))
                    else:  # tx is BasicTransaction
                        basic_tx = BasicTransaction(tx.debtor, tx.creditor, round(tx.amount, 2))
                    basic_transactions_for_opt.append(basic_tx)
                    temp_node_basic = temp_node_basic.next

                if algorithm_name == "Greedy":
                    simplifier = GreedySimplifier(basic_transactions_for_opt)
                elif algorithm_name == "Dynamic Programming":
                    simplifier = DynamicProgrammingSimplifier(basic_transactions_for_opt)
                elif algorithm_name == "Cycle Detector":
                    simplifier = DebtCycleSimplifier(basic_transactions_for_opt)
                elif algorithm_name == "Min-Cost Max-Flow":
                    simplifier = MinCostMaxFlowSimplifier(basic_transactions_for_opt)
                else:
                    raise ValueError(f"Thuật toán cơ bản không hợp lệ: {algorithm_name}")

                result_transactions_list = simplifier.simplify()

            else:  # Chế độ "Nâng cao"
                advanced_transactions_for_opt = LinkedList()
                temp_node_adv = self.transactions.head
                has_valid_advanced_tx = False
                while temp_node_adv:
                    if isinstance(temp_node_adv.data, AdvancedTransaction):
                        advanced_transactions_for_opt.append(temp_node_adv.data)
                        has_valid_advanced_tx = True
                    else:
                        self.result_text.insert(tk.END, f"⚠️ Cảnh báo: Giao dịch cơ bản ({temp_node_adv.data.debtor} -> {temp_node_adv.data.creditor}) được tìm thấy ở chế độ Nâng cao và sẽ được bỏ qua.\n")
                    temp_node_adv = temp_node_adv.next

                if not has_valid_advanced_tx:
                    self.result_text.insert(tk.END, "❌ Không có giao dịch Nâng cao hợp lệ để tối ưu hóa.\n")
                    self.notebook.select(self.result_tab)
                    return

                if algorithm_name == "Greedy":
                    simplifier = AdvancedGreedySimplifier(advanced_transactions_for_opt, current_date_for_calc)
                    result_transactions_list = simplifier.simplify()

                elif algorithm_name == "Dynamic Programming":
                    simplifier = AdvancedDynamicProgrammingSimplifier(advanced_transactions_for_opt, current_date_for_calc)
                    result_tuple = simplifier.simplify()
                    result_transactions_list = result_tuple[0]
                    dp_stats = result_tuple[1]

                elif algorithm_name == "Cycle Detector":
                    simplifier = AdvancedDebtCycleSimplifier(advanced_transactions_for_opt, current_date_for_calc)
                    result_adv_list = simplifier.simplify_advanced()
                    
                    temp_node_cycle_res = result_adv_list.head
                    while temp_node_cycle_res:
                        adv_tx_res = temp_node_cycle_res.data
                        result_transactions_list.append(
                            BasicTransaction(adv_tx_res.debtor, adv_tx_res.creditor, round(adv_tx_res.amount, 2))
                        )
                        temp_node_cycle_res = temp_node_cycle_res.next

                elif algorithm_name == "Min-Cost Max-Flow":
                    simplifier = AdvancedMinCostMaxFlowSimplifier(advanced_transactions_for_opt, current_date_for_calc)
                    result_transactions_list = simplifier.simplify()
                else:
                    raise ValueError(f"Thuật toán nâng cao không hợp lệ: {algorithm_name}")

            # --- HIỂN THỊ KẾT QUẢ CHUNG ---
            optimized_count = 0
            if result_transactions_list.is_empty():
                self.result_text.insert(tk.END, "✅ Không cần giao dịch nào - Tất cả đã được bù trừ!\n")
            else:
                res_node_display = result_transactions_list.head
                i = 1
                while res_node_display:
                    res_tx = res_node_display.data
                    self.result_text.insert(
                        tk.END,
                        f"{i}. {res_tx.debtor} → {res_tx.creditor}: {res_tx.amount:,.2f}\n"
                    )
                    optimized_count += 1
                    i += 1
                    res_node_display = res_node_display.next

            self.result_text.insert(tk.END, f"\n📊 Số giao dịch gốc: {original_count}\n")
            self.result_text.insert(tk.END, f"📊 Số giao dịch sau tối ưu: {optimized_count}\n")
            if original_count > 0:
                reduction_percent = ((original_count - optimized_count) / original_count * 100)
                self.result_text.insert(
                    tk.END,
                    f"📉 Giảm số giao dịch: {original_count - optimized_count} ({reduction_percent:,.1f}%)\n"
                )
            else:
                self.result_text.insert(tk.END, "📉 Không có giao dịch để tính toán mức giảm.\n")

            # --- TÍNH & HIỂN THỊ SỐ DƯ NET ---
            balance = defaultdict(float)
            final_res_node_balance = result_transactions_list.head
            while final_res_node_balance:
                res_tx_balance = final_res_node_balance.data
                balance[res_tx_balance.debtor] -= res_tx_balance.amount
                balance[res_tx_balance.creditor] += res_tx_balance.amount
                final_res_node_balance = final_res_node_balance.next

            self.stats_text.insert(tk.END, "💰 SỐ DƯ RÒNG TỪNG NGƯỜI:\n")
            self.stats_text.insert(tk.END, "-" * 30 + "\n")
            for person, net_amount in sorted(balance.items()):
                status = "cân bằng"
                if net_amount < -1e-6:
                    status = "phải trả"
                elif net_amount > 1e-6:
                    status = "được nhận"
                self.stats_text.insert(
                    tk.END,
                    f"{person}: {net_amount:,.2f} ({status})\n"
                )

            total_balance = sum(balance.values())
            self.stats_text.insert(tk.END, f"\n🔢 Tổng số dư ròng: {total_balance:,.2f}\n")
            if abs(total_balance) < 1e-6:
                self.stats_text.insert(tk.END, "✅ Tổng số dư bằng 0 (chính xác).\n")
            else:
                self.stats_text.insert(
                    tk.END,
                    f"❌ Lỗi tối ưu hóa: Tổng số dư không bằng 0 (Giá trị: {total_balance:.2f}).\n"
                )

            self.notebook.select(self.result_tab)

        except Exception as e:
            error_message = f"❌ Lỗi khi tối ưu hóa: {e}\n"
            import traceback
            traceback_str = traceback.format_exc()
            print(f"LỖI TRONG optimize_transactions:\n{traceback_str}")
            self.result_text.insert(tk.END, error_message + "\n" + traceback_str)
            self.stats_text.insert(tk.END, error_message)
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi tối ưu hóa: {e}\nXem chi tiết lỗi trong tab kết quả.")
            self.notebook.select(self.result_tab)

    def save_changes_to_dataset(self, show_success_message=True):
        """
        Lưu lại các thay đổi (sửa, xóa giao dịch) vào BỘ DỮ LIỆU HIỆN TẠI đang được tải.
        Hàm này sẽ xóa hết giao dịch cũ của bộ này và chèn lại danh sách hiện tại.
        """
        if self.current_dataset_id is None:
            if show_success_message:
                 messagebox.showwarning("Cảnh báo", "Không có bộ giao dịch nào đang được chọn để lưu thay đổi. Hãy tải hoặc lưu một bộ mới trước.")
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Xóa tất cả giao dịch cũ của bộ hiện tại
                cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (self.current_dataset_id,))
                
                # Lưu lại toàn bộ danh sách giao dịch hiện tại với self.current_dataset_id
                for tx_node in self.transactions:
                    tx = tx_node
                    if isinstance(tx, BasicTransaction):
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (self.current_dataset_id, "basic", tx.debtor, tx.creditor, tx.amount))
                    else: # AdvancedTransaction
                        interest_type_name = tx.interest_type.name if tx.interest_type else None
                        penalty_type_name = tx.penalty_type.name if tx.penalty_type else None
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount, 
                                                    borrow_date, due_date, interest_rate, penalty_fee,
                                                    interest_type_name, penalty_type_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (self.current_dataset_id, "advanced", tx.debtor, tx.creditor, tx.amount,
                              tx.borrow_date.strftime("%Y-%m-%d"),
                              tx.due_date.strftime("%Y-%m-%d"),
                              tx.interest_rate, tx.penalty_rate,
                              interest_type_name, penalty_type_name))
                
                conn.commit()
                if show_success_message:
                    messagebox.showinfo("Thành công", "Đã lưu các thay đổi vào bộ giao dịch hiện tại!")
        
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thay đổi: {e}")