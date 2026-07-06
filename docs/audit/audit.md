# AUDIT CODE - K16

## Đề tài

Quản lý dự án và quản lý công việc.

---

# Module hiện có

## 1. Quản lý nhân sự

### Chức năng

- Quản lý nhân viên
- Chức vụ
- Phòng ban
- Nhóm dự án
- Lịch sử làm việc

### Đánh giá

✔ CRUD đầy đủ

Thiếu

- Avatar
- Import Excel
- Dashboard

---

## 2. Quản lý dự án

### Chức năng

- CRUD dự án
- Người phụ trách
- Thành viên
- Giai đoạn
- Ngân sách
- Chi phí
- Tài nguyên

### Đánh giá

✔ Hoạt động tốt

Thiếu

- Progress tự tính
- Deadline Warning
- KPI

---

## 3. Quản lý công việc

### Chức năng

- CRUD công việc
- Nhật ký
- Đánh giá nhân viên

### Đánh giá

✔ Hoạt động

Thiếu

- Phân công thông minh
- Workflow
- Notification

---

# Kiến trúc

HRM

↓

Project

↓

Task

↓

Evaluation

---

# Điểm mạnh

- Module tách rõ
- Dữ liệu liên kết
- Có nhiều relation

---

# Điểm yếu

- Thiếu Automation
- Thiếu Dashboard
- Thiếu AI
- Thiếu External API
- Progress nhập tay
- Chưa có Notification
# GAP ANALYSIS

| Chức năng | K16 | K17 |
|------------|------|------|
| CRUD HRM | ✔ | ✔ |
| CRUD Project | ✔ | ✔ |
| CRUD Task | ✔ | ✔ |
| Progress tự động | ✘ | ✔ |
| Status tự động | ✘ | ✔ |
| Deadline Notification | ✘ | ✔ |
| Telegram | ✘ | ✔ |
| AI Planning | ✘ | ✔ |
| Dashboard | ✘ | ✔ |
