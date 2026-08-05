# HỆ THỐNG QUẢN LÝ NHÂN SỰ, VĂN BẢN, KHÁCH HÀNG

## 1. Giới thiệu hệ thống
Hệ thống giúp doanh nghiệp quản lý toàn diện nhân sự, văn bản và khách hàng trên một nền tảng duy nhất. Mục tiêu là tự động hóa quy trình, giảm thao tác thủ công, tăng hiệu quả và minh bạch dữ liệu.

## 2. Tổng quan hệ thống
- Các module chính: Quản lý Nhân sự, Quản lý Văn bản, Quản lý Khách hàng, Chấm công & Tính lương, Chatbot hỗ trợ.
- Dữ liệu tập trung, liên thông giữa các module, dễ dàng mở rộng và tích hợp.
- Đối tượng sử dụng: Ban lãnh đạo, phòng nhân sự, kế toán, nhân viên, bộ phận kinh doanh, quản lý văn bản.

## 3. Chức năng các module

### 3.1. Quản lý Nhân sự (HR)
- Lưu trữ hồ sơ nhân viên, hợp đồng, phòng ban, chức vụ.
- Quản lý quá trình công tác, thay đổi lương, nghỉ phép, chế độ.

### 3.2. Quản lý Văn bản
- Lưu trữ, phân loại, tìm kiếm văn bản nội bộ, công văn.
- Quản lý quy trình phê duyệt, ban hành, phân quyền truy cập.

### 3.3. Quản lý Khách hàng (CRM)
- Quản lý thông tin khách hàng, lịch sử giao dịch, hợp đồng.
- Theo dõi cơ hội bán hàng, chăm sóc khách hàng, báo cáo doanh số.

### 3.4. Chấm công & Tính lương
- Quản lý ca làm việc, ghi nhận chấm công, xử lý dữ liệu công.
- Tính lương tự động, lập bảng lương, tra cứu phiếu lương cá nhân.

### 3.5. Chatbot hỗ trợ
- Trả lời câu hỏi về nhân sự, lương, quy định công ty.
- Tra cứu thông tin cá nhân, hỗ trợ thao tác tự phục vụ, nhắc nhở công việc.
<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
    🎓 Faculty of Information Technology (DaiNam University)
    </a>
</h2>
<h2 align="center">
    Hệ Thống Quản Lý Nhân Sự, Khách Hàng & Văn Bản<br/>
    <small>HRM, CRM & Document Management System</small>
</h2>
<div align="center">
    <p align="center">
        <img src="images/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="images/fitdnu_logo.png" alt="FITDNU Logo" width="180"/>
        <img src="images/dnu_logo.png" alt="DaiNam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-orange?style=for-the-badge)](https://dainam.edu.vn)

</div>
 

## 📖 1. Giới thiệu

Hệ thống **Quản lý Nhân Sự, Khách Hàng & Văn Bản** được xây dựng trên nền tảng **Odoo 17**, giúp doanh nghiệp số hóa toàn diện quy trình quản trị nhân sự, chăm sóc khách hàng và lưu trữ, xử lý văn bản nội bộ.

### Thông tin kỹ thuật (theo code thực tế)

#### 1. Quản lý Nhân Sự (HRM)
- **Chấm công, hiện diện:**
    - Model: `HrAttendance` ([addons/hr_attendance/models/hr_attendance.py](addons/hr_attendance/models/hr_attendance.py))
    - Model: `Employee` ([addons/hr_presence/models/hr_employee.py](addons/hr_presence/models/hr_employee.py))
    - Các hàm: `check_in`, `check_out`, `_compute_presence_state`, `action_set_present`, `action_set_absent`, `action_open_leave_request`, ...
- **Phòng ban, hợp đồng, nhân viên:**
    - Trường liên kết employee, department, contract trong các model trên
- **Tính lương, nghỉ phép:**
    - Dữ liệu chấm công và hiện diện phục vụ tính lương, nghỉ phép

#### 2. Quản lý Khách Hàng (CRM)
- **Thông tin khách hàng, giao dịch:**
    - Model: `Partner` ([addons/crm/models/res_partner.py](addons/crm/models/res_partner.py))
    - Model: `crm.lead` ([addons/crm/models/crm_lead.py](addons/crm/models/crm_lead.py))
    - Các hàm: `default_get`, `action_view_opportunity`, `_compute_opportunity_count`, ...
- **Báo cáo, chăm sóc khách hàng:**
    - Quản lý lead, opportunity, báo cáo, phân công, chăm sóc khách hàng

#### 3. Quản lý Văn Bản (Document)
- **Lưu trữ, tìm kiếm, phân loại:**
    - Model: `IrAttachment` ([addons/attachment_indexation/models/ir_attachment.py](addons/attachment_indexation/models/ir_attachment.py))
    - Các hàm: `_index_docx`, `_index_pptx`, `_index_xlsx`, `_index_opendoc`, `_index_pdf`, `_index`
    - Hỗ trợ tìm kiếm nội dung file docx, xlsx, pptx, pdf, opendoc

> **Lưu ý:** README này đã được đối chiếu với code thực tế (cập nhật ngày 2026-01-29). Các tính năng, model, và hàm nêu trên đều có trong source code.

<div align="center">

📸 **Giao diện hệ thống**

<p>
    <img src="images/nhansu.jpg" alt="Màn hình Quản lý nhân sự" width="30%"/>
    <img src="images/crm.jpg" alt="Màn hình Quản lý khách hàng" width="30%"/>
    <img src="images/vanban.jpg" alt="Màn hình Quản lý văn bản" width="30%"/>
</p>

</div>

<br/>

### 🎯 Lợi ích chính:
- ✅ Số hóa toàn bộ quy trình nhân sự, khách hàng, văn bản
- ✅ Loại bỏ giấy tờ, Excel rời rạc, tăng hiệu quả quản trị
- ✅ Quản lý tập trung, phân quyền rõ ràng
- ✅ Báo cáo trực quan, tìm kiếm nhanh
- ✅ Dễ dàng mở rộng, tích hợp các module khác

### 📌 3 Module Cốt Lõi:
1. **Quản lý Nhân Sự (HRM)** - Hồ sơ, hợp đồng, phòng ban, chấm công, lương, nghỉ phép
2. **Quản lý Khách Hàng (CRM)** - Thông tin khách hàng, lịch sử giao dịch, chăm sóc khách hàng
3. **Quản lý Văn Bản (Document)** - Lưu trữ, phân loại, tìm kiếm, phê duyệt, chia sẻ văn bản

## 🎨 2. Các Tính Năng Chi Tiết

### 1️⃣ Quản lý Nhân Sự (HRM Module) 👥
**Quản lý toàn bộ thông tin nhân viên, phòng ban, hợp đồng, chấm công, lương, nghỉ phép**

<div align="center">
    <img src="images/nhansu.jpg" alt="Giao diện danh sách nhân sự" width="90%"/>
</div>

| Tính năng | Mô tả |
|-----------|-------|
| 📋 Hồ sơ nhân viên | Thông tin cá nhân, liên lạc, giấy tờ |
| 🏢 Quản lý phòng ban | Tạo, chỉnh sửa phòng ban, cấu trúc tổ chức |
| 📜 Hợp đồng lao động | Tạo, theo dõi, quản lý hợp đồng |
| ⏱️ Chấm công | Check-in/out, báo cáo giờ làm, nghỉ phép |
| 💰 Tính lương | Tự động tính lương từ dữ liệu chấm công |
| 📅 Lịch làm việc | Quản lý ca, lịch làm việc, nghỉ lễ |
| 🔒 Phân quyền | Phân quyền theo phòng ban, vai trò |

### 2️⃣ Quản lý Khách Hàng (CRM Module) 🤝
**Quản lý thông tin khách hàng, lịch sử giao dịch, chăm sóc khách hàng**

<div align="center">
    <img src="images/crm.jpg" alt="Giao diện CRM" width="90%"/>
</div>

| Tính năng | Mô tả |
|-----------|-------|
| 👤 Thông tin khách hàng | Lưu trữ, cập nhật thông tin khách hàng |
| 📞 Lịch sử liên hệ | Ghi nhận lịch sử gọi điện, email, gặp mặt |
| 📝 Quản lý giao dịch | Theo dõi báo giá, hợp đồng, đơn hàng |
| 📊 Báo cáo khách hàng | Thống kê, phân loại khách hàng |
| 💬 Chăm sóc khách hàng | Quản lý lịch sử CSKH, nhắc nhở tự động |
| 🔍 Tìm kiếm nhanh | Tìm kiếm khách hàng theo nhiều tiêu chí |

### 3️⃣ Quản lý Văn Bản (Document Module) 📄
**Lưu trữ, phân loại, tìm kiếm, phê duyệt, chia sẻ văn bản nội bộ**

<div align="center">
    <img src="images/vanban.jpg" alt="Giao diện quản lý văn bản" width="90%"/>
</div>

| Tính năng | Mô tả |
|-----------|-------|
| 📂 Lưu trữ văn bản | Lưu trữ file, scan, tài liệu điện tử |
| 🗂️ Phân loại | Phân loại theo loại văn bản, phòng ban |
| 🔍 Tìm kiếm | Tìm kiếm nhanh theo tên, nội dung, tag |
| ✅ Phê duyệt | Quy trình phê duyệt, ký số, lưu vết |
| 🔗 Chia sẻ nội bộ | Chia sẻ văn bản cho phòng ban, cá nhân |
| 🕒 Lịch sử thay đổi | Theo dõi chỉnh sửa, truy cập |

## 🛠️ 3. Công Nghệ & Công Cụ

<div align="center">

### Backend & Database
[![Python](https://img.shields.io/badge/Python%203.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Odoo](https://img.shields.io/badge/Odoo%2017-6C3696?style=for-the-badge&logo=odoo&logoColor=white)](https://www.odoo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

### Frontend
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)

### DevOps & Deployment
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

### Operating Systems
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

</div>

## ⚙️ 4. Cài Đặt & Chạy Hệ Thống

### 📋 4.1 Yêu Cầu Hệ Thống
- **Python 3.10+**
- **PostgreSQL 12+**
- **Docker & Docker Compose** (khuyến nghị)
- **Git**
- **RAM: 4GB+**, **Disk: 10GB+**

### 🐳 4.2 Cài Đặt Nhanh với Docker (Khuyến nghị)

```bash
# 1. Clone project
git clone https://github.com/your-repo/odoo-fitdnu.git
cd odoo-fitdnu

# 2. Khởi động
docker-compose up -d

# 3. Truy cập tại http://localhost:8070
# Username: admin
# Password: admin
```

### 🖥️ 4.3 Cài Đặt Trên Linux (Ubuntu/Debian)

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt dependencies
sudo apt install -y python3 python3-pip python3-dev postgresql postgresql-contrib \
    git libxml2-dev libxslt1-dev libzip-dev libsasl2-dev libssl-dev libffi-dev

# 3. Clone project
cd /opt
sudo git clone https://github.com/your-repo/odoo-fitdnu.git
cd odoo-fitdnu

# 4. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Cấu hình Database PostgreSQL
sudo -u postgres createdb odoo_db
sudo -u postgres createuser -P odoo_user

# 7. Cấu hình Odoo
cp odoo.conf.template odoo.conf
# Sửa file odoo.conf: db_name, db_user, db_password

# 8. Chạy Odoo
./odoo-bin -c odoo.conf
# Hoặc: python3 odoo-bin.py -c odoo.conf

# 9. Truy cập: http://localhost:8070
```

### 🪟 4.4 Cài Đặt Trên Windows

```bash
# 1. Tải Python 3.10+ từ https://www.python.org/downloads/
# 2. Tải PostgreSQL từ https://www.postgresql.org/download/windows/

# 3. Clone project
git clone https://github.com/your-repo/odoo-fitdnu.git
cd odoo-fitdnu

# 4. Virtual environment
python -m venv venv
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Chạy Odoo
python odoo-bin.py -c odoo.conf

# 7. Truy cập: http://localhost:8070
```

## 📚 5. Hướng Dẫn Sử Dụng

### 5.1 Module Quản Lý Nhân Sự (HRM)
```
Menu: Nhân sự → Danh sách nhân viên
Chức năng:
- Quản lý thông tin nhân viên
- Quản lý phòng ban, hợp đồng
- Chấm công, tính lương, nghỉ phép
- Phân quyền theo phòng ban
```

### 5.2 Module Quản Lý Khách Hàng (CRM)
```
Menu: Khách hàng → Danh sách khách hàng
Chức năng:
- Lưu trữ, cập nhật thông tin khách hàng
- Quản lý lịch sử giao dịch, liên hệ
- Báo giá, hợp đồng, chăm sóc khách hàng
- Tìm kiếm, phân loại khách hàng
```

### 5.3 Module Quản Lý Văn Bản (Document)
```
Menu: Văn bản → Danh sách văn bản
Chức năng:
- Lưu trữ, phân loại, tìm kiếm văn bản
- Quy trình phê duyệt, ký số
- Chia sẻ nội bộ, phân quyền truy cập
- Theo dõi lịch sử chỉnh sửa
```

## 🎨 6. Các Tính Năng Nổi Bật

### ⚡ Số Hóa & Tự Động Hóa
```
- Quản lý tập trung toàn bộ dữ liệu nhân sự, khách hàng, văn bản
- Tự động hóa quy trình phê duyệt, nhắc nhở, báo cáo
- Tìm kiếm, truy xuất dữ liệu nhanh chóng
```

### 📊 Báo Cáo & Thống Kê
```
- Dashboard tổng quan nhân sự, khách hàng, văn bản
- Báo cáo theo phòng ban, thời gian, loại văn bản
- Xuất Excel, PDF chuyên nghiệp
```

### 🔒 Bảo Mật & Phân Quyền
```
- Phân quyền chi tiết theo vai trò, phòng ban
- Lưu vết truy cập, chỉnh sửa
- Mã hóa dữ liệu nhạy cảm
```

## 💡 7. Use Cases & Ví Dụ

### 📌 Quản Lý Nhân Sự
```
- Tuyển dụng, lưu trữ hồ sơ, hợp đồng
- Chấm công, tính lương, nghỉ phép
- Báo cáo nhân sự theo phòng ban
```

### 📌 Quản Lý Khách Hàng
```
- Lưu trữ thông tin, lịch sử giao dịch
- Chăm sóc khách hàng, nhắc nhở tự động
- Báo cáo khách hàng tiềm năng
```

### 📌 Quản Lý Văn Bản
```
- Lưu trữ, tìm kiếm, phân loại văn bản nội bộ
- Quy trình phê duyệt, ký số, chia sẻ nội bộ
- Theo dõi lịch sử chỉnh sửa, truy cập
```

## 📞 8. Support & Liên Hệ

- 📧 Email: [phannk2904@gmail.com]
- 🌐 Website: [https://dainam.edu.vn]
- 💬 Issues: GitHub Issues

## 📄 9. License & Attribution

- **License**: [MIT/GPL/Commercial]
- **Developed by**: VietLoi-PhuongAnh-MaiLan, Faculty of Information Technology, DaiNam University
- **Built with**: [Odoo](https://odoo.com)
- **Reference source**: [TTDN-15-03-N5](https://github.com/ThienDao103/TTDN-15-03-N5) - Quản Lý Khách Hàng

## 🙏 10. Đóng Góp

Chúng tôi chào đón các đóng góp từ cộng đồng!

```bash
# 1. Fork project
# 2. Tạo branch feature: git checkout -b feature/YourFeature
# 3. Commit: git commit -m 'Add YourFeature'
# 4. Push: git push origin feature/YourFeature
# 5. Tạo Pull Request
```

Xem thêm: [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

⭐ Nếu bạn thích project này, hãy star nó! ⭐

Made with ❤️ by VietLoi, PhuongAnh, MaiLan

</div>
