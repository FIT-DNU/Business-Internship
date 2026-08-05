# HƯỚNG DẪN TÍNH TIẾN ĐỘ DỰ ÁN VÀ CÔNG VIỆC

## MỤC LỤC
1. [Tổng quan](#tổng-quan)
2. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
3. [Luồng tính toán tiến độ](#luồng-tính-toán-tiến-độ)
4. [Chi tiết code](#chi-tiết-code)
5. [Ví dụ minh họa](#ví-dụ-minh-họa)

---

## TỔNG QUAN

Hệ thống quản lý dự án sử dụng mô hình tính tiến độ từ dưới lên (bottom-up):

```
Nhật Ký Công Việc (muc_do) 
    ↓ Tính trung bình
Công Việc (phan_tram_cong_viec)
    ↓ Tính trung bình
Dự Án (tien_do) → Trạng thái (trang_thai, tien_do_du_an)
```

### Nguyên tắc hoạt động:
1. **Nhật ký công việc**: Nhân viên cập nhật % hoàn thành từng task nhỏ (0-100%)
2. **Công việc**: Tự động tính % từ trung bình các nhật ký
3. **Dự án**: Tự động tính % từ trung bình các công việc
4. **Trạng thái**: Tự động cập nhật dựa trên % và thời gian

---

## KIẾN TRÚC HỆ THỐNG

### Module `quan_ly_du_an` (Base Module)
- Định nghĩa model `du_an` cơ bản
- Chứa các field: `trang_thai`, `tien_do_du_an`, `tien_do`
- Quản lý thông tin dự án, nhân viên, ngân sách

### Module `quan_ly_cong_viec` (Extension Module)
- Kế thừa và mở rộng model `du_an`
- Thêm logic tính toán tiến độ từ công việc
- Định nghĩa models: `cong_viec`, `nhat_ky_cong_viec`

---

## LUỒNG TÍNH TOÁN TIẾN ĐỘ

### 1. Nhật Ký Công Việc
**File**: `quan_ly_cong_viec/models/nhat_ky_cong_viec.py`

```python
muc_do = fields.Float(
    string='Mức Độ Hoàn Thành (%)', 
    digits=(6, 2), 
    default=0.0
)
```

**Vai trò**: 
- Nhân viên nhập % hoàn thành cho từng lần báo cáo
- Giá trị: 0 - 100%
- Mỗi công việc có thể có nhiều nhật ký

**Ví dụ**:
- Ngày 1: Nhật ký 1 - muc_do = 30%
- Ngày 2: Nhật ký 2 - muc_do = 50%
- Ngày 3: Nhật ký 3 - muc_do = 80%

---

### 2. Công Việc
**File**: `quan_ly_cong_viec/models/cong_viec.py`

```python
phan_tram_cong_viec = fields.Float(
    string="Phần Trăm Hoàn Thành", 
    compute="_compute_phan_tram_cong_viec", 
    store=True
)

@api.depends('nhat_ky_cong_viec_ids.muc_do')
def _compute_phan_tram_cong_viec(self):
    for record in self:
        if record.nhat_ky_cong_viec_ids:
            # Tính trung bình cộng các nhật ký
            total_progress = sum(record.nhat_ky_cong_viec_ids.mapped('muc_do'))
            record.phan_tram_cong_viec = total_progress / len(record.nhat_ky_cong_viec_ids)
        else:
            record.phan_tram_cong_viec = 0.0
```

**Cách tính**:
```
phan_tram_cong_viec = (Tổng muc_do của tất cả nhật ký) / (Số lượng nhật ký)
```

**Ví dụ**: 
Công việc có 3 nhật ký: 30%, 50%, 80%
```
phan_tram_cong_viec = (30 + 50 + 80) / 3 = 53.33%
```

**Trigger**: 
- Tự động chạy khi thêm/sửa/xóa nhật ký
- Được lưu vào database (`store=True`)

---

### 3. Dự Án - Tiến Độ
**File**: `quan_ly_cong_viec/models/du_an.py`

```python
# Override field tien_do
tien_do = fields.Float(
    "Tiến độ (%)",
    compute="_compute_tien_do_tu_cong_viec",
    store=True,
    help="Tiến độ dự án tính từ % hoàn thành công việc"
)

@api.depends('cong_viec_ids', 'cong_viec_ids.phan_tram_cong_viec')
def _compute_tien_do_tu_cong_viec(self):
    """Tính tiến độ dự án dựa trên công việc"""
    for record in self:
        if record.tong_so_cong_viec > 0:
            # Tính trung bình tiến độ của tất cả công việc
            tong_tien_do = sum(record.cong_viec_ids.mapped('phan_tram_cong_viec'))
            record.tien_do = tong_tien_do / record.tong_so_cong_viec
        else:
            record.tien_do = 0.0
```

**Cách tính**:
```
tien_do = (Tổng phan_tram_cong_viec của tất cả công việc) / (Số lượng công việc)
```

**Ví dụ**:
Dự án có 3 công việc: 53.33%, 100%, 20%
```
tien_do = (53.33 + 100 + 20) / 3 = 57.78%
```

**Trigger**:
- Tự động chạy khi thêm/sửa/xóa công việc
- Tự động chạy khi tiến độ công việc thay đổi

---

### 4. Dự Án - Trạng Thái
**File**: `quan_ly_cong_viec/models/du_an.py`

```python
@api.depends('tien_do', 'ngay_bat_dau', 'ngay_ket_thuc_du_kien')
def _compute_tien_do_du_an(self):
    """
    Tự động cập nhật trạng thái dự án dựa trên:
    - Tiến độ công việc (ưu tiên cao nhất)
    - Ngày hiện tại so với kế hoạch
    """
    today = date.today()
    
    for record in self:
        # Ưu tiên 1: Hoàn thành 100% công việc
        if record.tien_do >= 100.0:
            record.tien_do_du_an = 'hoan_thanh'
            record.trang_thai = 'done'
        
        # Ưu tiên 2: Chưa đến ngày bắt đầu
        elif record.ngay_bat_dau and today < record.ngay_bat_dau:
            record.tien_do_du_an = 'chua_bat_dau'
            record.trang_thai = 'planned'
        
        # Ưu tiên 3: Đã bắt đầu nhưng chưa hoàn thành
        elif record.ngay_bat_dau and today >= record.ngay_bat_dau:
            record.tien_do_du_an = 'dang_thuc_hien'
            record.trang_thai = 'in_progress'
        
        # Mặc định
        else:
            record.tien_do_du_an = 'chua_bat_dau'
            record.trang_thai = 'planned'
```

**Logic quyết định trạng thái**:

| Điều kiện | tien_do_du_an | trang_thai | Mô tả |
|-----------|---------------|------------|-------|
| tien_do >= 100% | hoan_thanh | done | Hoàn thành tất cả công việc |
| today < ngay_bat_dau | chua_bat_dau | planned | Chưa đến ngày bắt đầu |
| today >= ngay_bat_dau AND tien_do < 100% | dang_thuc_hien | in_progress | Đang làm |
| Khác | chua_bat_dau | planned | Mặc định |

**Trigger**:
- Tự động chạy khi `tien_do` thay đổi
- Tự động chạy khi `ngay_bat_dau` thay đổi

---

### 5. Thống Kê Công Việc

```python
@api.depends('cong_viec_ids', 'cong_viec_ids.phan_tram_cong_viec')
def _compute_cong_viec_stats(self):
    """Tính toán thống kê công việc"""
    for record in self:
        cong_viec_ids = record.cong_viec_ids
        record.tong_so_cong_viec = len(cong_viec_ids)
        
        # Đếm công việc hoàn thành (100%)
        record.so_cong_viec_hoan_thanh = len([
            cv for cv in cong_viec_ids 
            if cv.phan_tram_cong_viec >= 100.0
        ])
```

**Fields**:
- `tong_so_cong_viec`: Tổng số công việc trong dự án
- `so_cong_viec_hoan_thanh`: Số công việc đã hoàn thành 100%

---

## CHI TIẾT CODE

### Quan hệ giữa các Models

```
du_an (1) ──────< (n) cong_viec (1) ──────< (n) nhat_ky_cong_viec
   │                      │
   │                      └── phan_tram_cong_viec (computed)
   │
   └── tien_do (computed from cong_viec)
   └── trang_thai (computed from tien_do + dates)
```

### Fields quan trọng

**du_an**:
- `tien_do`: Float - Tiến độ % (computed, stored)
- `trang_thai`: Selection - Trạng thái dự án (computed, stored)
- `tien_do_du_an`: Selection - Tương thích với module cũ (computed, stored)
- `cong_viec_ids`: One2many - Danh sách công việc
- `tong_so_cong_viec`: Integer - Tổng số công việc (computed, stored)
- `so_cong_viec_hoan_thanh`: Integer - Số CV hoàn thành (computed, stored)

**cong_viec**:
- `phan_tram_cong_viec`: Float - % hoàn thành (computed, stored)
- `nhat_ky_cong_viec_ids`: One2many - Danh sách nhật ký
- `du_an_id`: Many2one - Dự án (required)

**nhat_ky_cong_viec**:
- `muc_do`: Float - % hoàn thành (manual input)
- `cong_viec_id`: Many2one - Công việc
- `trang_thai`: Selection - Trạng thái nhật ký

### Computed Fields và Dependencies

```python
# Sơ đồ dependency chain:

nhat_ky_cong_viec.muc_do (manual)
    ↓ triggers
cong_viec.phan_tram_cong_viec (@api.depends('nhat_ky_cong_viec_ids.muc_do'))
    ↓ triggers
du_an.tien_do (@api.depends('cong_viec_ids.phan_tram_cong_viec'))
    ↓ triggers
du_an.trang_thai (@api.depends('tien_do', 'ngay_bat_dau', 'ngay_ket_thuc_du_kien'))
```

---

## VÍ DỤ MINH HỌA

### Scenario: Dự án Phát triển Website

**Setup ban đầu**:
```
Dự án: "Phát triển Website Công ty"
- Ngày bắt đầu: 01/01/2026
- Ngày kết thúc dự kiến: 31/03/2026
- Ngày hiện tại: 15/01/2026
```

**Công việc 1: Thiết kế giao diện**
- Nhật ký 1 (05/01): muc_do = 40%
- Nhật ký 2 (10/01): muc_do = 70%
- Nhật ký 3 (15/01): muc_do = 100%
- **→ phan_tram_cong_viec = (40 + 70 + 100) / 3 = 70%**

**Công việc 2: Lập trình Backend**
- Nhật ký 1 (08/01): muc_do = 30%
- Nhật ký 2 (12/01): muc_do = 50%
- **→ phan_tram_cong_viec = (30 + 50) / 2 = 40%**

**Công việc 3: Lập trình Frontend**
- Nhật ký 1 (10/01): muc_do = 20%
- **→ phan_tram_cong_viec = 20%**

**Tính tiến độ dự án**:
```
tien_do = (70 + 40 + 20) / 3 = 43.33%
```

**Xác định trạng thái**:
```
- tien_do = 43.33% < 100% ❌ Không phải hoàn thành
- today (15/01) >= ngay_bat_dau (01/01) ✅
- tien_do < 100% ✅

→ tien_do_du_an = 'dang_thuc_hien'
→ trang_thai = 'in_progress'
```

**Thống kê**:
```
- tong_so_cong_viec = 3
- so_cong_viec_hoan_thanh = 0 (không có công việc nào 100%)
```

---

### Scenario tiếp: Sau 1 tháng

**Ngày hiện tại: 15/02/2026**

**Công việc 1: Thiết kế giao diện** (Không đổi)
- **phan_tram_cong_viec = 70%**

**Công việc 2: Lập trình Backend** (Cập nhật)
- Nhật ký 3 (25/01): muc_do = 80%
- Nhật ký 4 (10/02): muc_do = 100%
- **→ phan_tram_cong_viec = (30 + 50 + 80 + 100) / 4 = 65%**

**Công việc 3: Lập trình Frontend** (Cập nhật)
- Nhật ký 2 (20/01): muc_do = 50%
- Nhật ký 3 (05/02): muc_do = 80%
- Nhật ký 4 (15/02): muc_do = 100%
- **→ phan_tram_cong_viec = (20 + 50 + 80 + 100) / 4 = 62.5%**

**Tính tiến độ dự án**:
```
tien_do = (70 + 65 + 62.5) / 3 = 65.83%
```

**Trạng thái**:
```
→ tien_do_du_an = 'dang_thuc_hien'
→ trang_thai = 'in_progress'
```

**Thống kê**:
```
- tong_so_cong_viec = 3
- so_cong_viec_hoan_thanh = 0
```

---

### Scenario cuối: Hoàn thành dự án

**Ngày hiện tại: 25/03/2026**

**Tất cả công việc hoàn thành 100%**:
- Công việc 1: phan_tram_cong_viec = 100%
- Công việc 2: phan_tram_cong_viec = 100%
- Công việc 3: phan_tram_cong_viec = 100%

**Tính tiến độ dự án**:
```
tien_do = (100 + 100 + 100) / 3 = 100%
```

**Trạng thái**:
```
- tien_do >= 100% ✅

→ tien_do_du_an = 'hoan_thanh'
→ trang_thai = 'done'
```

**Thống kê**:
```
- tong_so_cong_viec = 3
- so_cong_viec_hoan_thanh = 3
```

---

## LƯU Ý QUAN TRỌNG

### 1. Computed Fields với store=True
- Tất cả computed fields đều có `store=True`
- Giá trị được lưu vào database để tăng hiệu suất
- Tự động cập nhật khi dependencies thay đổi

### 2. Cascade Dependencies
- Khi thêm/sửa nhật ký → tự động tính lại % công việc
- Khi % công việc thay đổi → tự động tính lại tiến độ dự án
- Khi tiến độ dự án thay đổi → tự động cập nhật trạng thái

### 3. Performance
- Odoo tự động batch update các computed fields
- Không cần lo về vấn đề performance với số lượng record vừa phải
- Với dự án lớn (>1000 công việc), cân nhắc thêm index

### 4. Validation
- Constraint đảm bảo không thêm công việc vào dự án đã hoàn thành
- Nhật ký công việc có constraint: 0 <= muc_do <= 100

---

## CÁCH SỬ DỤNG

### Bước 1: Tạo Dự Án
```
Thông tin dự án → Ngày bắt đầu, kết thúc → Người quản lý
```

### Bước 2: Thêm Công Việc
```
Tab "Công Việc" → Tạo công việc → Gán nhân viên
```

### Bước 3: Cập Nhật Nhật Ký
```
Công việc → Tab "Nhật Ký" → Thêm nhật ký với muc_do
```

### Bước 4: Xem Tiến Độ
```
Dự án tự động tính tiến độ và cập nhật trạng thái
```

---

## TROUBLESHOOTING

### Tiến độ không cập nhật?
1. Kiểm tra nhật ký có field `muc_do` hợp lệ (0-100)
2. Kiểm tra quan hệ: nhật ký → công việc → dự án
3. Force recompute: Edit và Save lại record

### Trạng thái không đúng?
1. Kiểm tra `ngay_bat_dau` của dự án
2. Kiểm tra `tien_do` đã đạt 100% chưa
3. Xem log để debug dependencies

### Performance chậm?
1. Kiểm tra số lượng công việc và nhật ký
2. Xem xét tăng server resources
3. Optimize dependencies nếu cần

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 08/01/2026  
**Tác giả**: Development Team

