from odoo import models, fields, api
from datetime import date
from calendar import monthrange  # Thư viện giúp lấy số ngày chính xác trong tháng

class TinhLuong(models.Model):
    _name = 'tinh_luong'
    _description = 'Bảng tính lương nhân viên'
    _order = 'nam desc, thang desc'
    _rec_name = 'nhan_vien_id'

    # --- Thông tin chung ---
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    thang = fields.Selection([
        ('1', 'Tháng 1'), ('2', 'Tháng 2'), ('3', 'Tháng 3'), ('4', 'Tháng 4'),
        ('5', 'Tháng 5'), ('6', 'Tháng 6'), ('7', 'Tháng 7'), ('8', 'Tháng 8'),
        ('9', 'Tháng 9'), ('10', 'Tháng 10'), ('11', 'Tháng 11'), ('12', 'Tháng 12')
    ], string="Tháng", required=True, default=str(date.today().month))
    
    nam = fields.Integer(string="Năm", required=True, default=date.today().year)
    cong_chuan = fields.Float(string="Công khóa (Ngày)", default=26, help="Số ngày làm việc tiêu chuẩn trong tháng")
    
    # --- Dữ liệu lấy từ Hồ sơ nhân viên ---
    luong_co_ban = fields.Float(string="Lương cơ bản", compute="_compute_thong_tin_nhan_vien", store=True, readonly=False)
    phu_cap = fields.Float(string="Phụ cấp", compute="_compute_thong_tin_nhan_vien", store=True, readonly=False)
    
    # --- Dữ liệu tự động tính từ Chấm công ---
    so_cong_thuc_te = fields.Float(string="Số công thực tế", compute="_compute_tu_cham_cong", store=True)
    tien_ot = fields.Float(string="Tiền OT", compute="_compute_tu_cham_cong", store=True)
    
    # --- Dữ liệu nhập thêm ---
    thuong_phat = fields.Float(string="Thưởng/Phạt", default=0, help="Nhập số âm nếu là phạt (ví dụ: -50000)")

    # --- Kết quả tính toán ---
    luong_ngay = fields.Float(string="Lương ngày", compute="_compute_luong_cuoi", store=True)
    tong_luong = fields.Float(string="Tổng thực lĩnh", compute="_compute_luong_cuoi", store=True)

    @api.depends('nhan_vien_id')
    def _compute_thong_tin_nhan_vien(self):
        """Tự động điền lương CB và phụ cấp khi chọn nhân viên"""
        for record in self:
            if record.nhan_vien_id:
                record.luong_co_ban = record.nhan_vien_id.luong_co_ban
                record.phu_cap = record.nhan_vien_id.phu_cap
            else:
                record.luong_co_ban = 0
                record.phu_cap = 0

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_tu_cham_cong(self):
        """Tự động tính tổng công và tiền OT từ bảng chấm công"""
        for record in self:
            if record.nhan_vien_id and record.thang and record.nam:
                # 1. Xác định ngày bắt đầu và ngày kết thúc chính xác của tháng
                try:
                    thang_int = int(record.thang)
                    nam_int = int(record.nam)
                    # monthrange trả về (thứ_đầu_tuần, số_ngày_trong_tháng)
                    _, days_in_month = monthrange(nam_int, thang_int)
                except Exception:
                    days_in_month = 31 # Fallback nếu có lỗi
                
                start_date = f'{record.nam}-{record.thang}-01'
                end_date = f'{record.nam}-{record.thang}-{days_in_month}'

                # 2. Tìm các phiếu chấm công trong khoảng thời gian này
                cham_cong_recs = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_cham_cong', '>=', start_date),
                    ('ngay_cham_cong', '<=', end_date),
                ])
                
                # 3. Tổng hợp dữ liệu
                record.so_cong_thuc_te = len(cham_cong_recs) # Đếm số ngày đi làm
                record.tien_ot = sum(line.tien_ot for line in cham_cong_recs) # Tổng tiền OT
            else:
                record.so_cong_thuc_te = 0
                record.tien_ot = 0

    @api.depends('luong_co_ban', 'cong_chuan', 'so_cong_thuc_te', 'phu_cap', 'thuong_phat', 'tien_ot')
    def _compute_luong_cuoi(self):
        """Tính lương cuối cùng"""
        for record in self:
            if record.cong_chuan > 0:
                # Lương ngày = Lương CB / Công chuẩn
                record.luong_ngay = record.luong_co_ban / record.cong_chuan
                
                # Tổng = (Lương ngày * Công thực) + Phụ cấp + Thưởng/Phạt + OT
                record.tong_luong = (record.luong_ngay * record.so_cong_thuc_te) + \
                                    record.phu_cap + \
                                    record.thuong_phat + \
                                    record.tien_ot
            else:
                record.luong_ngay = 0
                record.tong_luong = 0