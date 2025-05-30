import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import csv
import os
import sys
import json
import traceback
import logging
import sqlite3  
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.data_structures.transaction_graph import TransactionGraph
import src.algorithms.simplification as algorithms

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debt_simplifier_gui")

class DebtSimplifierApp:
    def __init__(self, root):
        """
        Initialize the Debt Simplification GUI application
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Tối ưu hóa dòng tiền")
        self.root.geometry("1920x1080")  # Set window size to 1920x1080 (full HD)
        self.root.minsize(1400, 900)  # Increased minimum window size for better usability

        # Set application icon (if running on Windows)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Initialize theme
        self.style = ttk.Style()
        self.current_theme = "flatly"  # Default to light theme
        self.style.theme_use(self.current_theme)

        # Initialize the data structures
        self.transaction_graph = TransactionGraph()  # Use our custom graph data structure
        self.simplified_transactions = []  # Store simplified transactions

        # SQLite database path (custom directory)
        database_dir = r"C:\Users\Admin\Desktop\2024.2\GTS\Baitap\DSA-2024.2-main\src\database"
        # Đảm bảo thư mục tồn tại, nếu không thì tạo mới
        os.makedirs(database_dir, exist_ok=True)
        self.db_path = os.path.join(database_dir, "debt_simplifier.db")

        # Initialize SQLite database
        self._initialize_database()

        # Create main frame with dark background
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a top frame for theme toggle button
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Theme toggle button
        self.theme_button = ttk.Button(
            self.top_frame,
            text="🌙 Chuyển sang chế độ tối",
            command=self._toggle_theme,
            bootstyle="secondary"
        )
        self.theme_button.pack(side=tk.RIGHT)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.tab_add = ttk.Frame(self.notebook)
        self.tab_view = ttk.Frame(self.notebook)
        self.tab_simplified = ttk.Frame(self.notebook)
        self.tab_visualization = ttk.Frame(self.notebook)  # Visualization tab

        self.notebook.add(self.tab_add, text="Thêm giao dịch")
        self.notebook.add(self.tab_view, text="Thống kê giao dịch")
        self.notebook.add(self.tab_simplified, text="Giao dịch đã tối ưu")
        self.notebook.add(self.tab_visualization, text="Hình ảnh hóa")  # Add visualization tab

        # Create the tab contents
        self._create_add_tab()
        self._create_view_tab()
        self._create_simplified_tab()
        self._create_visualization_tab()  # Create visualization tab content

        # Add a separator
        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Add a status bar
        self.status_bar = ttk.Label(self.main_frame, text="", anchor=tk.W, padding=(10, 5))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        if self.current_theme == "flatly":
            self.current_theme = "darkly"
            self.theme_button.config(text="☀ Chuyển sang chế độ sáng", bootstyle="light")
        else:
            self.current_theme = "flatly"
            self.theme_button.config(text="🌙 Chuyển sang chế độ tối", bootstyle="secondary")
        self.style.theme_use(self.current_theme)
        self.status_bar.config(text="Đã chuyển đổi giao diện.")

    def _initialize_database(self):
        """Initialize the SQLite database and create giao_dich and giao_dich_toi_uu tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create giao_dich table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS giao_dich (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nguoi_no TEXT NOT NULL,
                    chu_no TEXT NOT NULL,
                    so_tien REAL NOT NULL
                )
            ''')

            # Create giao_dich_toi_uu table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS giao_dich_toi_uu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nguoi_no TEXT NOT NULL,
                    chu_no TEXT NOT NULL,
                    so_tien REAL NOT NULL,
                    phuong_phap TEXT NOT NULL
                )
            ''')

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể khởi tạo cơ sở dữ liệu: {str(e)}")
            logger.error(f"Database initialization error: {str(e)}")

    def _save_transactions_to_database(self):
        """Save all transactions to the SQLite giao_dich table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Clear existing transactions
            cursor.execute("DELETE FROM giao_dich")
            # Insert current transactions
            for t in self.transaction_graph.transactions:
                cursor.execute(
                    "INSERT INTO giao_dich (nguoi_no, chu_no, so_tien) VALUES (?, ?, ?)",
                    (t["debtor"], t["creditor"], t["amount"])
                )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Dữ liệu giao dịch gốc đã được lưu vào cơ sở dữ liệu.")
            self.status_bar.config(text="Đã lưu dữ liệu giao dịch gốc.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu giao dịch gốc: {str(e)}")
            logger.error(f"Save transactions error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể lưu dữ liệu giao dịch gốc.")

    def _save_simplified_to_database(self, method):
        """Save simplified transactions to the SQLite giao_dich_toi_uu table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Clear existing simplified transactions for this method
            cursor.execute("DELETE FROM giao_dich_toi_uu WHERE phuong_phap = ?", (method,))
            # Insert current simplified transactions
            for t in self.simplified_transactions:
                cursor.execute(
                    "INSERT INTO giao_dich_toi_uu (nguoi_no, chu_no, so_tien, phuong_phap) VALUES (?, ?, ?, ?)",
                    (t["debtor"], t["creditor"], t["amount"], method)
                )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Dữ liệu giao dịch đã tối ưu đã được lưu vào cơ sở dữ liệu.")
            self.status_bar.config(text="Đã lưu dữ liệu giao dịch đã tối ưu.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu giao dịch đã tối ưu: {str(e)}")
            logger.error(f"Save simplified error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể lưu dữ liệu giao dịch đã tối ưu.")

    def _load_transactions_from_database(self):
        """Load transactions from the SQLite giao_dich table."""
        if self.transaction_graph.transactions:
            confirm = messagebox.askyesno("Xác nhận",
                                          "Thao tác này sẽ xóa tất cả giao dịch hiện có. Bạn có muốn tiếp tục?")
            if not confirm:
                return

        self._clear_all_data()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nguoi_no, chu_no, so_tien FROM giao_dich")
            transactions = cursor.fetchall()
            for t in transactions:
                nguoi_no, chu_no, so_tien = t
                self.transaction_graph.add_transaction(nguoi_no, chu_no, so_tien)
                self.transactions_tree.insert("", "end", values=(nguoi_no, chu_no, f"{so_tien:.2f}"))
            cursor.close()
            conn.close()
            self._refresh_balances()
            messagebox.showinfo("Thành công", "Dữ liệu giao dịch gốc đã được tải từ cơ sở dữ liệu.")
            self.status_bar.config(text="Đã tải dữ liệu giao dịch gốc.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu giao dịch gốc: {str(e)}")
            logger.error(f"Load transactions error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể tải dữ liệu giao dịch gốc.")

    def _load_simplified_from_database(self):
        """Load simplified transactions from the SQLite giao_dich_toi_uu table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nguoi_no, chu_no, so_tien, phuong_phap FROM giao_dich_toi_uu")
            simplified = cursor.fetchall()
            self.simplified_transactions = []
            for t in simplified:
                nguoi_no, chu_no, so_tien, phuong_phap = t
                self.simplified_transactions.append({
                    "debtor": nguoi_no,
                    "creditor": chu_no,
                    "amount": so_tien
                })
                self.simplified_tree.insert("", "end", values=(nguoi_no, chu_no, f"{so_tien:.2f}"))
            if simplified:
                method = simplified[0][3]  # phuong_phap from the first record
                stats = algorithms.calculate_reduction_stats(self.transaction_graph.transactions, self.simplified_transactions)
                status_text = (f"Phương pháp: {method} | "
                               f"Giảm từ {stats['original_count']} xuống {stats['simplified_count']} giao dịch "
                               f"({stats['reduction_percent']:.1f}% giảm)")
                self.status_var.set(status_text)
            cursor.close()
            conn.close()
            self.status_bar.config(text="Đã tải dữ liệu giao dịch đã tối ưu.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu giao dịch đã tối ưu: {str(e)}")
            logger.error(f"Load simplified error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể tải dữ liệu giao dịch đã tối ưu.")

    def _edit_transaction(self):
        """Edit the selected transaction in the giao_dich table."""
        selected_item = self.transactions_tree.selection()
        if not selected_item:
            messagebox.showinfo("Lựa chọn", "Vui lòng chọn một giao dịch để chỉnh sửa.")
            return

        # Get values from the selected item
        item_values = self.transactions_tree.item(selected_item[0], "values")
        debtor = item_values[0]
        creditor = item_values[1]
        amount = float(item_values[2])

        # Open dialog for editing
        new_debtor = simpledialog.askstring("Chỉnh sửa", "Người nợ:", initialvalue=debtor)
        if new_debtor is None:
            return
        new_creditor = simpledialog.askstring("Chỉnh sửa", "Chủ nợ:", initialvalue=creditor)
        if new_creditor is None:
            return
        new_amount = simpledialog.askfloat("Chỉnh sửa", "Số tiền ($):", initialvalue=amount)
        if new_amount is None:
            return

        # Validate input
        if not new_debtor or not new_creditor or new_amount <= 0:
            messagebox.showwarning("Lỗi đầu vào", "Thông tin không hợp lệ.")
            return

        # Update in transaction graph
        self.transaction_graph.remove_transaction(debtor, creditor, amount)
        self.transaction_graph.add_transaction(new_debtor, new_creditor, new_amount)

        # Update in treeview
        self.transactions_tree.item(selected_item, values=(new_debtor, new_creditor, f"{new_amount:.2f}"))

        # Update in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE giao_dich SET nguoi_no = ?, chu_no = ?, so_tien = ? WHERE nguoi_no = ? AND chu_no = ? AND so_tien = ?",
                (new_debtor, new_creditor, new_amount, debtor, creditor, amount)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật giao dịch trong cơ sở dữ liệu: {str(e)}")
            logger.error(f"Update transaction error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể cập nhật giao dịch.")
            return

        # Refresh balances and clear other views
        self._refresh_balances()
        self._clear_view('all')
        messagebox.showinfo("Thành công", "Giao dịch đã được chỉnh sửa.")
        self.status_bar.config(text="Đã chỉnh sửa giao dịch.")

    def _edit_simplified_transaction(self):
        """Edit the selected simplified transaction in the giao_dich_toi_uu table."""
        selected_item = self.simplified_tree.selection()
        if not selected_item:
            messagebox.showinfo("Lựa chọn", "Vui lòng chọn một giao dịch đã tối ưu để chỉnh sửa.")
            return

        # Get values from the selected item
        item_values = self.simplified_tree.item(selected_item[0], "values")
        debtor = item_values[0]
        creditor = item_values[1]
        amount = float(item_values[2])

        # Open dialog for editing
        new_debtor = simpledialog.askstring("Chỉnh sửa", "Người nợ:", initialvalue=debtor)
        if new_debtor is None:
            return
        new_creditor = simpledialog.askstring("Chỉnh sửa", "Chủ nợ:", initialvalue=creditor)
        if new_creditor is None:
            return
        new_amount = simpledialog.askfloat("Chỉnh sửa", "Số tiền ($):", initialvalue=amount)
        if new_amount is None:
            return

        # Validate input
        if not new_debtor or not new_creditor or new_amount <= 0:
            messagebox.showwarning("Lỗi đầu vào", "Thông tin không hợp lệ.")
            return

        # Update in simplified_transactions list
        for t in self.simplified_transactions:
            if t["debtor"] == debtor and t["creditor"] == creditor and t["amount"] == amount:
                t["debtor"] = new_debtor
                t["creditor"] = new_creditor
                t["amount"] = new_amount
                break

        # Update in treeview
        self.simplified_tree.item(selected_item, values=(new_debtor, new_creditor, f"{new_amount:.2f}"))

        # Update in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE giao_dich_toi_uu SET nguoi_no = ?, chu_no = ?, so_tien = ? WHERE nguoi_no = ? AND chu_no = ? AND so_tien = ?",
                (new_debtor, new_creditor, new_amount, debtor, creditor, amount)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật giao dịch đã tối ưu trong cơ sở dữ liệu: {str(e)}")
            logger.error(f"Update simplified transaction error: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể cập nhật giao dịch đã tối ưu.")
            return

        messagebox.showinfo("Thành công", "Giao dịch đã tối ưu đã được chỉnh sửa.")
        self.status_bar.config(text="Đã chỉnh sửa giao dịch đã tối ưu.")

    def _create_add_tab(self):
        """Create the Add Transactions tab"""
        # Frame for input
        input_frame = ttk.LabelFrame(self.tab_add, text="Giao dịch mới", padding="15")
        input_frame.pack(fill=tk.X, padx=15, pady=15)

        # Debtor (who owes)
        ttk.Label(input_frame, text="Người nợ:", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.debtor_var = tk.StringVar()
        self.debtor_entry = ttk.Entry(input_frame, textvariable=self.debtor_var, width=30, font=("Arial", 11))
        self.debtor_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Creditor (who is owed)
        ttk.Label(input_frame, text="Chủ nợ:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.creditor_var = tk.StringVar()
        self.creditor_entry = ttk.Entry(input_frame, textvariable=self.creditor_var, width=30, font=("Arial", 11))
        self.creditor_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Amount
        ttk.Label(input_frame, text="Số tiền ($):", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=30, font=("Arial", 11))
        self.amount_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Add transaction button
        ttk.Button(input_frame, text="➕ Thêm giao dịch", command=self._add_transaction, bootstyle="success").grid(row=3, column=0, columnspan=2, pady=10)

        # Separator
        ttk.Separator(self.tab_add, orient="horizontal").pack(fill=tk.X, padx=15, pady=10)

        # Recent transactions list
        ttk.Label(self.tab_add, text="Giao dịch gần đây:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=15, pady=(10, 5))

        # Frame for the transactions list
        transactions_frame = ttk.Frame(self.tab_add)
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(transactions_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for transactions
        self.transactions_tree = ttk.Treeview(transactions_frame, show="headings",
                                              columns=("nguoi_no", "chu_no", "so_tien"),
                                              yscrollcommand=scrollbar_y.set)

        # Configure columns
        self.transactions_tree.column("nguoi_no", width=300)
        self.transactions_tree.column("chu_no", width=300)
        self.transactions_tree.column("so_tien", width=200)

        # Configure headers
        self.transactions_tree.heading("nguoi_no", text="Người nợ")
        self.transactions_tree.heading("chu_no", text="Chủ nợ")
        self.transactions_tree.heading("so_tien", text="Số tiền ($)")

        # Pack treeview
        self.transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        scrollbar_y.config(command=self.transactions_tree.yview)

        # Create a frame for the buttons
        button_frame = ttk.Frame(self.tab_add)
        button_frame.pack(fill=tk.X, padx=15, pady=10)

        # Delete transaction button
        ttk.Button(button_frame, text="🗑️ Xóa giao dịch đã chọn", command=self._delete_transaction,
                   bootstyle="danger").pack(side=tk.LEFT, padx=(0, 5))

        # Edit transaction button
        ttk.Button(button_frame, text="✏️ Chỉnh sửa giao dịch", command=self._edit_transaction,
                   bootstyle="warning").pack(side=tk.LEFT, padx=5)

        # Clear all transactions button
        ttk.Button(button_frame, text="🧹 Xóa tất cả giao dịch", command=self._clear_all_transactions,
                   bootstyle="danger").pack(side=tk.LEFT, padx=5)

        # Save and load buttons
        ttk.Button(button_frame, text="💾 Lưu dữ liệu", command=self._save_transactions_to_database,
                   bootstyle="primary").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 Tải dữ liệu", command=self._load_transactions_from_database,
                   bootstyle="primary").pack(side=tk.LEFT, padx=5)

        # Import transactions button
        ttk.Button(button_frame, text="📥 Nhập giao dịch", command=self._load_sample_transactions,
                   bootstyle="info").pack(side=tk.LEFT, padx=5)

    def _clear_all_transactions(self):
        """Clear all transactions after confirmation."""
        if not self.transaction_graph.transactions:
            messagebox.showinfo("Không có giao dịch", "Không có giao dịch nào để xóa.")
            return

        confirm = messagebox.askyesno("Xác nhận",
                                      "Bạn có chắc chắn muốn xóa tất cả giao dịch không? Hành động này không thể hoàn tác.")
        if confirm:
            self._clear_all_data()
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM giao_dich")
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu trong cơ sở dữ liệu: {str(e)}")
                logger.error(f"Clear transactions error: {str(e)}")
                self.status_bar.config(text="Lỗi: Không thể xóa dữ liệu giao dịch.")
                return
            messagebox.showinfo("Thành công", "Đã xóa tất cả giao dịch.")
            self.status_bar.config(text="Đã xóa tất cả giao dịch.")

    def _create_view_tab(self):
        """Create the View Transactions tab with balances"""
        # Frame for balances
        balances_frame = ttk.LabelFrame(self.tab_view, text="Số dư ròng", padding="15")
        balances_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(balances_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for balances
        self.balances_tree = ttk.Treeview(balances_frame, show="headings",
                                          columns=("person", "amount", "status"),
                                          yscrollcommand=scrollbar_y.set)

        # Configure columns
        self.balances_tree.column("person", width=300)
        self.balances_tree.column("amount", width=200)
        self.balances_tree.column("status", width=200)

        # Configure headers
        self.balances_tree.heading("person", text="Người")
        self.balances_tree.heading("amount", text="Số tiền ($)")
        self.balances_tree.heading("status", text="Trạng thái")

        # Pack treeview
        self.balances_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        scrollbar_y.config(command=self.balances_tree.yview)

        # Refresh button
        ttk.Button(self.tab_view, text="🔄 Làm mới số dư", command=self._refresh_balances, bootstyle="info").pack(
            anchor=tk.W, padx=15, pady=5)

    def _create_simplified_tab(self):
        """Create the Simplified Debts tab"""
        # Top frame with explanation and simplify button
        top_frame = ttk.Frame(self.tab_simplified, padding="15")
        top_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(top_frame, text="Nhấn 'Tối ưu hóa nợ' để tính toán số lượng giao dịch tối thiểu:",
                  font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

        # Add algorithm selection dropdown
        ttk.Label(top_frame, text="Phương pháp:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(10, 5))
        self.algorithm_var = tk.StringVar(value="greedy")
        algorithm_dropdown = ttk.Combobox(top_frame, textvariable=self.algorithm_var, width=15, state="readonly",
                                          font=("Arial", 11))
        algorithm_dropdown['values'] = (
            "greedy", "dual_heap", "cycle", "graph_flow", "priority_queue"
        )
        algorithm_dropdown.pack(side=tk.LEFT, padx=5)

        # Add tooltip for algorithm selection
        self.algorithm_tooltip = tk.Label(top_frame, text="?", font=("Arial", 10, "bold"),
                                          bg="lightblue", fg="blue", padx=5, pady=0)
        self.algorithm_tooltip.pack(side=tk.LEFT)
        self.algorithm_tooltip.bind("<Enter>", self._show_algorithm_tooltip)
        self.algorithm_tooltip.bind("<Leave>", self._hide_algorithm_tooltip)

        ttk.Button(top_frame, text="🔄 Tối ưu hóa nợ", command=self._simplify_debts, bootstyle="success").pack(
            side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self.tab_simplified, orient="horizontal").pack(fill=tk.X, padx=15, pady=10)

        # Frame for simplified transactions
        simplified_frame = ttk.LabelFrame(self.tab_simplified, text="Giao dịch đã tối ưu", padding="15")
        simplified_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(simplified_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for simplified transactions
        self.simplified_tree = ttk.Treeview(simplified_frame, show="headings",
                                            columns=("nguoi_no", "chu_no", "so_tien"),
                                            yscrollcommand=scrollbar_y.set)

        # Configure columns
        self.simplified_tree.column("nguoi_no", width=300)
        self.simplified_tree.column("chu_no", width=300)
        self.simplified_tree.column("so_tien", width=200)

        # Configure headers
        self.simplified_tree.heading("nguoi_no", text="Người nợ")
        self.simplified_tree.heading("chu_no", text="Chủ nợ")
        self.simplified_tree.heading("so_tien", text="Số tiền ($)")

        # Pack treeview
        self.simplified_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        scrollbar_y.config(command=self.simplified_tree.yview)

        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Chưa thực hiện tối ưu hóa.")
        ttk.Label(self.tab_simplified, textvariable=self.status_var, font=("Arial", 11)).pack(anchor=tk.W, padx=15,
                                                                                              pady=5)

        # Export buttons
        export_frame = ttk.Frame(self.tab_simplified)
        export_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(export_frame, text="📊 Hình ảnh hóa", command=self._visualize_debts, bootstyle="info").pack(
            side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="✏️ Chỉnh sửa giao dịch", command=self._edit_simplified_transaction,
                   bootstyle="warning").pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📂 Tải giao dịch đã tối ưu", command=self._load_simplified_from_database,
                   bootstyle="primary").pack(side=tk.LEFT, padx=5)

    def _show_algorithm_tooltip(self, event):
        """Show tooltip for algorithm selection"""
        tooltip_window = tk.Toplevel(self.root)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        tooltip_text = """
        Các phương pháp tối ưu hóa nợ có sẵn:

        greedy: Thuật toán tham lam tiêu chuẩn (khớp người nợ lớn nhất với chủ nợ lớn nhất)
        dual_heap: Sử dụng max heap cho người nợ và min heap cho chủ nợ
        cycle: Phát hiện và loại bỏ các chu kỳ nợ trước khi khớp
        graph_flow: Mô hình hóa tối ưu hóa nợ như một bài toán luồng chi phí tối thiểu trên đồ thị
        priority_queue: Sử dụng hàng đợi ưu tiên để tối ưu hóa thứ tự thanh toán dựa trên số tiền nợ
        """

        label = tk.Label(tooltip_window, text=tooltip_text, justify=tk.LEFT,
                         background="#ffffcc", relief=tk.SOLID, borderwidth=1, padx=5, pady=5)
        label.pack()

        self.tooltip_window = tooltip_window

    def _hide_algorithm_tooltip(self, event):
        """Hide tooltip for algorithm selection"""
        if hasattr(self, 'tooltip_window'):
            self.tooltip_window.destroy()
            delattr(self, 'tooltip_window')

    def _create_visualization_tab(self):
        """Create the Visualization tab with a list-based interface"""
        # Top frame with explanation and visualization button
        top_frame = ttk.Frame(self.tab_visualization, padding="15")
        top_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(top_frame, text="Nhấn 'Hình ảnh hóa nợ' để hiển thị danh sách giao dịch:", font=("Arial", 12)).pack(
            side=tk.LEFT, padx=5)
        visualize_button = ttk.Button(top_frame, text="📊 Hình ảnh hóa nợ", command=self._visualize_debts,
                                      bootstyle="info")
        visualize_button.pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self.tab_visualization, orient="horizontal").pack(fill=tk.X, padx=15, pady=10)

        # Frame for visualization
        visualization_frame = ttk.LabelFrame(self.tab_visualization, text="Danh sách giao dịch", padding="15")
        visualization_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create a frame to hold both original and simplified transactions
        self.viz_container = ttk.Frame(visualization_frame)
        self.viz_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Create a message label that will be shown initially
        self.viz_message = ttk.Label(
            self.viz_container,
            text="Nhấn 'Hình ảnh hóa nợ' để hiển thị danh sách giao dịch",
            font=("Arial", 18, "bold"),
            padding=40,
            anchor="center"
        )
        self.viz_message.pack(expand=True, fill=tk.BOTH)

        # Create frames for original and simplified transactions (initially hidden)
        self.original_frame = ttk.Frame(self.viz_container)
        self.simplified_frame = ttk.Frame(self.viz_container)

        # Original transactions label
        ttk.Label(self.original_frame, text="Giao dịch gốc", font=("Arial", 16, "bold")).pack(anchor=tk.W, padx=5,
                                                                                              pady=5)

        # Scrollbar for original transactions
        original_scrollbar_y = ttk.Scrollbar(self.original_frame)
        original_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for original transactions
        self.original_tree = ttk.Treeview(self.original_frame, show="headings",
                                          columns=("so_tien", "huong_giao_dich"),
                                          yscrollcommand=original_scrollbar_y.set)

        # Configure columns
        self.original_tree.column("so_tien", width=150)
        self.original_tree.column("huong_giao_dich", width=300)

        # Configure headers
        self.original_tree.heading("so_tien", text="Số tiền ($)")
        self.original_tree.heading("huong_giao_dich", text="Hướng giao dịch")

        # Pack treeview
        self.original_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        original_scrollbar_y.config(command=self.original_tree.yview)

        # Simplified transactions label
        ttk.Label(self.simplified_frame, text="Giao dịch đã tối ưu", font=("Arial", 16, "bold")).pack(anchor=tk.W,
                                                                                                      padx=5, pady=5)

        # Scrollbar for simplified transactions
        simplified_scrollbar_y = ttk.Scrollbar(self.simplified_frame)
        simplified_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for simplified transactions
        self.simplified_tree_viz = ttk.Treeview(self.simplified_frame, show="headings",
                                                columns=("so_tien", "huong_giao_dich"),
                                                yscrollcommand=simplified_scrollbar_y.set)

        # Configure columns
        self.simplified_tree_viz.column("so_tien", width=150)
        self.simplified_tree_viz.column("huong_giao_dich", width=300)

        # Configure headers
        self.simplified_tree_viz.heading("so_tien", text="Số tiền ($)")
        self.simplified_tree_viz.heading("huong_giao_dich", text="Hướng giao dịch")

        # Pack treeview
        self.simplified_tree_viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        simplified_scrollbar_y.config(command=self.simplified_tree_viz.yview)

    def _add_transaction(self):
        """Add a transaction from the input fields to the transaction graph."""
        try:
            # Get values from input fields
            debtor = self.debtor_var.get().strip()
            creditor = self.creditor_var.get().strip()
            amount_str = self.amount_var.get().strip()

            # Validate input
            if not debtor:
                messagebox.showwarning("Lỗi đầu vào", "Vui lòng nhập tên người nợ.")
                return

            if not creditor:
                messagebox.showwarning("Lỗi đầu vào", "Vui lòng nhập tên chủ nợ.")
                return

            if not amount_str:
                messagebox.showwarning("Lỗi đầu vào", "Vui lòng nhập số tiền.")
                return

            # Try to convert amount to float
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showwarning("Lỗi đầu vào", "Số tiền phải là số dương.")
                    return
            except ValueError:
                messagebox.showwarning("Lỗi đầu vào", "Số tiền phải là một số hợp lệ.")
                return

            # Add transaction to the graph
            transaction = self.transaction_graph.add_transaction(debtor, creditor, amount)

            # Add to treeview
            self.transactions_tree.insert("", "end", values=(debtor, creditor, f"{amount:.2f}"))

            # Clear input fields
            self.debtor_var.set("")
            self.creditor_var.set("")
            self.amount_var.set("")

            # Focus on debtor field for next entry
            self.debtor_entry.focus()

            # Refresh balances view
            self._refresh_balances()

            # Clear simplified view and visualization as they're now out of date
            self._clear_view('all')

            self.status_bar.config(text="Đã thêm giao dịch thành công.")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể thêm giao dịch.")

    def _delete_transaction(self):
        """Delete the selected transaction from the transaction graph after confirmation."""
        # Get selected item
        selected_item = self.transactions_tree.selection()

        if not selected_item:
            messagebox.showinfo("Lựa chọn", "Vui lòng chọn một giao dịch để xóa.")
            return

        # Get values from the selected item
        item_values = self.transactions_tree.item(selected_item[0], "values")
        debtor = item_values[0]
        creditor = item_values[1]
        amount = float(item_values[2])

        # Show confirmation dialog
        confirm = messagebox.askyesno("Xác nhận",
                                      f"Bạn có chắc chắn muốn xóa giao dịch: {debtor} → {creditor} (${amount:.2f}) không? Hành động này không thể hoàn tác.")
        if not confirm:
            return

        # Remove transaction from the graph
        success = self.transaction_graph.remove_transaction(debtor, creditor, amount)

        if success:
            # Remove from treeview
            self.transactions_tree.delete(selected_item)

            # Remove from database
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM giao_dich WHERE nguoi_no = ? AND chu_no = ? AND so_tien = ?",
                    (debtor, creditor, amount)
                )
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa giao dịch trong cơ sở dữ liệu: {str(e)}")
                logger.error(f"Delete transaction error: {str(e)}")
                self.status_bar.config(text="Lỗi: Không thể xóa giao dịch.")
                return

            # Refresh balances view
            self._refresh_balances()

            # Clear simplified view and visualization as they're now out of date
            self._clear_view('all')
            messagebox.showinfo("Thành công", "Giao dịch đã được xóa.")
            self.status_bar.config(text="Đã xóa giao dịch.")
        else:
            messagebox.showwarning("Lỗi", "Không tìm thấy giao dịch để xóa.")

    def _refresh_balances(self):
        """Refresh the balances treeview with current balance information."""
        # Clear existing items
        for item in self.balances_tree.get_children():
            self.balances_tree.delete(item)

        # Add balances to treeview using our custom data structures
        balance_keys = self.transaction_graph.balance.keys()
        current = balance_keys.head

        row_index = 0
        while current:
            person = current.data
            amount = self.transaction_graph.balance.get(person)

            if abs(amount) < 1e-9:  # Near zero
                status = "Đã thanh toán"
                amount_display = "0.00"
            elif amount > 0:
                status = "Được nhận"
                amount_display = f"{amount:.2f}"
            else:
                status = "Đang nợ"
                amount_display = f"{-amount:.2f}"

            self.balances_tree.insert("", "end", values=(person, amount_display, status))

            current = current.next
            row_index += 1

    def _simplify_debts(self):
        """Simplify debts using the selected algorithm and display the results."""
        if not self.transaction_graph.transactions:
            messagebox.showinfo("Không có giao dịch", "Không có giao dịch nào để tối ưu hóa.")
            return

        # Get the selected approach
        approach = self.algorithm_var.get()

        try:
            # Use the algorithm module to simplify debts with the selected approach
            self.simplified_transactions = algorithms.simplify_debts_with_approach(
                self.transaction_graph, approach=approach)

            # Clear existing items in the simplified transactions treeview
            for item in self.simplified_tree.get_children():
                self.simplified_tree.delete(item)

            # Add simplified transactions to treeview
            for i, t in enumerate(self.simplified_transactions):
                self.simplified_tree.insert("", "end", values=(
                    t["debtor"], t["creditor"], f"{t['amount']:.2f}"))

            # Calculate reduction statistics
            stats = algorithms.calculate_reduction_stats(
                self.transaction_graph.transactions,
                self.simplified_transactions
            )

            # Update status text
            status_text = (f"Phương pháp: {approach} | "
                           f"Giảm từ {stats['original_count']} xuống {stats['simplified_count']} giao dịch "
                           f"({stats['reduction_percent']:.1f}% giảm)")
            self.status_var.set(status_text)

            # Save simplified transactions to database
            self._save_simplified_to_database(approach)

            # Switch to the Simplified Debts tab
            self.notebook.select(self.tab_simplified)

            self.status_bar.config(text="Đã tối ưu hóa giao dịch.")

        except Exception as e:
            messagebox.showerror("Lỗi tối ưu hóa", f"Đã xảy ra lỗi: {str(e)}")
            logger.error(f"Simplification error: {str(e)}", exc_info=True)
            self.status_bar.config(text="Lỗi: Không thể tối ưu hóa giao dịch.")

    def _clear_view(self, view_type):
        """
        Clear a specific view in the application.

        Args:
            view_type (str): Type of view to clear ('simplified', 'visualization', or 'all')
        """
        if view_type in ('simplified', 'all'):
            # Clear simplified treeview
            for item in self.simplified_tree.get_children():
                self.simplified_tree.delete(item)

            # Reset status
            self.status_var.set("Chưa thực hiện tối ưu hóa.")

            # Clear stored simplified transactions
            self.simplified_transactions = []

        if view_type in ('visualization', 'all'):
            # Clear the visualization treeviews
            for item in self.original_tree.get_children():
                self.original_tree.delete(item)
            for item in self.simplified_tree_viz.get_children():
                self.simplified_tree_viz.delete(item)

            # Hide the visualization frames
            self.original_frame.pack_forget()
            self.simplified_frame.pack_forget()

            # Show the message label
            self.viz_message.pack(expand=True, fill=tk.BOTH)

    def _load_sample_transactions(self):
        """Load transactions from a sample CSV file selected by the user."""
        # First check if tests/sample_transactions.csv exists as a default suggestion
        default_dir = ""
        tests_sample_file = os.path.join("tests", "sample_transactions.csv")
        if os.path.exists(tests_sample_file):
            default_dir = "tests"

        # Open file dialog to select the sample transactions file
        file_path = filedialog.askopenfilename(
            title="Chọn tệp CSV giao dịch mẫu",
            filetypes=[("Tệp CSV", "*.csv"), ("Tất cả tệp", "*.*")],
            initialdir=default_dir
        )

        if not file_path:
            return  # User cancelled

        # Ask for confirmation if data already exists
        if self.transaction_graph.transactions:
            confirm = messagebox.askyesno("Xác nhận",
                                          "Thao tác này sẽ xóa tất cả giao dịch hiện có. Bạn có muốn tiếp tục?")
            if not confirm:
                return

        # Clear existing data
        self._clear_all_data()

        # Load transactions from CSV
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header

                successful_count = 0
                for row in reader:
                    if len(row) >= 3:  # Expecting debtor, creditor, amount
                        try:
                            debtor = row[0].strip()
                            creditor = row[1].strip()
                            amount = float(row[2].strip())

                            # Add to transactions graph
                            self.transaction_graph.add_transaction(debtor, creditor, amount)

                            # Add to treeview
                            self.transactions_tree.insert("", "end", values=(
                                debtor, creditor, f"{amount:.2f}"))

                            successful_count += 1
                        except Exception as e:
                            logger.error(f"Error processing row {row}: {str(e)}")

            if successful_count == 0:
                raise Exception("Failed to load any transactions from the sample file")

            # Refresh balances view
            self._refresh_balances()

            # Show success message
            messagebox.showinfo("Giao dịch mẫu",
                                f"Đã tải thành công {successful_count} giao dịch từ {os.path.basename(file_path)}")
            self.status_bar.config(text=f"Đã nhập {successful_count} giao dịch từ tệp CSV.")

        except Exception as e:
            logger.error(f"Error loading sample transactions: {str(e)}")
            messagebox.showerror("Lỗi", f"Không thể tải giao dịch mẫu: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể nhập giao dịch từ tệp CSV.")
            return

    def _show_about(self):
        """Show about dialog"""
        about_text = """Tối ưu hóa nợ

Một công cụ để giảm thiểu số lượng giao dịch cần thiết để thanh toán nợ trong một nhóm.

Thuật toán:
- Tính toán số dư ròng cho mỗi người
- Khớp người nợ với chủ nợ một cách tối ưu
- Giảm tổng số giao dịch

Triển khai nhiều thuật toán tối ưu hóa nợ.
"""
        messagebox.showinfo("Giới thiệu", about_text)

    def _visualize_debts(self):
        """Display the original and simplified transactions in a list format."""
        try:
            if not self.transaction_graph.transactions:
                messagebox.showinfo("Không có giao dịch", "Không có giao dịch nào để hình ảnh hóa.")
                return

            # Hide the message and show the transaction lists
            self.viz_message.pack_forget()

            # Pack the frames
            self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.simplified_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Clear existing items
            for item in self.original_tree.get_children():
                self.original_tree.delete(item)
            for item in self.simplified_tree_viz.get_children():
                self.simplified_tree_viz.delete(item)

            # Populate original transactions
            for i, t in enumerate(self.transaction_graph.transactions):
                direction = f"{t['debtor']} → {t['creditor']}"
                self.original_tree.insert("", "end", values=(
                    f"${t['amount']:.2f}",
                    direction
                ))

            # Run simplification if not already done
            if not hasattr(self, 'simplified_transactions') or not self.simplified_transactions:
                self._simplify_debts()

            # Populate simplified transactions
            if hasattr(self, 'simplified_transactions') and self.simplified_transactions:
                for i, t in enumerate(self.simplified_transactions):
                    direction = f"{t['debtor']} → {t['creditor']}"
                    self.simplified_tree_viz.insert("", "end", values=(
                        f"${t['amount']:.2f}",
                        direction
                    ))

            # Switch to the visualization tab
            self.notebook.select(self.tab_visualization)

            self.status_bar.config(text="Đã hiển thị danh sách giao dịch.")

        except Exception as e:
            logger.error(f"Error in visualization: {str(e)}")
            messagebox.showerror("Lỗi hình ảnh hóa", f"Đã xảy ra lỗi khi hình ảnh hóa: {str(e)}")
            self.status_bar.config(text="Lỗi: Không thể hình ảnh hóa giao dịch.")

    def _clear_all_data(self):
        """Clear all data and reset the application state."""
        # Clear the transaction graph
        self.transaction_graph.clear()

        # Clear transaction treeview
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        # Clear balances treeview
        for item in self.balances_tree.get_children():
            self.balances_tree.delete(item)

        # Clear simplified view and visualization
        self._clear_view('all')

def main():
    """Main function to run the application"""
    root = ttk.Window(themename="flatly")  # Start with light theme
    app = DebtSimplifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
