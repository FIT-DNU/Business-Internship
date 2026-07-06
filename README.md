# HN-QTDN-17-01-N9

## 1. Thông tin đề tài

**Học phần:** Hội nhập và Quản trị phần mềm doanh nghiệp  
**Nền tảng:** Odoo 15  
**Đề tài:** Quản lý dự án + Quản lý công việc tích hợp Quản lý nhân sự  
**Nhóm:** N9  

## 2. Mục tiêu hệ thống

Hệ thống hỗ trợ doanh nghiệp quản lý nhân sự, quản lý dự án và quản lý công việc trên cùng một nền tảng Odoo 15.

Mục tiêu chính:

- Quản lý hồ sơ nhân viên.
- Tạo và quản lý dự án.
- Phân công nhân viên từ HRM vào dự án.
- Chia dự án thành các công việc nhỏ.
- Phân công người phụ trách công việc.
- Theo dõi trạng thái, deadline và tiến độ.
- Tích hợp AI cục bộ để sinh danh sách công việc từ mô tả dự án.

## 3. Các module chính

| Module | Chức năng |
|---|---|
| `quan_ly_nhan_su` | Quản lý nhân viên, phòng ban, chức vụ |
| `quan_ly_du_an` | Quản lý dự án, nhân viên tham gia, người phụ trách |
| `quan_ly_cong_viec` | Quản lý công việc, deadline, trạng thái, tiến độ |
| `quan_ly_ai` | AI sinh danh sách công việc từ mô tả dự án |

## 4. Điểm tích hợp HRM

Module `quan_ly_nhan_su` là dữ liệu gốc về nhân viên.

Khi tạo dự án hoặc công việc, hệ thống sử dụng nhân viên từ HRM để:

- Chọn nhân viên tham gia dự án.
- Chọn người phụ trách dự án.
- Phân công người phụ trách công việc.
- Gắn nhân viên tham gia công việc.

## 5. Tính năng AI

Module `quan_ly_ai` tích hợp Ollama và model `qwen2.5:1.5b`.

Luồng AI:

1. Quản lý mở một dự án.
2. Bấm nút **AI Tạo Công Việc**.
3. Odoo lấy thông tin dự án: tên, mô tả, ngày bắt đầu, ngày kết thúc, người phụ trách, nhân viên tham gia.
4. Odoo gửi prompt sang Ollama.
5. AI trả danh sách công việc dạng JSON.
6. Hệ thống hiển thị danh sách công việc để quản lý duyệt.
7. Quản lý chọn/chỉnh sửa công việc.
8. Odoo tạo công việc thật trong module `quan_ly_cong_viec`.

## 6. Cấu trúc thư mục quan trọng

```text
addons/
├── quan_ly_nhan_su/
├── quan_ly_du_an/
├── quan_ly_cong_viec/
└── quan_ly_ai/

docs/
├── audit/
├── business-flow/
├── sprint/
└── report/
```

## 7. Clone project từ GitHub

Mở WSL Ubuntu và chạy:

```bash
cd ~
git clone -b btl-quan-ly-du-an-cong-viec https://github.com/ThinhNguyen25/HN-QTDN-17-01-N9.git odoo-fitdnu
cd ~/odoo-fitdnu
```

Nếu đã có thư mục cũ và muốn lấy lại sạch từ GitHub:

```bash
cd ~
mv odoo-fitdnu odoo-fitdnu-old
git clone -b btl-quan-ly-du-an-cong-viec https://github.com/ThinhNguyen25/HN-QTDN-17-01-N9.git odoo-fitdnu
cd ~/odoo-fitdnu
```

## 8. Yêu cầu môi trường

Cần có:

- Ubuntu/WSL
- Python 3.10
- PostgreSQL chạy bằng Docker
- Odoo 15
- Ollama nếu muốn dùng tính năng AI

Kiểm tra nhanh:

```bash
python3 --version
docker --version
git --version
```

## 9. Cài môi trường Python

Trong thư mục project:

```bash
cd ~/odoo-fitdnu
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install requests
```

Nếu bị lỗi thiếu `setuptools` hoặc `pkg_resources`, chạy:

```bash
pip install setuptools
```

## 10. Chạy PostgreSQL bằng Docker

Nếu project có `docker-compose.yml`, chạy:

```bash
cd ~/odoo-fitdnu
docker compose up -d
```

Nếu container PostgreSQL đã tồn tại rồi, lần sau chỉ cần bật lại:

```bash
docker start postgres_odoo-base
```

Kiểm tra database container:

```bash
docker ps
```

## 11. Cấu hình Odoo

File cấu hình cần có tên `odoo.conf`.

Ví dụ cấu hình:

```ini
[options]
addons_path = addons
db_host = localhost
db_port = 5431
db_user = odoo
db_password = odoo
xmlrpc_port = 8069
admin_passwd = admin
```

Lưu ý:

- `db_port` phải khớp với port PostgreSQL Docker.
- Nếu Docker map `5431:5432` thì dùng `db_port = 5431`.
- Nếu Docker map `5435:5432` thì dùng `db_port = 5435`.

## 12. Chạy Odoo

```bash
cd ~/odoo-fitdnu
source venv/bin/activate
python3 odoo-bin.py -c odoo.conf
```

Mở trình duyệt:

```text
http://localhost:8069
```

## 13. Tạo database mới

Truy cập:

```text
http://localhost:8069/web/database/manager
```

Tạo database, ví dụ:

```text
btl_k16_project_task
```

Master password:

```text
admin
```

Sau đó đăng nhập Odoo.

## 14. Cài các module của bài

Trong giao diện Odoo:

1. Bật Developer Mode.
2. Vào Apps.
3. Update Apps List.
4. Tìm và cài các module:

```text
Quản Lý Nhân Sự
Quản Lý Dự Án
Quản Lý Công Việc
Quản Lý AI
```

Hoặc cài bằng terminal:

```bash
cd ~/odoo-fitdnu
source venv/bin/activate

python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -i quan_ly_nhan_su
python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -i quan_ly_du_an
python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -i quan_ly_cong_viec
python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -i quan_ly_ai
```

Nếu đã cài rồi và chỉ muốn cập nhật code:

```bash
python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -u quan_ly_ai
```

## 15. Chạy AI bằng Ollama

Mở terminal WSL khác.

Kiểm tra Ollama:

```bash
ollama list
```

Nếu chưa có model:

```bash
ollama pull qwen2.5:1.5b
```

Bật Ollama:

```bash
ollama serve
```

Nếu báo Ollama đã chạy rồi thì bỏ qua.

## 16. Demo tính năng AI

1. Đăng nhập Odoo.
2. Vào module **Quản Lý Dự Án**.
3. Mở một dự án.
4. Đảm bảo dự án có:
   - tên dự án,
   - mô tả,
   - ngày bắt đầu,
   - nhân viên tham gia,
   - người phụ trách.
5. Bấm **AI Tạo Công Việc**.
6. Bấm **Sinh gợi ý AI**.
7. Chỉnh sửa hoặc bỏ chọn công việc không cần thiết.
8. Bấm **Tạo công việc**.
9. Kiểm tra các công việc mới trong module **Quản Lý Công Việc**.

## 17. Cách chạy lại sau khi đã tắt terminal

Mở WSL Ubuntu.

### Terminal 1: bật database

```bash
docker start postgres_odoo-base
```

Nếu chưa có container:

```bash
cd ~/odoo-fitdnu
docker compose up -d
```

### Terminal 2: chạy Odoo

```bash
cd ~/odoo-fitdnu
source venv/bin/activate
python3 odoo-bin.py -c odoo.conf
```

Mở:

```text
http://localhost:8069
```

### Terminal 3: chạy AI nếu cần dùng nút AI

```bash
ollama serve
```

## 18. Một số lỗi thường gặp

### Lỗi không kết nối được database

Kiểm tra Docker:

```bash
docker ps -a
docker start postgres_odoo-base
docker ps
```

### Lỗi không thấy module mới

Cập nhật module:

```bash
cd ~/odoo-fitdnu
source venv/bin/activate
python3 odoo-bin.py -c odoo.conf -d btl_k16_project_task --stop-after-init -u quan_ly_ai
```

### Lỗi AI không phản hồi

Kiểm tra Ollama:

```bash
ollama list
ollama serve
```

### Lỗi cổng 8069 đang bị chiếm

```bash
lsof -i :8069
kill -9 <PID>
```

## 19. Tài liệu nghiệp vụ

- Audit mã nguồn: `docs/audit/audit.md`
- Business Flow: `docs/business-flow/`
- Sprint/Backlog: `docs/sprint/backlog.md`
- Hướng dẫn báo cáo: `docs/report/huong_dan_bao_cao.md`

## 20. Link repository

```text
https://github.com/ThinhNguyen25/HN-QTDN-17-01-N9
```
