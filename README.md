---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)




# Hệ thống Quản lý Nhân sự & Dự án Thông minh (Odoo 15)

## 📌 Giới thiệu dự án
Dự án này là một giải pháp quản trị doanh nghiệp tập trung, kết hợp giữa quản lý nguồn lực con người và điều hành dự án. Hệ thống được xây dựng trên nền tảng Odoo 15, tập trung vào tính tự động hóa và ràng buộc nghiệp vụ thông minh để tối ưu hóa hiệu suất làm việc.

## ✨ Tính năng nổi bật

### 1. Quản lý Nhân sự chuyên sâu (`nhan_su`)
* **Hồ sơ năng lực chi tiết**: Quản lý thông tin nhân viên bao gồm Mã nhân viên, Chức vụ, Ngày vào làm và Trình độ học vấn.
* **Hệ thống Bằng cấp**: Phân loại trình độ từ Trung cấp đến Tiến sĩ, hỗ trợ lọc và sắp xếp nhân sự theo năng lực.
* **Tích hợp thực thể**: Sử dụng `ten_nhan_vien` làm định danh hiển thị giúp việc liên kết dữ liệu giữa các module trở nên thân thiện và trực quan.

### 2. Quản lý Dự án & Công việc (`quan_ly_du_an`)
* **Tính toán Tiến độ Tự động**: Tiến độ tổng thể của dự án (`tien_do_tong_the`) được hệ thống tự động cập nhật dựa trên giá trị trung bình từ các công việc con thành viên.
* **Logic Ưu tiên Thông minh (Priority Matrix)**:
    * Dự án tự động được đánh giá mức độ **"Rất khẩn cấp"** (3 sao) nếu thời hạn còn lại ít hơn hoặc bằng 3 ngày, ưu tiên xử lý thời gian hơn quy mô vốn.
    * Hệ thống tự động phân loại mức độ ưu tiên dựa trên quy mô Ngân sách và Thời gian còn lại.
* **Ràng buộc Nghiệp vụ Chặt chẽ (`constrains`)**:
    * **Kiểm soát Ngân sách**: Chỉ những nhân sự có chức danh "Trưởng phòng" mới được phép quản trị các dự án lớn (ngân sách trên 500 triệu VNĐ).
    * **Phân cấp Quản lý**: Đảm bảo dự án phải được quản lý bởi cấp bậc tối thiểu là Trưởng nhóm hoặc Trưởng phòng.

### 3. Dashboard & Cảnh báo Trực quan
* **Nhãn dán Trạng thái (Ribbons)**: Hiển thị thông báo "KHẨN CẤP" hoặc "DỰ ÁN LỚN" trực tiếp trên giao diện để người dùng nắm bắt thông tin quan trọng tức thì.
* **Cảnh báo Màu sắc (Decorations)**:
    * Hệ thống tự động bôi đỏ các công việc đã quá hạn (`is_overdue`) để cảnh báo người thực hiện.
    * Sử dụng thanh tiến độ (Progress Bar) và huy hiệu (Badges) để theo dõi trạng thái công việc một cách chuyên nghiệp.
* **Báo cáo Phân tích**: Tích hợp các góc nhìn **Graph (Biểu đồ cột)** và **Pivot (Bảng phân tích)** giúp nhà quản lý so sánh nguồn lực và ngân sách giữa các dự án.

## 📂 Cấu trúc thư mục
```text
 Business-Internship/
 ├── nhan_su/                # Module Quản lý nhân sự
 │   ├── models/             # Định nghĩa cấu trúc nhân viên, bằng cấp
 │   ├── views/              # Giao diện quản lý & Menu QLNS
 │   └── data/               # Dữ liệu mẫu nhân sự (Trưởng phòng, Lead, Dev)
 └── quan_ly_du_an/          # Module Quản lý dự án & Công việc
     ├── models/             # Logic tính ưu tiên & ràng buộc chức vụ
     ├── views/              # Dashboard, Kanban, Biểu đồ ngân sách
     └── data/               # Kịch bản dự án mẫu (Core Banking, ERP)
```
# 4. Chạy hệ thống và cài đặt các ứng dụng cần thiết

Người sử dụng truy cập theo đường dẫn _http://localhost:8069/_ để đăng nhập vào hệ thống.
   
