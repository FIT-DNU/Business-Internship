# Backlog và kế hoạch phát triển

## Product Backlog

| STT | Chức năng | Ưu tiên | Trạng thái |
|---|---|---|---|
| 1 | Cài đặt môi trường Odoo 15 | Cao | Hoàn thành |
| 2 | Tích hợp module Quản lý nhân sự | Cao | Hoàn thành |
| 3 | Tích hợp module Quản lý dự án | Cao | Hoàn thành |
| 4 | Tích hợp module Quản lý công việc | Cao | Hoàn thành |
| 5 | Xử lý xung đột module nhân sự cũ | Cao | Hoàn thành |
| 6 | Dùng HRM làm dữ liệu nhân viên gốc | Cao | Hoàn thành |
| 7 | Gắn nhân viên vào dự án | Cao | Hoàn thành |
| 8 | Gắn nhân viên vào công việc | Cao | Hoàn thành |
| 9 | Kiểm tra nhân viên công việc thuộc dự án | Trung bình | Hoàn thành |
| 10 | Thêm AI sinh công việc từ dự án | Cao | Hoàn thành |
| 11 | Thêm wizard preview trước khi tạo task | Cao | Hoàn thành |
| 12 | Viết README hướng dẫn chạy | Cao | Đang thực hiện |
| 13 | Viết business flow | Cao | Đang thực hiện |
| 14 | Viết báo cáo bài tập lớn | Cao | Đang thực hiện |

## Sprint 1 - Khởi tạo và audit

- Clone mã nguồn.
- Cài Odoo 15.
- Cài PostgreSQL bằng Docker.
- Chạy thử hệ thống.
- Audit module cũ.
- Xác định lỗi và xung đột.

## Sprint 2 - Tích hợp nghiệp vụ

- Tích hợp HRM.
- Tích hợp quản lý dự án.
- Tích hợp quản lý công việc.
- Chuẩn hóa dữ liệu nhân viên.
- Kiểm thử tạo dự án và phân công nhân viên.

## Sprint 3 - Tính năng AI

- Tạo module `quan_ly_ai`.
- Gọi Ollama/Qwen2.5 cục bộ.
- Sinh danh sách công việc từ mô tả dự án.
- Cho quản lý preview trước khi tạo task.
- Tạo task thật trong model `cong_viec`.

## Sprint 4 - Hoàn thiện nộp bài

- Viết README.
- Viết business flow.
- Viết báo cáo.
- Push source lên GitHub.
- Chuẩn bị demo.
