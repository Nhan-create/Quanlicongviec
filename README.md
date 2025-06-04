# Ứng Dụng Quản Lý Công Việc 

Một ứng dụng desktop đơn giản giúp bạn quản lý danh sách công việc cá nhân trong công ty, được phát triển bằng Python và thư viện Tkinter. Dữ liệu được lưu trữ cục bộ sử dụng các file JSON.

## Tính Năng Chính

* **Quản lý Người Dùng:**
    * Đăng ký tài khoản mới.
    * Đăng nhập an toàn với mật khẩu được băm.
    * Phân quyền người dùng: Admin và User thường.
      + Admin có tài khoản mặc định là admin và mật khẩu là admin123 và có thể câp nhật thông tin của admin và của user
    * Người dùng tự cập nhật thông tin cá nhân và mật khẩu.
    * Người dùng tự xóa tài khoản (Admin mặc định không thể tự xóa).
* **Quản lý Công Việc (CRUD):**
    * Thêm công việc mới với các thông tin: tiêu đề, mô tả, mức độ ưu tiên, ngày bắt đầu, ngày hết hạn.
    * Xem danh sách công việc.
    * Chỉnh sửa thông tin công việc đã có.
    * Xóa công việc.
* **Chức năng Admin:**
    * Xem danh sách tất cả người dùng (user thường).
    * Sửa thông tin (họ tên, reset mật khẩu) cho người dùng thường.
    * Xóa tài khoản người dùng thường (bao gồm cả các công việc liên quan của họ).
    * Xem và quản lý công việc của bất kỳ người dùng nào.
* **Lấy Dữ Liệu Gợi Ý Từ Bên Ngoài:**
    * Tính năng "Chọn CV Gợi Ý..." trong form thêm công việc mới, lấy danh sách công việc từ một file JSON được lưu trữ trên GitHub Gist.
    * Có cơ chế cache và Conditional GET (ETag/Last-Modified) để tối ưu việc tải lại dữ liệu từ Gist.
* **Lưu Trữ Dữ Liệu:**
    * Sử dụng file JSON (`users.json`, `tasks.json`) để lưu trữ thông tin người dùng và công việc.
    * File cache `suggested_tasks_cache.json` cho dữ liệu Gist.

## Hướng Dẫn Sử Dụng

### 1. Sử dụng Phiên Bản Đã Đóng Gói (Dành cho người dùng cuối)

Đây là cách đơn giản nhất để trải nghiệm ứng dụng:

1.  **Tải ứng dụng:**
    * Truy cập mục **[Releases](https://github.com/Nhan-create/Quanlicongviec/releases)** của kho chứa này.
    * Tải về file `.zip` (hoặc `.rar`) của phiên bản mới nhất (ví dụ: `QuanLyCongViec_v1.0.0.zip`).
2.  **Giải nén:**
    * Giải nén file vừa tải về ra một thư mục trên máy tính của bạn.
3.  **Chạy ứng dụng:**
    * Mở thư mục đã giải nén, tìm và chạy file `QuanLyCongViec.exe` (hoặc tên file thực thi tương ứng).
    * Lần đầu chạy, các file dữ liệu (`users.json`, `tasks.json`, `suggested_tasks_cache.json`) sẽ được tự động tạo ra trong cùng thư mục nếu chúng chưa tồn tại. Tài khoản admin mặc định (`admin`/`admin123`) sẽ được tạo.

### 2. Chạy Từ Mã Nguồn (Dành cho nhà phát triển/người muốn xem code)

**Yêu cầu:**
* Python 3.x (ví dụ: Python 3.9 trở lên)
* Pip (thường đi kèm với Python)
* Git (để clone repository)

**Các bước thực hiện:**

1.  **Clone repository về máy:**
    ```bash
    git clone [https://github.com/Nhan-create/Quanlicongviec.git](https://github.com/Nhan-create/Quanlicongviec.git)
    ```
2.  **Di chuyển vào thư mục dự án:**
    ```bash
    cd Quanlicongviec
    ```
3.  **(Khuyến khích) Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    # Trên Windows:
    venv\Scripts\activate
    # Trên macOS/Linux:
    # source venv/bin/activate
    ```
4.  **Cài đặt các thư viện cần thiết:**
    Ứng dụng này sử dụng thư viện `requests`.
    ```bash
    pip install requests
    ```
5.  **(QUAN TRỌNG) Cấu hình URL Gist cho Công Việc Gợi Ý:**
    * Mở file mã nguồn chính (ví dụ: `Quanlicongviec.py` hoặc tên file tương tự).
    * Tìm đến dòng `self.suggested_tasks_gist_url = "..."` trong hàm `__init__` của lớp `TaskApp`.
    * Thay thế URL hiện tại bằng **URL Raw Gist của riêng bạn**. File JSON trên Gist này cần chứa danh sách các công việc gợi ý theo cấu trúc:
        ```json
        [
          {"title": "CV Gợi Ý 1", "description": "Mô tả cho CV1"},
          {"title": "CV Gợi Ý 2", "description": "Mô tả cho CV2"}
        ]
        ```
    * Nếu bạn không cung cấp URL hoặc URL không hợp lệ, ứng dụng sẽ sử dụng một danh sách công việc gợi ý mặc định.

6.  **Chạy ứng dụng:**
    ```bash
    python Quanlicongviec.py 
    ```
    (Thay `Quanlicongviec.py` bằng tên file Python chính của bạn nếu khác).
