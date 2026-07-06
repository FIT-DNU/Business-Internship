# Audit mã nguồn ban đầu

## 1. Mục tiêu

Dự án được phát triển dựa trên các module Odoo có sẵn, sau đó tái cấu trúc và mở rộng để đáp ứng yêu cầu bài tập lớn.

Module chính:

- `quan_ly_nhan_su`: Quản lý nhân sự.
- `quan_ly_du_an`: Quản lý dự án.
- `quan_ly_cong_viec`: Quản lý công việc.
- `quan_ly_ai`: AI hỗ trợ sinh công việc từ mô tả dự án.

## 2. Vấn đề phát hiện

- Có module nhân sự cũ `nhan_su` gây xung đột với module `quan_ly_nhan_su`.
- Có trùng model `nhan_vien`.
- Một số file Python bị lỗi tab/space.
- Quy trình HRM - Dự án - Công việc chưa được mô tả rõ.
- Chưa có tính năng AI/API nâng cao.

## 3. Hướng xử lý

- Vô hiệu hóa module nhân sự cũ.
- Dùng `quan_ly_nhan_su` làm dữ liệu gốc.
- Tích hợp nhân viên HRM vào dự án và công việc.
- Sửa lỗi indentation trong module công việc.
- Bổ sung module `quan_ly_ai` dùng Ollama/Qwen2.5 để sinh công việc.

## 4. Kết quả

- Hệ thống chạy trên Odoo 15.
- Dữ liệu nhân sự được dùng làm dữ liệu gốc.
- Dự án có nhân viên tham gia.
- Công việc được phân công cho nhân viên.
- AI có thể sinh danh sách công việc từ mô tả dự án.
- Quản lý có thể duyệt task AI trước khi tạo task thật.
