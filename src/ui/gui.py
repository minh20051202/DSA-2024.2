import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
import sqlite3
import os
import sys

# Thêm đường dẫn để Python nhận diện thư mục src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import các core types và cấu trúc dữ liệu
from src.core_types.transaction import BasicTransaction, AdvancedTransaction
from src.core_types.date import Date
from src.data_structures.linked_list import LinkedList

# Import các thuật toán
try:
    from src.algorithms.basic_transactions.greedy import GreedySimplifier
    from src.algorithms.basic_transactions.dynamic_programming import DynamicProgrammingSimplifier
    from src.algorithms.basic_transactions.cycle_detector import DebtCycleSimplifier
    from src.algorithms.basic_transactions.min_cost_max_flow import MinCostMaxFlowSimplifier
except ImportError as e:
    print(f"Lỗi import thuật toán: {e}")
    raise

class DebtSimplifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Đơn giản hóa giao dịch")
        self.root.geometry("800x700")
        self.transactions = LinkedList()
        self.entries = {}
        self.mode_var = tk.StringVar(value="Cơ bản")
        self.algorithm_var = tk.StringVar(value="Greedy")
        self.dataset_name_var = tk.StringVar()
        self.current_dataset_id = None
        # Xác định đường dẫn đến thư mục database dựa trên vị trí của file gui.py
        self.base_dir = os.path.abspath(os.path.dirname(__file__))  # Thư mục chứa gui.py (src/ui)
        self.db_dir = os.path.join(self.base_dir, "..", "database")  # Thư mục src/database
        self.db_path = os.path.join(self.db_dir, "debt_simplifier.db")  # Đường dẫn đến debt_simplifier.db
        # Tạo thư mục database nếu chưa tồn tại
        os.makedirs(self.db_dir, exist_ok=True)
        self.setup_database()
        self.setup_gui()

    def setup_database(self):
        """Khởi tạo cơ sở dữ liệu SQLite và các bảng cần thiết."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Tạo bảng datasets
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS datasets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL
                    )
                ''')
                # Tạo bảng transactions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        debtor TEXT NOT NULL,
                        creditor TEXT NOT NULL,
                        amount REAL NOT NULL,
                        borrow_date TEXT,
                        due_date TEXT,
                        interest_rate REAL,
                        penalty_fee REAL,
                        status TEXT,
                        FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể khởi tạo cơ sở dữ liệu: {e}")

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

        # Khung quản lý bộ giao dịch
        dataset_frame = ttk.LabelFrame(main_frame, text="Quản lý bộ giao dịch", padding=10)
        dataset_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dataset_frame, text="Tên bộ giao dịch:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dataset_frame, textvariable=self.dataset_name_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(dataset_frame, text="Lưu bộ giao dịch", command=self.save_dataset).pack(side=tk.LEFT, padx=5)
        ttk.Button(dataset_frame, text="Tải bộ giao dịch", command=self.show_datasets).pack(side=tk.LEFT, padx=5)
        ttk.Button(dataset_frame, text="Lưu thay đổi", command=self.save_changes_to_dataset).pack(side=tk.LEFT, padx=5)

        # Khung nhập giao dịch
        input_frame = ttk.LabelFrame(main_frame, text="Nhập giao dịch", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        labels = [
            "Người nợ:", "Người cho vay:", "Số tiền:", "Ngày vay (dd/mm/yyyy):",
            "Ngày đến hạn (dd/mm/yyyy):", "Lãi suất (%/ngày):", "Phí phạt:"
        ]
        for i, label in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2
            ttk.Label(input_frame, text=label).grid(row=row, column=col, padx=5, pady=2, sticky="w")
            entry = ttk.Entry(input_frame, width=20)
            entry.grid(row=row, column=col + 1, padx=5, pady=2, sticky="ew")
            self.entries[label.replace(":", "")] = entry
        for i in range(4):
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
        self.setup_transaction_tab()
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Thống kê giao dịch")
        self.setup_stats_tab()
        self.result_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.result_tab, text="Kết quả tối ưu")
        self.setup_result_tab()
        self.toggle_mode()
        self.update_transaction_display()

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
        columns = ("STT", "Người nợ", "Người cho vay", "Số tiền", "Chi tiết")
        self.transaction_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        self.transaction_tree.heading("STT", text="STT")
        self.transaction_tree.heading("Người nợ", text="Người nợ")
        self.transaction_tree.heading("Người cho vay", text="Người cho vay")
        self.transaction_tree.heading("Số tiền", text="Số tiền")
        self.transaction_tree.heading("Chi tiết", text="Chi tiết")
        self.transaction_tree.column("STT", width=50, anchor=tk.CENTER)
        self.transaction_tree.column("Người nợ", width=120, anchor=tk.W)
        self.transaction_tree.column("Người cho vay", width=120, anchor=tk.W)
        self.transaction_tree.column("Số tiền", width=100, anchor=tk.E)
        self.transaction_tree.column("Chi tiết", width=300, anchor=tk.W)
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
        self.result_text = tk.Text(result_frame, height=20, wrap=tk.WORD, font=("Consolas", 10))
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
        self.stats_text = tk.Text(stats_frame, height=20, wrap=tk.WORD, font=("Consolas", 10))
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_stats = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.configure(yscrollcommand=scrollbar_stats.set)

    def toggle_mode(self):
        mode = self.mode_var.get()
        fields_to_toggle = ["Ngày vay (dd/mm/yyyy)", "Ngày đến hạn (dd/mm/yyyy)", "Lãi suất (%/ngày)", "Phí phạt"]
        state = "normal" if mode == "Nâng cao" else "disabled"
        for field in fields_to_toggle:
            self.entries[field].config(state=state)

    def save_dataset(self):
        """Lưu danh sách giao dịch hiện tại vào cơ sở dữ liệu."""
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
                # Kiểm tra xem tên bộ giao dịch đã tồn tại chưa
                cursor.execute("SELECT id FROM datasets WHERE name = ?", (dataset_name,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", f"Bộ giao dịch '{dataset_name}' đã tồn tại. Vui lòng chọn tên khác.")
                    return
                # Lưu bộ giao dịch
                cursor.execute("INSERT INTO datasets (name, created_at) VALUES (?, ?)",
                               (dataset_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                dataset_id = cursor.lastrowid
                # Lưu các giao dịch
                for tx in self.transactions:
                    if isinstance(tx, BasicTransaction):
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (dataset_id, "basic", tx.debtor, tx.creditor, tx.amount))
                    else:
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount, borrow_date, due_date, interest_rate, penalty_fee, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (dataset_id, "advanced", tx.debtor, tx.creditor, tx.amount,
                              f"{tx.borrow_date.year}-{tx.borrow_date.month:02}-{tx.borrow_date.day:02}",
                              f"{tx.due_date.year}-{tx.due_date.month:02}-{tx.due_date.day:02}",
                              tx.interest_rate, tx.penalty_fee, tx.status))
                conn.commit()
                messagebox.showinfo("Thành công", f"Đã lưu bộ giao dịch '{dataset_name}'!")
                self.dataset_name_var.set("")
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
                           command=lambda: self.load_dataset(dataset_tree)).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Xóa bộ giao dịch",
                           command=lambda: self.delete_dataset(dataset_tree)).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Đóng", command=dataset_window.destroy).pack(side=tk.LEFT, padx=5)
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bộ giao dịch: {e}")

    def load_dataset(self, tree):
        """Tải bộ giao dịch được chọn."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bộ giao dịch để tải.")
            return
        dataset_id = tree.item(selected[0])["values"][0]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM transactions WHERE dataset_id = ?", (dataset_id,))
                transactions = cursor.fetchall()
                self.transactions = LinkedList()
                for tx in transactions:
                    if tx[2] == "basic":
                        transaction = BasicTransaction(
                            debtor=tx[3],
                            creditor=tx[4],
                            amount=tx[5]
                        )
                    else:
                        borrow_date = datetime.strptime(tx[6], "%Y-%m-%d")
                        due_date = datetime.strptime(tx[7], "%Y-%m-%d")
                        transaction = AdvancedTransaction(
                            debtor=tx[3],
                            creditor=tx[4],
                            amount=tx[5],
                            borrow_date=Date(borrow_date.day, borrow_date.month, borrow_date.year),
                            due_date=Date(due_date.day, due_date.month, due_date.year),
                            interest_rate=tx[8],
                            penalty_fee=tx[9],
                            status=tx[10]
                        )
                    self.transactions.append(transaction)
                self.current_dataset_id = dataset_id
                self.update_transaction_display()
                messagebox.showinfo("Thành công", "Đã tải bộ giao dịch!")
                self.root.focus_force()
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể tải bộ giao dịch: {e}")

    def delete_dataset(self, tree):
        """Xóa bộ giao dịch được chọn."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bộ giao dịch để xóa.")
            return
        dataset_id = tree.item(selected[0])["values"][0]
        dataset_name = tree.item(selected[0])["values"][1]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa bộ giao dịch '{dataset_name}'?"):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (dataset_id,))
                    cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
                    conn.commit()
                    if self.current_dataset_id == dataset_id:
                        self.transactions = LinkedList()
                        self.current_dataset_id = None
                        self.update_transaction_display()
                    messagebox.showinfo("Thành công", f"Đã xóa bộ giao dịch '{dataset_name}'!")
                    tree.delete(selected[0])
            except sqlite3.Error as e:
                messagebox.showerror("Lỗi", f"Không thể xóa bộ giao dịch: {e}")

    def add_transaction(self):
        try:
            mode = self.mode_var.get()
            debtor = self.entries["Người nợ"].get().strip()
            creditor = self.entries["Người cho vay"].get().strip()
            amount = float(self.entries["Số tiền"].get())
            if not debtor or not creditor:
                raise ValueError("Người nợ và người cho vay không được để trống.")
            if debtor == creditor:
                raise ValueError("Người nợ và người cho vay không được trùng nhau.")
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")
            if mode == "Cơ bản":
                tx = BasicTransaction(
                    debtor=debtor,
                    creditor=creditor,
                    amount=amount
                )
            else:
                borrow_date_str = self.entries["Ngày vay (dd/mm/yyyy)"].get()
                due_date_str = self.entries["Ngày đến hạn (dd/mm/yyyy)"].get()
                interest_rate = float(self.entries["Lãi suất (%/ngày)"].get()) / 100
                penalty_fee = float(self.entries["Phí phạt"].get())
                if not borrow_date_str or not due_date_str:
                    raise ValueError("Ngày vay và ngày đến hạn không được để trống.")
                if interest_rate < 0 or penalty_fee < 0:
                    raise ValueError("Lãi suất và phí phạt không được âm.")
                borrow_date = datetime.strptime(borrow_date_str, "%d/%m/%Y")
                due_date = datetime.strptime(due_date_str, "%d/%m/%Y")
                if due_date < borrow_date:
                    raise ValueError("Ngày đến hạn phải sau ngày vay.")
                tx = AdvancedTransaction(
                    debtor=debtor,
                    creditor=creditor,
                    amount=amount,
                    borrow_date=Date(borrow_date.day, borrow_date.month, borrow_date.year),
                    due_date=Date(due_date.day, due_date.month, due_date.year),
                    interest_rate=interest_rate,
                    penalty_fee=penalty_fee,
                    status="pending"
                )
            self.transactions.append(tx)
            messagebox.showinfo("Thành công", "Đã thêm giao dịch!")
            self.clear_entries()
            self.update_transaction_display()
        except ValueError as ve:
            messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {ve}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def update_transaction_display(self):
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        if self.transactions.is_empty():
            self.transaction_tree.insert("", tk.END, values=("", "Không có giao dịch nào", "", "", ""))
            return
        for i, tx in enumerate(self.transactions, 1):
            if isinstance(tx, BasicTransaction):
                details = "Giao dịch cơ bản"
                self.transaction_tree.insert("", tk.END, values=(
                    i, tx.debtor, tx.creditor, f"{tx.amount:,.0f}", details
                ))
            else:
                details = f"Vay: {tx.borrow_date}, Hạn: {tx.due_date}, Lãi: {tx.interest_rate * 100:.1f}%/ngày, Phạt: {tx.penalty_fee:,.0f}"
                self.transaction_tree.insert("", tk.END, values=(
                    i, tx.debtor, tx.creditor, f"{tx.amount:,.0f}", details
                ))

    def edit_selected_transaction(self):
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một giao dịch để sửa.")
            return
        item = selected[0]
        index = int(self.transaction_tree.item(item)["values"][0]) - 1
        tx = self.transactions.get_at_index(index)
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Sửa giao dịch")
        edit_window.geometry("400x400")
        form_frame = ttk.Frame(edit_window, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(form_frame, text="Người nợ:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        debtor_entry = ttk.Entry(form_frame)
        debtor_entry.insert(0, tx.debtor)
        debtor_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="Người cho vay:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        creditor_entry = ttk.Entry(form_frame)
        creditor_entry.insert(0, tx.creditor)
        creditor_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="Số tiền:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        amount_entry = ttk.Entry(form_frame)
        amount_entry.insert(0, str(tx.amount))
        amount_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        advanced_widgets = []
        if isinstance(tx, AdvancedTransaction):
            ttk.Label(form_frame, text="Ngày vay (dd/mm/yyyy):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
            borrow_date_entry = ttk.Entry(form_frame)
            borrow_date_entry.insert(0, f"{tx.borrow_date.day:02}/{tx.borrow_date.month:02}/{tx.borrow_date.year}")
            borrow_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
            advanced_widgets.append(borrow_date_entry)
            ttk.Label(form_frame, text="Ngày đến hạn (dd/mm/yyyy):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
            due_date_entry = ttk.Entry(form_frame)
            due_date_entry.insert(0, f"{tx.due_date.day:02}/{tx.due_date.month:02}/{tx.due_date.year}")
            due_date_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
            advanced_widgets.append(due_date_entry)
            ttk.Label(form_frame, text="Lãi suất (%/ngày):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
            interest_entry = ttk.Entry(form_frame)
            interest_entry.insert(0, str(tx.interest_rate * 100))
            interest_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
            advanced_widgets.append(interest_entry)
            ttk.Label(form_frame, text="Phí phạt:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
            penalty_entry = ttk.Entry(form_frame)
            penalty_entry.insert(0, str(tx.penalty_fee))
            penalty_entry.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
            advanced_widgets.append(penalty_entry)
        form_frame.columnconfigure(1, weight=1)

        def save_changes():
            try:
                new_debtor = debtor_entry.get().strip()
                new_creditor = creditor_entry.get().strip()
                new_amount = float(amount_entry.get())
                if not new_debtor or not new_creditor:
                    raise ValueError("Người nợ và người cho vay không được để trống.")
                if new_debtor == new_creditor:
                    raise ValueError("Người nợ và người cho vay không được trùng nhau.")
                if new_amount <= 0:
                    raise ValueError("Số tiền phải lớn hơn 0.")
                if isinstance(tx, BasicTransaction):
                    updated_tx = BasicTransaction(
                        debtor=new_debtor,
                        creditor=new_creditor,
                        amount=new_amount
                    )
                else:
                    borrow_date = datetime.strptime(borrow_date_entry.get(), "%d/%m/%Y")
                    due_date = datetime.strptime(due_date_entry.get(), "%d/%m/%Y")
                    interest_rate = float(interest_entry.get()) / 100
                    penalty_fee = float(penalty_entry.get())
                    updated_tx = AdvancedTransaction(
                        debtor=new_debtor,
                        creditor=new_creditor,
                        amount=new_amount,
                        borrow_date=Date(borrow_date.day, borrow_date.month, borrow_date.year),
                        due_date=Date(due_date.day, due_date.month, due_date.year),
                        interest_rate=interest_rate,
                        penalty_fee=penalty_fee,
                        status=tx.status
                    )
                self.transactions.set_at(index, updated_tx)
                self.update_transaction_display()

                # Cập nhật cơ sở dữ liệu
                if self.current_dataset_id:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        # Lấy ID của giao dịch từ bảng transactions dựa trên vị trí trong danh sách
                        cursor.execute("SELECT id FROM transactions WHERE dataset_id = ? AND debtor = ? AND creditor = ? AND amount = ?",
                                       (self.current_dataset_id, tx.debtor, tx.creditor, tx.amount))
                        transaction_id = cursor.fetchone()
                        if transaction_id:
                            transaction_id = transaction_id[0]
                            if isinstance(updated_tx, BasicTransaction):
                                cursor.execute('''
                                    UPDATE transactions SET debtor = ?, creditor = ?, amount = ?, borrow_date = NULL, 
                                    due_date = NULL, interest_rate = NULL, penalty_fee = NULL, status = NULL
                                    WHERE id = ?
                                ''', (updated_tx.debtor, updated_tx.creditor, updated_tx.amount, transaction_id))
                            else:
                                cursor.execute('''
                                    UPDATE transactions SET debtor = ?, creditor = ?, amount = ?, borrow_date = ?, 
                                    due_date = ?, interest_rate = ?, penalty_fee = ?, status = ?
                                    WHERE id = ?
                                ''', (updated_tx.debtor, updated_tx.creditor, updated_tx.amount,
                                      f"{updated_tx.borrow_date.year}-{updated_tx.borrow_date.month:02}-{updated_tx.borrow_date.day:02}",
                                      f"{updated_tx.due_date.year}-{updated_tx.due_date.month:02}-{updated_tx.due_date.day:02}",
                                      updated_tx.interest_rate, updated_tx.penalty_fee, updated_tx.status, transaction_id))
                            conn.commit()
                            messagebox.showinfo("Thành công", "Đã cập nhật giao dịch và lưu vào cơ sở dữ liệu!")
                        else:
                            messagebox.showwarning("Cảnh báo", "Không tìm thấy giao dịch để cập nhật trong cơ sở dữ liệu.")
                else:
                    messagebox.showwarning("Cảnh báo", "Không có bộ giao dịch hiện tại để lưu thay đổi.")

                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {ve}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

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
            index = int(self.transaction_tree.item(item)["values"][0]) - 1  # Chỉ số trong danh sách (bắt đầu từ 0)
            try:
                tx = self.transactions.get_at_index(index)
                self.transactions.remove_at_index(index)
                self.update_transaction_display()
                # Cập nhật cơ sở dữ liệu
                if self.current_dataset_id:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM transactions WHERE dataset_id = ? AND debtor = ? AND creditor = ? AND amount = ?",
                                       (self.current_dataset_id, tx.debtor, tx.creditor, tx.amount))
                        transaction_id = cursor.fetchone()
                        if transaction_id:
                            transaction_id = transaction_id[0]
                            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                            conn.commit()
                            messagebox.showinfo("Thành công", "Đã xóa giao dịch và cập nhật cơ sở dữ liệu!")
                        else:
                            messagebox.showwarning("Cảnh báo", "Không tìm thấy giao dịch để xóa trong cơ sở dữ liệu.")
                else:
                    messagebox.showwarning("Cảnh báo", "Không có bộ giao dịch hiện tại để lưu thay đổi.")
            except IndexError as e:
                messagebox.showerror("Lỗi", f"Không thể xóa giao dịch: {e}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def delete_all_transactions(self):
        if self.transactions.is_empty():
            messagebox.showinfo("Thông báo", "Không có giao dịch nào để xóa.")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tất cả giao dịch?"):
            self.transactions = LinkedList()
            self.update_transaction_display()
            self.clear_result()
            # Cập nhật cơ sở dữ liệu
            if self.current_dataset_id:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (self.current_dataset_id,))
                    conn.commit()
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
            algorithm = self.algorithm_var.get()
            self.result_text.delete(1.0, tk.END)
            self.stats_text.delete(1.0, tk.END)
            self.notebook.select(1)
            self.result_text.insert(tk.END, f"🎯 KẾT QUẢ TỐI ƯU HÓA ({algorithm}):\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")
            if self.transactions.is_empty():
                self.result_text.insert(tk.END, "❌ Không có giao dịch nào để tối ưu hóa.\n")
                self.stats_text.insert(tk.END, "❌ Không có giao dịch nào để thống kê.\n")
                return
            basic_transactions = LinkedList()
            original_count = 0
            for tx in self.transactions:
                if isinstance(tx, AdvancedTransaction):
                    amount = tx.amount
                    if tx.status == "pending":
                        today = datetime.now()
                        due_date = datetime(tx.due_date.year, tx.due_date.month, tx.due_date.day)
                        if today > due_date:
                            days_overdue = (today - due_date).days
                            interest = amount * tx.interest_rate * days_overdue
                            amount += interest + tx.penalty_fee
                    basic_tx = BasicTransaction(
                        debtor=tx.debtor,
                        creditor=tx.creditor,
                        amount=amount
                    )
                else:
                    amount = tx.amount
                    basic_tx = tx
                basic_transactions.append(basic_tx)
                original_count += 1
            if algorithm == "Greedy":
                simplifier = GreedySimplifier(basic_transactions)
                result = simplifier.simplify()
            elif algorithm == "Dynamic Programming":
                simplifier = DynamicProgrammingSimplifier(basic_transactions)
                result = simplifier.simplify()
            elif algorithm == "Cycle Detector":
                simplifier = DebtCycleSimplifier(basic_transactions)
                result = simplifier.simplify()
            elif algorithm == "Min-Cost Max-Flow":
                simplifier = MinCostMaxFlowSimplifier(basic_transactions)
                result = simplifier.simplify()
            else:
                raise ValueError("Thuật toán không hợp lệ.")
            total_optimized = 0
            optimized_count = 0
            if result.is_empty():
                self.result_text.insert(tk.END, "✅ Không cần giao dịch nào - Tất cả đã được bù trừ!\n")
            else:
                for i, tx in enumerate(result, 1):
                    self.result_text.insert(tk.END, f"{i}. {tx.debtor} → {tx.creditor}: {tx.amount:,.0f}\n")
                    total_optimized += tx.amount
                    optimized_count += 1
            self.result_text.insert(tk.END, f"\n📊 Số giao dịch trước tối ưu: {original_count}\n")
            self.result_text.insert(tk.END, f"📊 Số giao dịch sau tối ưu: {optimized_count}\n")
            self.result_text.insert(tk.END,
                                   f"📉 Giảm số giao dịch: {original_count - optimized_count} ({((original_count - optimized_count) / original_count * 100):,.1f}%)\n\n")
            balance = defaultdict(float)
            for tx in result:
                balance[tx.debtor] -= tx.amount
                balance[tx.creditor] += tx.amount
            self.stats_text.insert(tk.END, "💰 SỐ DƯ TỪNG NGƯỜI:\n")
            self.stats_text.insert(tk.END, "-" * 30 + "\n")
            for person, amount in sorted(balance.items()):
                if amount < 0:
                    display_amount = f"-{abs(amount):,.0f}"
                    status = "phải trả"
                elif amount > 0:
                    display_amount = f"{amount:,.0f}"
                    status = "được nhận"
                else:
                    display_amount = "0"
                    status = "cân bằng"
                self.stats_text.insert(tk.END, f"{person}: {display_amount} ({status})\n")
            total_balance = sum(balance.values())
            self.stats_text.insert(tk.END, f"\n🔢 Tổng số dư: {total_balance:,.0f}\n")
            if abs(total_balance) < 1e-6:
                self.stats_text.insert(tk.END, "✅ Tổng số dư bằng 0\n")
            else:
                self.stats_text.insert(tk.END, "❌ Lỗi tối ưu hóa: Tổng số dư không bằng 0\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"❌ Lỗi khi tối ưu hóa: {e}\n")
            self.stats_text.insert(tk.END, f"❌ Lỗi khi thống kê: {e}\n")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi tối ưu hóa: {e}")

    def save_changes_to_dataset(self):
        """Lưu lại các thay đổi vào bộ giao dịch hiện tại trong cơ sở dữ liệu."""
        if not self.current_dataset_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng tải một bộ giao dịch trước khi lưu thay đổi.")
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Xóa tất cả giao dịch cũ của bộ hiện tại
                cursor.execute("DELETE FROM transactions WHERE dataset_id = ?", (self.current_dataset_id,))
                # Lưu lại toàn bộ danh sách giao dịch hiện tại
                for tx in self.transactions:
                    if isinstance(tx, BasicTransaction):
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (self.current_dataset_id, "basic", tx.debtor, tx.creditor, tx.amount))
                    else:
                        cursor.execute('''
                            INSERT INTO transactions (dataset_id, type, debtor, creditor, amount, borrow_date, due_date, interest_rate, penalty_fee, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (self.current_dataset_id, "advanced", tx.debtor, tx.creditor, tx.amount,
                              f"{tx.borrow_date.year}-{tx.borrow_date.month:02}-{tx.borrow_date.day:02}",
                              f"{tx.due_date.year}-{tx.due_date.month:02}-{tx.due_date.day:02}",
                              tx.interest_rate, tx.penalty_fee, tx.status))
                conn.commit()
                messagebox.showinfo("Thành công", "Đã lưu các thay đổi vào bộ giao dịch hiện tại!")
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thay đổi: {e}")
