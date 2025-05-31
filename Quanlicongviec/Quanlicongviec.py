import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import hashlib
from datetime import datetime
import requests 


USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"
SUGGESTED_TASKS_CACHE_FILE = "suggested_tasks_cache.json"
ADMIN_DEFAULT = {
    "username": "admin",
    "password": "admin123",
    "fullname": "Admin M",
    "role": "admin"
}


def load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path == SUGGESTED_TASKS_CACHE_FILE:
                 json.dump({"last_fetched_success_timestamp": "",
                            "etag": "",
                            "last_modified": "",
                            "suggested_tasks_data": []}, f, indent=4)
            else:
                json.dump([], f)
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            if file_path == SUGGESTED_TASKS_CACHE_FILE:
                return {"last_fetched_success_timestamp": "", "etag": "", "last_modified": "", "suggested_tasks_data": []}
            return []

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Hàm băm mật khẩu ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# --- Lớp ứng dụng chính ---
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng Dụng Quản Lý Công Việc Cá Nhân")
        self.root.geometry("850x650")
        self.root.configure(bg="#F0F2F5")
        self.current_user = None
        
        
        self.suggested_tasks_gist_url = "https://gist.githubusercontent.com/Nhan-create/5fb9c1bc8a5fd7ee3f544f1ea5abad5d/raw/task_templates_cache.json" 
        
        self.entries_add_task = {}
        self.entries_edit_task = {}
        self.task_map_for_chooser = {}

        self.ensure_files_exist()
        self.ensure_admin_exists()
        self.init_login()

    def ensure_files_exist(self):
        for file_path in [USERS_FILE, TASKS_FILE, SUGGESTED_TASKS_CACHE_FILE]:
            if not os.path.exists(file_path):
                load_json(file_path)

    def ensure_admin_exists(self):
        users = load_json(USERS_FILE)
        if not any(u['username'] == ADMIN_DEFAULT['username'] for u in users):
            admin_data = ADMIN_DEFAULT.copy()
            admin_data['password'] = hash_password(admin_data['password'])
            users.append(admin_data)
            save_json(USERS_FILE, users)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_styled_label(self, parent, text, font_size=12, bold=False, anchor="w", justify="left"):
        font_style = ("Arial", font_size)
        if bold:
            font_style = ("Arial", font_size, "bold")
        label = tk.Label(parent, text=text, font=font_style, bg="#F0F2F5", fg="#333333", anchor=anchor, justify=justify)
        return label

    def create_styled_button(self, parent, text, command, bg_color="#007bff", fg_color="white", width=15):
        return tk.Button(parent, text=text, command=command,
                         font=("Arial", 11), bg=bg_color, fg=fg_color,
                         width=width, relief="flat", padx=10, pady=5,
                         activebackground=bg_color, activeforeground=fg_color)

    def init_login(self):
        self.current_user = None
        self.clear_frame()
        login_frame = tk.Frame(self.root, bg="#F0F2F5", padx=30, pady=30, bd=2, relief="groove")
        login_frame.pack(expand=True, anchor="center")
        self.create_styled_label(login_frame, "Đăng Nhập", font_size=18, bold=True, anchor="center").pack(pady=15)
        self.create_styled_label(login_frame, "Tài khoản", anchor="w").pack(pady=(10, 0), fill="x")
        self.ent_user = ttk.Entry(login_frame, font=("Arial", 12), width=30)
        self.ent_user.pack(pady=5)
        self.ent_user.focus()
        self.create_styled_label(login_frame, "Mật khẩu", anchor="w").pack(pady=(10, 0), fill="x")
        self.ent_pass = ttk.Entry(login_frame, show="*", font=("Arial", 12), width=30)
        self.ent_pass.pack(pady=5)
        self.create_styled_button(login_frame, "Đăng nhập", self.login, bg_color="#28a745", width=25).pack(pady=15)
        self.create_styled_button(login_frame, "Đăng ký tài khoản người dùng", self.init_register, bg_color="#17a2b8", fg_color="white", width=25).pack(pady=5)

    def login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()
        if not username or not password:
            messagebox.showerror("Lỗi Đăng Nhập", "Vui lòng nhập tài khoản và mật khẩu.", parent=self.root)
            return
        hashed_password = hash_password(password)
        users = load_json(USERS_FILE)
        for user in users:
            if user['username'] == username and user['password'] == hashed_password:
                self.current_user = user
                self.init_main()
                return
        messagebox.showerror("Lỗi Đăng Nhập", "Sai tài khoản hoặc mật khẩu.", parent=self.root)

    def init_register(self):
        self.clear_frame()
        register_frame = tk.Frame(self.root, bg="#F0F2F5", padx=30, pady=30, bd=2, relief="groove")
        register_frame.pack(expand=True, anchor="center")
        self.create_styled_label(register_frame, "Đăng ký tài khoản", font_size=16, bold=True, anchor="center").pack(pady=15)
        self.create_styled_label(register_frame, "Tài khoản", anchor="w").pack(pady=(10, 0), fill="x")
        self.reg_user = ttk.Entry(register_frame, font=("Arial", 12), width=30)
        self.reg_user.pack(pady=5)
        self.reg_user.focus()
        self.create_styled_label(register_frame, "Mật khẩu", anchor="w").pack(pady=(10, 0), fill="x")
        self.reg_pass = ttk.Entry(register_frame, show="*", font=("Arial", 12), width=30)
        self.reg_pass.pack(pady=5)
        self.create_styled_label(register_frame, "Họ tên", anchor="w").pack(pady=(10, 0), fill="x")
        self.reg_fullname = ttk.Entry(register_frame, font=("Arial", 12), width=30)
        self.reg_fullname.pack(pady=5)
        self.create_styled_button(register_frame, "Tạo tài khoản", self.register_user, bg_color="#007bff", width=25).pack(pady=15)
        self.create_styled_button(register_frame, "Quay lại", self.init_login, bg_color="#6c757d", width=25).pack(pady=5)

    def register_user(self):
        username = self.reg_user.get().strip()
        password = self.reg_pass.get().strip()
        fullname = self.reg_fullname.get().strip()
        if not username or not password or not fullname:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ thông tin.", parent=self.root)
            return
        users = load_json(USERS_FILE)
        if any(u['username'] == username for u in users):
            messagebox.showwarning("Tài khoản đã tồn tại", "Tài khoản này đã được đăng ký.", parent=self.root)
            return
        hashed_password = hash_password(password)
        users.append({"username": username, "password": hashed_password, "fullname": fullname, "role": "user"})
        save_json(USERS_FILE, users)
        messagebox.showinfo("Thành công", "Đăng ký tài khoản thành công! Bây giờ bạn có thể đăng nhập.", parent=self.root)
        self.init_login()

    def init_main(self):
        self.clear_frame()
        main_frame = tk.Frame(self.root, bg="#F0F2F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        welcome_text = f"Xin chào {self.current_user['fullname']} ({self.current_user['role']})"
        self.create_styled_label(main_frame, welcome_text, font_size=16, bold=True, anchor="center").pack(pady=20)
        btn_frame = tk.Frame(main_frame, bg="#F0F2F5")
        btn_frame.pack(pady=10)
        row_num = 0
        if self.current_user['role'] == 'admin':
            self.create_styled_button(btn_frame, "Quản lý người dùng", self.view_users, width=25).grid(row=row_num, column=0, padx=10, pady=5)
            self.create_styled_button(btn_frame, "Thông tin tài khoản", self.edit_account_info, width=25).grid(row=row_num, column=1, padx=10, pady=5)
            self.create_styled_button(btn_frame, "Đăng xuất", self.init_login, bg_color="#dc3545", width=25).grid(row=row_num, column=2, padx=10, pady=5)
        else:
            self.create_styled_button(btn_frame, "Danh sách công việc", lambda: self.view_tasks(self.current_user['username']), width=25).grid(row=row_num, column=0, padx=10, pady=5)
            self.create_styled_button(btn_frame, "Thông tin tài khoản", self.edit_account_info, width=25).grid(row=row_num, column=1, padx=10, pady=5)
            self.create_styled_button(btn_frame, "Đăng xuất", self.init_login, bg_color="#dc3545", width=25).grid(row=row_num, column=2, padx=10, pady=5)

    def edit_account_info(self):
        self.clear_frame()
        edit_frame = tk.Frame(self.root, bg="#F0F2F5", padx=30, pady=30, bd=2, relief="groove")
        edit_frame.pack(expand=True, anchor="center")
        self.create_styled_label(edit_frame, "Cập nhật thông tin tài khoản", font_size=16, bold=True, anchor="center").pack(pady=15)
        self.create_styled_label(edit_frame, "Mật khẩu cũ (bắt buộc để thay đổi)", anchor="w").pack(pady=(10,0), fill="x")
        old_pass_entry = ttk.Entry(edit_frame, font=("Arial", 12), show="*", width=30)
        old_pass_entry.pack(pady=5)
        old_pass_entry.focus()
        self.create_styled_label(edit_frame, "Tài khoản mới (để trống nếu không đổi)", anchor="w").pack(pady=(10, 0), fill="x")
        new_user_entry = ttk.Entry(edit_frame, font=("Arial", 12), width=30)
        new_user_entry.insert(0, self.current_user['username'])
        new_user_entry.pack(pady=5)
        self.create_styled_label(edit_frame, "Mật khẩu mới (để trống nếu không đổi)", anchor="w").pack(pady=(10, 0), fill="x")
        new_pass_entry = ttk.Entry(edit_frame, font=("Arial", 12), show="*", width=30)
        new_pass_entry.pack(pady=5)
        self.create_styled_label(edit_frame, "Họ tên mới (để trống nếu không đổi)", anchor="w").pack(pady=(10, 0), fill="x")
        new_name_entry = ttk.Entry(edit_frame, font=("Arial", 12), width=30)
        new_name_entry.insert(0, self.current_user['fullname'])
        new_name_entry.pack(pady=5)

        def save_changes():
            entered_old_pass = old_pass_entry.get().strip()
            updated_username_val = new_user_entry.get().strip()
            updated_pass_val = new_pass_entry.get().strip()
            updated_name_val = new_name_entry.get().strip()
            if not entered_old_pass:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mật khẩu cũ để xác thực.", parent=self.root)
                return
            if hash_password(entered_old_pass) != self.current_user['password']:
                messagebox.showerror("Lỗi Xác Thực", "Mật khẩu cũ không đúng.", parent=self.root)
                return
            users = load_json(USERS_FILE)
            tasks_data = load_json(TASKS_FILE)
            original_username = self.current_user['username']
            user_to_update_index = -1
            for i, u in enumerate(users):
                if u['username'] == original_username:
                    user_to_update_index = i
                    break
            if user_to_update_index == -1:
                messagebox.showerror("Lỗi", "Không tìm thấy tài khoản hiện tại trong hệ thống.", parent=self.root)
                self.init_main()
                return
            user_data_changed = False
            current_user_copy_for_update = users[user_to_update_index].copy()
            if updated_username_val and updated_username_val != original_username:
                if any(u['username'] == updated_username_val for u in users if u['username'] != original_username):
                    messagebox.showwarning("Lỗi", f"Tài khoản '{updated_username_val}' đã tồn tại. Vui lòng chọn tên khác.", parent=self.root)
                    return
                current_user_copy_for_update['username'] = updated_username_val
                user_data_changed = True
            elif not updated_username_val:
                 current_user_copy_for_update['username'] = original_username
            if updated_pass_val:
                current_user_copy_for_update['password'] = hash_password(updated_pass_val)
                user_data_changed = True
            if updated_name_val and updated_name_val != self.current_user.get('fullname', ''):
                current_user_copy_for_update['fullname'] = updated_name_val
                user_data_changed = True
            elif not updated_name_val :
                 current_user_copy_for_update['fullname'] = self.current_user.get('fullname', '')
            if not user_data_changed:
                messagebox.showinfo("Thông báo", "Không có thông tin nào được thay đổi.", parent=self.root)
                return
            users[user_to_update_index] = current_user_copy_for_update
            save_json(USERS_FILE, users)
            self.current_user = current_user_copy_for_update
            if current_user_copy_for_update['username'] != original_username:
                tasks_changed_flag = False
                for task in tasks_data:
                    if task.get('username') == original_username:
                        task['username'] = current_user_copy_for_update['username']
                        tasks_changed_flag = True
                if tasks_changed_flag:
                    save_json(TASKS_FILE, tasks_data)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin tài khoản.", parent=self.root)
            self.init_main()

        btn_container = tk.Frame(edit_frame, bg="#F0F2F5")
        btn_container.pack(pady=20)
        self.create_styled_button(btn_container, "Lưu thay đổi", save_changes, bg_color="#28a745", width=15).grid(row=0, column=0, padx=5, pady=5)
        self.create_styled_button(btn_container, "Quay lại", self.init_main, bg_color="#6c757d", width=15).grid(row=0, column=1, padx=5, pady=5)
        self.create_styled_button(btn_container, "Xóa tài khoản này", self.prompt_self_delete_account, bg_color="#dc3545", width=20).grid(row=1, column=0, columnspan=2, padx=5, pady=10)

    def prompt_self_delete_account(self):
        if self.current_user['username'] == ADMIN_DEFAULT['username'] and self.current_user['role'] == 'admin':
            messagebox.showerror("Không thể xóa", "Không thể xóa tài khoản admin mặc định.", parent=self.root)
            return
        confirm_delete_window = tk.Toplevel(self.root)
        confirm_delete_window.title("Xác nhận xóa tài khoản")
        confirm_delete_window.geometry("450x250")
        confirm_delete_window.configure(bg="#F0F2F5")
        confirm_delete_window.transient(self.root)
        confirm_delete_window.grab_set()
        tk.Label(confirm_delete_window,
                 text="CẢNH BÁO!\nHành động này sẽ xóa vĩnh viễn tài khoản của bạn\nvà tất cả dữ liệu liên quan (bao gồm công việc).\nKhông thể hoàn tác.",
                 font=("Arial", 11, "bold"), fg="red", bg="#F0F2F5", justify="center").pack(pady=15)
        tk.Label(confirm_delete_window, text="Để xác nhận, vui lòng nhập mật khẩu hiện tại của bạn:",
                 font=("Arial", 10), bg="#F0F2F5").pack(pady=(5,0))
        password_entry_confirm = ttk.Entry(confirm_delete_window, show="*", font=("Arial", 11), width=25)
        password_entry_confirm.pack(pady=5)
        password_entry_confirm.focus()
        btn_frame_confirm = tk.Frame(confirm_delete_window, bg="#F0F2F5")
        btn_frame_confirm.pack(pady=15)
        confirm_button = self.create_styled_button(btn_frame_confirm, "Xác nhận xóa",
                                   lambda: self._perform_self_delete_account(password_entry_confirm.get(), confirm_delete_window),
                                   bg_color="#dc3545", width=15)
        confirm_button.grid(row=0, column=0, padx=10)
        cancel_button = self.create_styled_button(btn_frame_confirm, "Hủy bỏ",
                                  confirm_delete_window.destroy,
                                  bg_color="#6c757d", width=15)
        cancel_button.grid(row=0, column=1, padx=10)

    def _perform_self_delete_account(self, entered_password, confirm_window):
        if not entered_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu.", parent=confirm_window)
            return
        if hash_password(entered_password) != self.current_user['password']:
            messagebox.showerror("Lỗi", "Mật khẩu không đúng.", parent=confirm_window)
            return
        confirm_window.destroy()
        username_to_delete = self.current_user['username']
        users = load_json(USERS_FILE)
        users_after_deletion = [u for u in users if u['username'] != username_to_delete]
        tasks = load_json(TASKS_FILE)
        tasks_after_deletion = [t for t in tasks if t.get('username') != username_to_delete]
        if len(users) != len(users_after_deletion):
            save_json(USERS_FILE, users_after_deletion)
            save_json(TASKS_FILE, tasks_after_deletion)
            messagebox.showinfo("Thành công", "Tài khoản của bạn và tất cả dữ liệu liên quan đã được xóa thành công.", parent=self.root)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản để xóa. Vui lòng thử lại.", parent=self.root)
        self.current_user = None
        self.init_login()

    def get_user_tasks(self, username_to_filter_by):
        tasks = load_json(TASKS_FILE)
        return [t for t in tasks if t.get('username') == username_to_filter_by]

    def get_fullname_from_username(self, username_to_find):
        users = load_json(USERS_FILE)
        for user in users:
            if user['username'] == username_to_find:
                return user.get('fullname', username_to_find)
        return username_to_find

    def view_tasks(self, username_for_tasks):
        self.clear_frame()
        display_name_for_title = self.get_fullname_from_username(username_for_tasks)
        is_admin_viewing_other_user = (self.current_user['role'] == 'admin' and
                                       username_for_tasks != self.current_user['username'])
        self.create_styled_label(self.root, f"Danh sách công việc của {display_name_for_title}",
                                 font_size=16, bold=True, anchor="center").pack(pady=10)
        tasks_for_display = self.get_user_tasks(username_for_tasks)
        tree_container = tk.Frame(self.root)
        tree_container.pack(pady=(0,5), padx=20, fill="both", expand=True)
        cols = ("ID", "Tiêu đề", "Mô tả", "Ưu tiên", "Ngày bắt đầu", "Hạn chót")
        self.task_tree = ttk.Treeview(tree_container, columns=cols, show="headings", height=15)
        scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.task_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.task_tree.pack(side="left", fill="both", expand=True)
        for col_name in cols:
            self.task_tree.heading(col_name, text=col_name)
        self.task_tree.column("ID", width=50, minwidth=40, anchor="center")
        self.task_tree.column("Tiêu đề", width=200, minwidth=150, anchor="w")
        self.task_tree.column("Mô tả", width=300, minwidth=200, anchor="w")
        self.task_tree.column("Ưu tiên", width=100, minwidth=80, anchor="center")
        self.task_tree.column("Ngày bắt đầu", width=120, minwidth=100, anchor="center")
        self.task_tree.column("Hạn chót", width=120, minwidth=100, anchor="center")
        for i, task in enumerate(tasks_for_display):
            task_iid = str(task.get('task_id', i))
            self.task_tree.insert("", tk.END, iid=task_iid, values=(
                task.get('task_id', 'N/A'),
                task.get('title', ''),
                task.get('description', ''),
                task.get('priority', ''),
                task.get('start_date', ''),
                task.get('due_date', '')
            ))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#e0e0e0", foreground="#333333")
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.map('Treeview', background=[('selected', '#a0a0a0')])
        task_btn_frame = tk.Frame(self.root, bg="#F0F2F5")
        task_btn_frame.pack(pady=10, fill="x")
        add_cmd = lambda: self.add_task(username_for_tasks)
        edit_cmd = lambda: self.edit_task(username_for_tasks)
        delete_cmd = lambda: self.delete_task(username_for_tasks)
        back_cmd = self.view_users if is_admin_viewing_other_user else self.init_main
        self.create_styled_button(task_btn_frame, "Thêm", add_cmd, bg_color="#28a745", width=12).pack(side="left", padx=(10,5), pady=5)
        self.create_styled_button(task_btn_frame, "Sửa", edit_cmd, bg_color="#ffc107", fg_color="#333333", width=12).pack(side="left", padx=5, pady=5)
        self.create_styled_button(task_btn_frame, "Xóa", delete_cmd, bg_color="#dc3545", width=12).pack(side="left", padx=5, pady=5)
        self.create_styled_button(task_btn_frame, "Quay lại", back_cmd, bg_color="#6c757d", width=12).pack(side="right", padx=(5,10), pady=5)

    def validate_dates(self, start_date_str, due_date_str):
        try:
            start_dt = datetime.strptime(start_date_str, "%d-%m-%Y").date()
            due_dt = datetime.strptime(due_date_str, "%d-%m-%Y").date()
            if due_dt < start_dt:
                messagebox.showwarning("Lỗi thời gian", "Hạn chót không được trước ngày bắt đầu.", parent=self.root)
                return False
            return True
        except ValueError:
            messagebox.showwarning("Lỗi định dạng", "Vui lòng nhập đúng định dạng ngày (DD-MM-YYYY).", parent=self.root)
            return False

    def add_task(self, target_username_for_task):
        self.clear_frame()
        display_name = self.get_fullname_from_username(target_username_for_task)
        add_task_main_frame = tk.Frame(self.root, bg="#F0F2F5")
        add_task_main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.create_styled_label(add_task_main_frame, f"Thêm công việc cho {display_name}",
                                 font_size=16, bold=True, anchor="center").pack(pady=(0,15))
        form_frame = tk.Frame(add_task_main_frame, bg="#F0F2F5")
        form_frame.pack(pady=10)
        fields_info = {
            "Tiêu đề": {"type": "entry", "key": "title"},
            "Mô tả": {"type": "text_widget", "key": "description"},
            "Mức độ ưu tiên": {"type": "combobox", "values": ["Cao", "Trung bình", "Thấp"], "default": "Trung bình", "key": "priority"},
            "Ngày bắt đầu (DD-MM-YYYY)": {"type": "entry", "default_now": True, "key": "start_date"},
            "Hạn chót (DD-MM-YYYY)": {"type": "entry", "key": "due_date"}
        }
        self.entries_add_task = {}
        for i, (field_text, info) in enumerate(fields_info.items()):
            self.create_styled_label(form_frame, field_text, anchor="w").grid(row=i, column=0, sticky="nsew", pady=5, padx=5)
            if info["type"] == "combobox":
                entry = ttk.Combobox(form_frame, font=("Arial", 12), values=info["values"], width=38, state="readonly")
                entry.set(info["default"])
            elif info["type"] == "text_widget":
                entry = tk.Text(form_frame, font=("Arial", 12), width=40, height=5, wrap=tk.WORD)
                desc_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=entry.yview)
                entry.configure(yscrollcommand=desc_scrollbar.set)
                desc_scrollbar.grid(row=i, column=2, sticky="ns", pady=5, padx=(0,5))
            else:
                entry = ttk.Entry(form_frame, font=("Arial", 12), width=40)
                if info.get("default_now"):
                    entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries_add_task[info["key"]] = entry
        if "title" in self.entries_add_task: self.entries_add_task["title"].focus()
        form_frame.grid_columnconfigure(1, weight=1)
        btn_choose_suggested = self.create_styled_button(form_frame, "Chọn CV Gợi Ý...",
                                                        self._show_suggested_task_chooser,
                                                        bg_color="#5bc0de", width=18)
        btn_choose_suggested.grid(row=len(fields_info), column=0, columnspan=3, pady=10, padx=5, sticky="ew")
        def save_task_action():
            data_to_save = {}
            for key_info_label, widget_info_key in fields_info.items():
                widget_key = widget_info_key['key']
                widget = self.entries_add_task[widget_key]
                if isinstance(widget, tk.Text):
                    data_to_save[widget_key] = widget.get("1.0", tk.END).strip()
                else:
                    data_to_save[widget_key] = widget.get().strip()
            if not data_to_save["title"] or not data_to_save["priority"] or \
               not data_to_save["start_date"] or not data_to_save["due_date"]:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường bắt buộc (Tiêu đề, Ưu tiên, Ngày bắt đầu, Hạn chót).", parent=self.root)
                return
            if not self.validate_dates(data_to_save["start_date"], data_to_save["due_date"]): return
            all_tasks = load_json(TASKS_FILE)
            new_task_id = max([t.get('task_id', 0) for t in all_tasks] + [0]) + 1
            task_entry = { "task_id": new_task_id, "username": target_username_for_task, **data_to_save }
            all_tasks.append(task_entry)
            save_json(TASKS_FILE, all_tasks)
            messagebox.showinfo("Thành công", "Đã thêm công việc mới.", parent=self.root)
            self.view_tasks(target_username_for_task)
        add_task_btn_frame = tk.Frame(add_task_main_frame, bg="#F0F2F5")
        add_task_btn_frame.pack(pady=(10,0))
        self.create_styled_button(add_task_btn_frame, "Lưu công việc", save_task_action, bg_color="#28a745", width=20).grid(row=0, column=0, padx=5)
        self.create_styled_button(add_task_btn_frame, "Quay lại", lambda: self.view_tasks(target_username_for_task), bg_color="#6c757d", width=20).grid(row=0, column=1, padx=5)

    def _get_task_from_selection(self, target_username_of_task):
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một công việc.", parent=self.root)
            return None, -1
        selected_iid = selected_items[0]
        all_tasks = load_json(TASKS_FILE)
        try:
            task_id_to_find = int(selected_iid)
            for i, task in enumerate(all_tasks):
                if task.get('task_id') == task_id_to_find and task.get('username') == target_username_of_task:
                    return task, i
        except ValueError:
            messagebox.showerror("Lỗi IID", "IID của công việc không hợp lệ.", parent=self.root)
            return None, -1
        messagebox.showerror("Lỗi", f"Không tìm thấy công việc với ID {selected_iid} cho người dùng {target_username_of_task}.", parent=self.root)
        return None, -1

    def edit_task(self, target_username_of_task):
        original_task_data, task_index_in_all_tasks = self._get_task_from_selection(target_username_of_task)
        if original_task_data is None:
            return
        self.clear_frame()
        display_name = self.get_fullname_from_username(target_username_of_task)
        edit_task_main_frame = tk.Frame(self.root, bg="#F0F2F5")
        edit_task_main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.create_styled_label(edit_task_main_frame, f"Sửa công việc của {display_name}",
                                 font_size=16, bold=True, anchor="center").pack(pady=(0,15))
        form_frame = tk.Frame(edit_task_main_frame, bg="#F0F2F5")
        form_frame.pack(pady=10)
        fields_info_edit = {
            "Tiêu đề": {"key": "title", "value": original_task_data.get('title', '')},
            "Mô tả": {"key": "description", "value": original_task_data.get('description', ''), "type": "text_widget"},
            "Mức độ ưu tiên": {"key": "priority", "value": original_task_data.get('priority', 'Trung bình'), "type": "combobox", "values": ["Cao", "Trung bình", "Thấp"]},
            "Ngày bắt đầu (DD-MM-YYYY)": {"key": "start_date", "value": original_task_data.get('start_date', '')},
            "Hạn chót (DD-MM-YYYY)": {"key": "due_date", "value": original_task_data.get('due_date', '')}
        }
        self.entries_edit_task = {}
        for i, (field_text, info) in enumerate(fields_info_edit.items()):
            self.create_styled_label(form_frame, field_text, anchor="w").grid(row=i, column=0, sticky="nsew", pady=5, padx=5)
            if info.get("type") == "combobox":
                entry = ttk.Combobox(form_frame, font=("Arial", 12), values=info["values"], width=38, state="readonly")
                entry.set(info["value"])
            elif info.get("type") == "text_widget":
                entry = tk.Text(form_frame, font=("Arial", 12), width=40, height=5, wrap=tk.WORD)
                entry.insert("1.0", info["value"])
                desc_scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=entry.yview)
                entry.configure(yscrollcommand=desc_scrollbar.set)
                desc_scrollbar.grid(row=i, column=2, sticky="ns", pady=5, padx=(0,5))
            else:
                entry = ttk.Entry(form_frame, font=("Arial", 12), width=40)
                entry.insert(0, info["value"])
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries_edit_task[info["key"]] = entry
        if "title" in self.entries_edit_task: self.entries_edit_task["title"].focus()
        form_frame.grid_columnconfigure(1, weight=1)
        def save_task_changes_action():
            updated_data = {}
            for key_info_label, info_dict in fields_info_edit.items():
                widget_key = info_dict['key']
                widget = self.entries_edit_task[widget_key]
                if isinstance(widget, tk.Text):
                    updated_data[widget_key] = widget.get("1.0", tk.END).strip()
                else:
                    updated_data[widget_key] = widget.get().strip()
            if not updated_data["title"] or not updated_data["priority"] or \
               not updated_data["start_date"] or not updated_data["due_date"]:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường bắt buộc.", parent=self.root)
                return
            if not self.validate_dates(updated_data["start_date"], updated_data["due_date"]): return
            all_tasks_list = load_json(TASKS_FILE)
            if 0 <= task_index_in_all_tasks < len(all_tasks_list) and \
               all_tasks_list[task_index_in_all_tasks].get('task_id') == original_task_data.get('task_id') and \
               all_tasks_list[task_index_in_all_tasks].get('username') == target_username_of_task:
                for key_to_update, new_value in updated_data.items():
                    all_tasks_list[task_index_in_all_tasks][key_to_update] = new_value
                save_json(TASKS_FILE, all_tasks_list)
                messagebox.showinfo("Thành công", "Đã cập nhật công việc.", parent=self.root)
                self.view_tasks(target_username_of_task)
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật công việc. Công việc không tìm thấy, ID không khớp, hoặc không thuộc về người dùng này.", parent=self.root)
                self.view_tasks(target_username_of_task)
        edit_task_btn_frame = tk.Frame(edit_task_main_frame, bg="#F0F2F5")
        edit_task_btn_frame.pack(pady=(20,0))
        self.create_styled_button(edit_task_btn_frame, "Lưu thay đổi", save_task_changes_action, bg_color="#28a745", width=20).grid(row=0, column=0, padx=5)
        self.create_styled_button(edit_task_btn_frame, "Quay lại", lambda: self.view_tasks(target_username_of_task), bg_color="#6c757d", width=20).grid(row=0, column=1, padx=5)

    def delete_task(self, target_username_of_task):
        task_to_delete_data, task_index_in_all_tasks = self._get_task_from_selection(target_username_of_task)
        if task_to_delete_data is None:
            return
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa công việc '{task_to_delete_data['title']}' không?", parent=self.root):
            all_tasks_list = load_json(TASKS_FILE)
            if 0 <= task_index_in_all_tasks < len(all_tasks_list) and \
               all_tasks_list[task_index_in_all_tasks].get('task_id') == task_to_delete_data.get('task_id') and \
               all_tasks_list[task_index_in_all_tasks].get('username') == target_username_of_task:
                all_tasks_list.pop(task_index_in_all_tasks)
                save_json(TASKS_FILE, all_tasks_list)
                messagebox.showinfo("Thành công", "Đã xóa công việc.", parent=self.root)
            else:
                messagebox.showerror("Lỗi", "Không thể xóa công việc. Công việc không tìm thấy, ID không khớp, hoặc không thuộc về người dùng này.", parent=self.root)
            self.view_tasks(target_username_of_task)

    def view_users(self):
        self.clear_frame()
        view_users_main_frame = tk.Frame(self.root, bg="#F0F2F5")
        view_users_main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.create_styled_label(view_users_main_frame, "Quản lý Người dùng", font_size=16, bold=True, anchor="center").pack(pady=(0,15))
        users = load_json(USERS_FILE)
        self.users_display_list = [u for u in users if u['role'] == 'user']
        tree_frame_users = tk.Frame(view_users_main_frame)
        tree_frame_users.pack(fill="both", expand=True, pady=(0,10))
        self.user_tree = ttk.Treeview(tree_frame_users, columns=("Tài khoản", "Họ tên"), show="headings", height=15)
        user_scrollbar_y = ttk.Scrollbar(tree_frame_users, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scrollbar_y.set)
        user_scrollbar_y.pack(side="right", fill="y")
        self.user_tree.pack(side="left", fill="both", expand=True)
        self.user_tree.heading("Tài khoản", text="Tài khoản")
        self.user_tree.heading("Họ tên", text="Họ tên")
        self.user_tree.column("Tài khoản", width=200, minwidth=150, anchor="w")
        self.user_tree.column("Họ tên", width=300, minwidth=200, anchor="w")
        for i, user_data_item in enumerate(self.users_display_list):
            self.user_tree.insert("", tk.END, iid=str(i), values=(
                user_data_item.get('username', ''),
                user_data_item.get('fullname', '')
            ))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#e0e0e0", foreground="#333333")
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.map('Treeview', background=[('selected', '#a0a0a0')])
        admin_users_btn_frame = tk.Frame(view_users_main_frame, bg="#F0F2F5")
        admin_users_btn_frame.pack(fill="x", pady=5)
        self.create_styled_button(admin_users_btn_frame, "Xem công việc", self.open_user_tasks_for_admin, bg_color="#007bff", width=18).pack(side="left", padx=(10,5), pady=5)
        self.create_styled_button(admin_users_btn_frame, "Sửa TT User", self.edit_selected_user_by_admin, bg_color="#ffc107", fg_color="#333333", width=18).pack(side="left", padx=5, pady=5)
        self.create_styled_button(admin_users_btn_frame, "Xóa User", self.delete_selected_user_by_admin, bg_color="#dc3545", width=18).pack(side="left", padx=5, pady=5)
        self.create_styled_button(admin_users_btn_frame, "Quay lại", self.init_main, bg_color="#6c757d", width=18).pack(side="right", padx=(5,10), pady=5)

    def open_user_tasks_for_admin(self):
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một người dùng để xem công việc.", parent=self.root)
            return
        selected_iid = selected_items[0]
        try:
            index_in_display_list = int(selected_iid)
            user_to_view = self.users_display_list[index_in_display_list]
            self.view_tasks(user_to_view['username'])
        except (ValueError, IndexError):
             messagebox.showerror("Lỗi", "Lỗi khi chọn người dùng. Vui lòng thử lại.", parent=self.root)

    def edit_selected_user_by_admin(self):
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một người dùng để sửa thông tin.", parent=self.root)
            return
        selected_iid = selected_items[0]
        try:
            index_in_display_list = int(selected_iid)
            user_to_edit_data = self.users_display_list[index_in_display_list]
            self._edit_user_by_admin_form(user_to_edit_data)
        except (ValueError, IndexError):
             messagebox.showerror("Lỗi", "Lỗi khi chọn người dùng. Vui lòng thử lại.", parent=self.root)

    def _edit_user_by_admin_form(self, user_data_to_edit):
        self.clear_frame()
        target_username_val = user_data_to_edit['username']
        target_fullname_val = user_data_to_edit['fullname']
        edit_user_admin_main_frame = tk.Frame(self.root, bg="#F0F2F5")
        edit_user_admin_main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        edit_user_admin_form_frame = tk.Frame(edit_user_admin_main_frame, bg="#F0F2F5", bd=2, relief="groove")
        edit_user_admin_form_frame.pack(expand=True, anchor="center", padx=20, pady=20)
        self.create_styled_label(edit_user_admin_form_frame, f"Cập nhật cho: {target_fullname_val} ({target_username_val})", font_size=16, bold=True, anchor="center").pack(pady=15)
        self.create_styled_label(edit_user_admin_form_frame, "Họ tên mới (để trống nếu không đổi)", anchor="w").pack(pady=(10,0), fill="x", padx=10)
        new_fullname_admin_entry = ttk.Entry(edit_user_admin_form_frame, font=("Arial", 12), width=30)
        new_fullname_admin_entry.insert(0, target_fullname_val)
        new_fullname_admin_entry.pack(pady=5, padx=10)
        new_fullname_admin_entry.focus()
        self.create_styled_label(edit_user_admin_form_frame, "Mật khẩu mới (để trống nếu không đổi)", anchor="w").pack(pady=(10,0), fill="x", padx=10)
        new_password_admin_entry = ttk.Entry(edit_user_admin_form_frame, font=("Arial", 12), show="*", width=30)
        new_password_admin_entry.pack(pady=5, padx=10)
        def save_admin_user_edit_action():
            updated_fullname_val = new_fullname_admin_entry.get().strip()
            updated_password_val = new_password_admin_entry.get().strip()
            users_list = load_json(USERS_FILE)
            user_found_flag = False
            changes_made_flag = False
            for i, u_item in enumerate(users_list):
                if u_item['username'] == target_username_val:
                    user_found_flag = True
                    if updated_fullname_val and updated_fullname_val != u_item['fullname']:
                        users_list[i]['fullname'] = updated_fullname_val
                        changes_made_flag = True
                    if updated_password_val:
                        users_list[i]['password'] = hash_password(updated_password_val)
                        changes_made_flag = True
                    break
            if not user_found_flag:
                messagebox.showerror("Lỗi", f"Không tìm thấy người dùng {target_username_val}.", parent=self.root)
                self.view_users()
                return
            if not changes_made_flag:
                messagebox.showinfo("Thông báo", "Không có thông tin nào được thay đổi.", parent=self.root)
                self.view_users()
                return
            save_json(USERS_FILE, users_list)
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin cho {target_username_val}.", parent=self.root)
            self.view_users()
        admin_edit_btn_container = tk.Frame(edit_user_admin_form_frame, bg="#F0F2F5")
        admin_edit_btn_container.pack(pady=20)
        self.create_styled_button(admin_edit_btn_container, "Lưu thay đổi", save_admin_user_edit_action, bg_color="#28a745").grid(row=0, column=0, padx=10)
        self.create_styled_button(admin_edit_btn_container, "Quay lại", self.view_users, bg_color="#6c757d").grid(row=0, column=1, padx=10)

    def delete_selected_user_by_admin(self):
        selected_items = self.user_tree.selection()
        if not selected_items:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một người dùng để xóa.", parent=self.root)
            return
        selected_iid = selected_items[0]
        try:
            index_in_display_list = int(selected_iid)
            user_to_delete_data = self.users_display_list[index_in_display_list]
            if user_to_delete_data['username'] == ADMIN_DEFAULT['username']:
                 messagebox.showerror("Không thể xóa", "Không thể xóa tài khoản admin mặc định.", parent=self.root)
                 return
            if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa người dùng '{user_to_delete_data['username']}' không?\nTất cả công việc của người dùng này cũng sẽ bị xóa.", parent=self.root):
                self._perform_delete_user(user_to_delete_data['username'])
        except (ValueError, IndexError):
             messagebox.showerror("Lỗi", "Lỗi khi chọn người dùng. Vui lòng thử lại.", parent=self.root)

    def _perform_delete_user(self, username_to_delete_val):
        users_list = load_json(USERS_FILE)
        users_after_deletion_list = [u for u in users_list if u['username'] != username_to_delete_val]
        if len(users_list) == len(users_after_deletion_list):
            messagebox.showerror("Lỗi", f"Không tìm thấy người dùng {username_to_delete_val} để xóa.", parent=self.root)
        else:
            save_json(USERS_FILE, users_after_deletion_list)
            tasks_list = load_json(TASKS_FILE)
            tasks_after_deletion_list = [t for t in tasks_list if t.get('username') != username_to_delete_val]
            save_json(TASKS_FILE, tasks_after_deletion_list)
            messagebox.showinfo("Thành công", f"Đã xóa người dùng {username_to_delete_val} và các công việc liên quan.", parent=self.root)
        self.view_users()

    # --- SUGGESTED TASK (from Gist) FEATURE METHODS - WITH CONDITIONAL GET ---
    def _get_fallback_suggested_tasks(self):
        return [
            {"title": "Học bài (Mẫu mặc định)", "description": "Ôn tập kiến thức.", "status": "Chưa hoàn thành", "due_date": ""},
            {"title": "Tập thể dục (Mẫu mặc định)", "description": "Vận động cơ thể.", "status": "Chưa hoàn thành", "due_date": ""}
        ]

    def _fetch_suggested_tasks_from_gist(self, cached_etag=None, cached_last_modified=None):
        if not self.suggested_tasks_gist_url:
            print("Thông báo DEBUG: URL Gist rỗng, sử dụng fallback.")
            return 500, self._get_fallback_suggested_tasks()
        print(f"Thông báo DEBUG: Đang fetch từ URL: {self.suggested_tasks_gist_url}")
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        if cached_etag:
            headers['If-None-Match'] = cached_etag
        if cached_last_modified:
            headers['If-Modified-Since'] = cached_last_modified
        try:
            response = requests.get(self.suggested_tasks_gist_url, timeout=10, headers=headers)
            if response.status_code == 304:
                print("Thông báo DEBUG: Gist content not modified (304).")
                return 304, None
            response.raise_for_status()
            if not response.content:
                print("Thông báo DEBUG: Nội dung phản hồi từ Gist rỗng.")
                raise ValueError("Nội dung phản hồi từ Gist rỗng.")
            print(f"Thông báo DEBUG: Raw response text (first 500 chars): {response.text[:500]}")
            suggested_tasks_data = response.json()
            print(f"Thông báo DEBUG: Dữ liệu JSON đã parse (first 300 chars): {str(suggested_tasks_data)[:300]}...")
            if not isinstance(suggested_tasks_data, list):
                if isinstance(suggested_tasks_data, dict) and 'quotes' in suggested_tasks_data and isinstance(suggested_tasks_data['quotes'], list) :
                    suggested_tasks_data = suggested_tasks_data['quotes']
                elif isinstance(suggested_tasks_data, dict) and 'tasks' in suggested_tasks_data and isinstance(suggested_tasks_data['tasks'], list) :
                    suggested_tasks_data = suggested_tasks_data['tasks']
                elif isinstance(suggested_tasks_data, dict) and 'todos' in suggested_tasks_data and isinstance(suggested_tasks_data['todos'], list) : # For dummyjson/todos
                    suggested_tasks_data = suggested_tasks_data['todos']
                else:
                    raise ValueError("Dữ liệu từ Gist không phải là list hoặc object chứa key 'quotes'/'tasks'/'todos' với list.")
            new_etag = response.headers.get('ETag')
            new_last_modified = response.headers.get('Last-Modified')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cached_data = {
                "last_fetched_success_timestamp": timestamp,
                "etag": new_etag,
                "last_modified": new_last_modified,
                "suggested_tasks_data": suggested_tasks_data
            }
            save_json(SUGGESTED_TASKS_CACHE_FILE, cached_data)
            print(f"Thông báo DEBUG: Đã tải {len(suggested_tasks_data)} CV gợi ý và lưu vào cache.")
            return 200, suggested_tasks_data
        except requests.exceptions.Timeout:
            print("Lỗi DEBUG: Timeout khi fetch Gist.")
            messagebox.showerror("Lỗi Mạng (Gist)", "Yêu cầu lấy CV gợi ý bị timeout.", parent=self.root)
        except requests.exceptions.RequestException as e:
            print(f"Lỗi DEBUG: RequestException khi fetch Gist: {e}")
            messagebox.showerror("Lỗi API (Gist)", f"Không thể lấy CV gợi ý từ Gist: {e}", parent=self.root)
        except (json.JSONDecodeError, ValueError) as e_json:
            print(f"Lỗi DEBUG: JSONDecodeError hoặc ValueError khi parse Gist: {e_json}")
            messagebox.showerror("Lỗi Dữ Liệu (Gist)", f"Dữ liệu CV gợi ý từ Gist không đúng định dạng hoặc lỗi: {e_json}", parent=self.root)
        except Exception as e_general:
             print(f"Lỗi DEBUG: Lỗi không xác định khi fetch Gist: {e_general}")
             messagebox.showerror("Lỗi Không Xác Định (Gist)", f"Đã xảy ra lỗi khi lấy CV gợi ý: {e_general}", parent=self.root)
        print("Thông báo DEBUG: Có lỗi xảy ra trong fetch, sử dụng fallback.")
        return 500, self._get_fallback_suggested_tasks()

    def _load_or_fetch_suggested_tasks(self, force_fetch=False):
        cached_content = load_json(SUGGESTED_TASKS_CACHE_FILE)
        if not isinstance(cached_content, dict):
            cached_content = {"last_fetched_success_timestamp": "", "etag": "", "last_modified": "", "suggested_tasks_data": []}
        current_cached_data_list = cached_content.get("suggested_tasks_data", [])
        current_etag = cached_content.get("etag")
        current_last_modified = cached_content.get("last_modified")
        last_fetched_timestamp_str = cached_content.get("last_fetched_success_timestamp")
        perform_fetch_attempt = force_fetch
        if not force_fetch:
            if not last_fetched_timestamp_str or not current_cached_data_list:
                print("Thông báo DEBUG: Cache rỗng hoặc không có timestamp, sẽ thử fetch.")
                perform_fetch_attempt = True
            else:
                try:
                    last_fetched_dt = datetime.strptime(last_fetched_timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - last_fetched_dt).total_seconds() > 300: # Cache 5 phút
                        print("Thông báo DEBUG: Cache đã cũ (>5 phút), sẽ thử fetch.")
                        perform_fetch_attempt = True
                    else:
                        print("Thông báo DEBUG: Sử dụng dữ liệu CV gợi ý từ cache (còn hạn và không force_fetch).")
                        return current_cached_data_list if current_cached_data_list else self._get_fallback_suggested_tasks()
                except ValueError:
                    print("Thông báo DEBUG: Lỗi timestamp cache, sẽ thử fetch.")
                    perform_fetch_attempt = True
        if perform_fetch_attempt:
            print(f"Thông báo DEBUG: Thực hiện fetch (force_fetch={force_fetch}). ETag cache: {current_etag}, Last-Mod cache: {current_last_modified}")
            status_code, data_or_signal = self._fetch_suggested_tasks_from_gist(
                cached_etag=current_etag if current_etag else None,
                cached_last_modified=current_last_modified if current_last_modified else None
            )
            if status_code == 304:
                print("Thông báo DEBUG: Gist content not modified (304). Dùng dữ liệu cache hiện tại.")
                new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_cache_for_timestamp = {
                    "last_fetched_success_timestamp": new_timestamp,
                    "etag": current_etag,
                    "last_modified": current_last_modified,
                    "suggested_tasks_data": current_cached_data_list
                }
                save_json(SUGGESTED_TASKS_CACHE_FILE, updated_cache_for_timestamp)
                return current_cached_data_list if current_cached_data_list else self._get_fallback_suggested_tasks()
            return data_or_signal if data_or_signal else self._get_fallback_suggested_tasks()
        print("Thông báo DEBUG: Không fetch, sử dụng fallback (logic path bất thường).")
        return self._get_fallback_suggested_tasks()

    def _apply_suggested_task_to_form(self, suggested_task_data, chooser_window):
        chooser_window.destroy()
        title_widget = self.entries_add_task.get("title")
        description_widget = self.entries_add_task.get("description")
        task_title_from_gist = suggested_task_data.get("title",
                                 suggested_task_data.get("todo",
                                   suggested_task_data.get("quote", "Không có tiêu đề")))
        task_desc_from_gist = suggested_task_data.get("description",
                                suggested_task_data.get("author", "")) # Cho dummyjson quotes
        if title_widget:
            title_widget.delete(0, tk.END)
            title_widget.insert(0, task_title_from_gist)
        if description_widget and isinstance(description_widget, tk.Text):
            description_widget.delete("1.0", tk.END)
            description_widget.insert("1.0", task_desc_from_gist)
        messagebox.showinfo("Áp dụng CV Gợi Ý", f"Đã áp dụng: '{task_title_from_gist}'.\nHoàn tất các thông tin còn lại.", parent=self.root)

    def _show_suggested_task_chooser(self):
        suggested_tasks = self._load_or_fetch_suggested_tasks()
        if not suggested_tasks:
            messagebox.showinfo("Không có CV Gợi Ý", "Hiện không có công việc gợi ý nào để chọn.", parent=self.root)
            return
        chooser_window = tk.Toplevel(self.root)
        chooser_window.title("Chọn Công Việc Gợi Ý")
        chooser_window.geometry("500x350")
        chooser_window.configure(bg="#F0F2F5")
        chooser_window.transient(self.root)
        chooser_window.grab_set()
        tk.Label(chooser_window, text="Chọn một công việc gợi ý để thêm nhanh:",
                 font=("Arial", 12), bg="#F0F2F5").pack(pady=10)
        listbox_frame = tk.Frame(chooser_window)
        listbox_frame.pack(pady=5, padx=10, fill="both", expand=True)
        task_listbox = tk.Listbox(listbox_frame, font=("Arial", 11), height=10, exportselection=False)
        task_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=task_listbox.yview)
        task_listbox.configure(yscrollcommand=task_scrollbar.set)
        task_listbox.pack(side="left", fill="both", expand=True)
        task_scrollbar.pack(side="right", fill="y")
        self.task_map_for_chooser = {}
        for i, task_item in enumerate(suggested_tasks):
            display_name = task_item.get("title",
                             task_item.get("todo",
                               task_item.get("quote", f"CV không tên {i+1}")))
            task_listbox.insert(tk.END, display_name)
            self.task_map_for_chooser[display_name] = task_item
        if suggested_tasks:
             if task_listbox.size() > 0: task_listbox.selection_set(0)
             task_listbox.focus()
        btn_frame_chooser = tk.Frame(chooser_window, bg="#F0F2F5")
        btn_frame_chooser.pack(pady=10)
        def on_select_suggested_task():
            selected_indices = task_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn một công việc.", parent=chooser_window)
                return
            selected_display_name = task_listbox.get(selected_indices[0])
            selected_task_data = self.task_map_for_chooser.get(selected_display_name)
            if selected_task_data:
                self._apply_suggested_task_to_form(selected_task_data, chooser_window)
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu cho CV gợi ý đã chọn.", parent=chooser_window)
        select_button = self.create_styled_button(btn_frame_chooser, "Chọn",
                                     on_select_suggested_task,
                                     bg_color="#28a745", width=12)
        select_button.grid(row=0, column=0, padx=10)
        refresh_button = self.create_styled_button(btn_frame_chooser, "Tải lại DS",
                                     lambda: self._refresh_suggested_list_in_chooser(task_listbox, self.task_map_for_chooser),
                                     bg_color="#17a2b8", width=12)
        refresh_button.grid(row=0, column=1, padx=10)
        cancel_button = self.create_styled_button(btn_frame_chooser, "Hủy",
                                   chooser_window.destroy,
                                   bg_color="#6c757d", width=12)
        cancel_button.grid(row=0, column=2, padx=10)
        task_listbox.bind("<Double-1>", lambda event: on_select_suggested_task())

    def _refresh_suggested_list_in_chooser(self, listbox_widget, task_map_dict):
        new_suggested_tasks = self._load_or_fetch_suggested_tasks(force_fetch=True)
        listbox_widget.delete(0, tk.END)
        task_map_dict.clear()
        if new_suggested_tasks:
            for i, task_item in enumerate(new_suggested_tasks):
                display_name = task_item.get("title",
                                 task_item.get("todo",
                                   task_item.get("quote", f"CV không tên {i+1}")))
                listbox_widget.insert(tk.END, display_name)
                task_map_dict[display_name] = task_item
            if listbox_widget.size() > 0: listbox_widget.selection_set(0)
        else:
            messagebox.showinfo("Không có CV gợi ý", "Không tải được CV gợi ý nào hoặc danh sách rỗng.", parent=listbox_widget.winfo_toplevel())

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
