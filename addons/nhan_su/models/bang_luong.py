from odoo import models, fields, api
from datetime import datetime, timedelta


class BangLuong(models.Model):
    _name = 'bang_luong'
    _description = 'Bảng lương theo tháng'
    _rec_name = 'display_name'
    _order = 'thang_nam_dau desc, nhan_vien_id'

    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True, ondelete='cascade')
    luong_co_ban = fields.Float("Lương cơ bản 1 ngày công", default=500000, help="Lương cơ bản cho 1 ngày công (mặc định 500.000 VND)")
    so_cong = fields.Float("Số công", compute="_compute_so_cong", store=True, 
                           help="Số công = số ngày chấm công trong tháng (1 ngày = 1 công)")
    tong_so_gio_lam = fields.Float("Tổng số giờ làm", compute="_compute_tong_so_gio_lam", store=True,
                                    help="Tổng số giờ làm trong tháng từ bảng chấm công")
    so_ngay_dung_gio = fields.Integer("Số ngày đúng giờ", compute="_compute_thuong_phat", store=True)
    so_ngay_muon = fields.Integer("Số ngày muộn", compute="_compute_thuong_phat", store=True)
    thuong = fields.Float("Thưởng", compute="_compute_thuong_phat", store=True, 
                          help="Thưởng tự động: 10.000 VND/ngày đúng giờ")
    phat = fields.Float("Phạt", compute="_compute_thuong_phat", store=True,
                        help="Phạt tự động: 10.000 VND/ngày muộn")
    luong_thuc_nhan = fields.Float("Lương cơ bản", compute="_compute_luong_nhan", store=True,
                                   help="Lương cơ bản = Lương cơ bản 1 ngày công × Số công")
    luong_nhan = fields.Float("Lương nhận", compute="_compute_luong_nhan", store=True,
                              help="Lương nhận = Lương cơ bản 1 ngày công × Số công + Thưởng - Phạt")
    cham_cong_ids = fields.One2many(
        "cham_cong",
        inverse_name="nhan_vien_id",
        string="Danh sách chấm công",
        domain="[('ngay_cham_cong', '>=', thang_nam_dau), ('ngay_cham_cong', '<=', thang_nam_cuoi)]"
    )
    thang_nam_dau = fields.Date("Tháng năm đầu", required=True,
                                 default=lambda self: fields.Date.today().replace(day=1),
                                 help="Chọn tháng để tính lương (mặc định tháng hiện tại)")
    thang_nam_cuoi = fields.Date("Tháng năm cuối", compute="_compute_thang_nam_dates", store=True, readonly=True)
    display_name = fields.Char("Tên hiển thị", compute="_compute_display_name", store=True)
    ghi_chu = fields.Text("Ghi chú")

    @api.depends("thang_nam_dau")
    def _compute_thang_nam_dates(self):
        for record in self:
            if record.thang_nam_dau:
                # Tính ngày cuối tháng từ ngày đầu tháng
                if record.thang_nam_dau.month == 12:
                    record.thang_nam_cuoi = fields.Date.to_date(f"{record.thang_nam_dau.year + 1}-01-01") - timedelta(days=1)
                else:
                    record.thang_nam_cuoi = fields.Date.to_date(f"{record.thang_nam_dau.year}-{record.thang_nam_dau.month + 1:02d}-01") - timedelta(days=1)
            else:
                record.thang_nam_cuoi = False

    @api.depends("nhan_vien_id", "thang_nam_dau")
    def _compute_display_name(self):
        for record in self:
            if record.nhan_vien_id and record.thang_nam_dau:
                thang_nam_str = record.thang_nam_dau.strftime("%m/%Y")
                record.display_name = f"{record.nhan_vien_id.ho_va_ten} - {thang_nam_str}"
            else:
                record.display_name = "Bảng lương"

    @api.depends("nhan_vien_id", "thang_nam_dau", "thang_nam_cuoi")
    def _compute_so_cong(self):
        for record in self:
            if record.thang_nam_dau and record.thang_nam_cuoi and record.nhan_vien_id:
                # Lấy tất cả chấm công trong tháng của nhân viên (không tính vắng)
                cham_cong_records = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_cham_cong', '>=', record.thang_nam_dau),
                    ('ngay_cham_cong', '<=', record.thang_nam_cuoi),
                    ('trang_thai', '!=', 'vang')
                ])
                # Số công = số ngày chấm công (1 ngày = 1 công)
                record.so_cong = len(cham_cong_records)
            else:
                record.so_cong = 0

    @api.depends("nhan_vien_id", "thang_nam_dau", "thang_nam_cuoi")
    def _compute_tong_so_gio_lam(self):
        for record in self:
            if record.thang_nam_dau and record.thang_nam_cuoi and record.nhan_vien_id:
                # Lấy tất cả chấm công trong tháng của nhân viên
                cham_cong_records = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_cham_cong', '>=', record.thang_nam_dau),
                    ('ngay_cham_cong', '<=', record.thang_nam_cuoi)
                ])
                record.tong_so_gio_lam = sum(cham_cong_records.mapped('so_gio_lam'))
            else:
                record.tong_so_gio_lam = 0

    @api.depends("nhan_vien_id", "thang_nam_dau", "thang_nam_cuoi")
    def _compute_thuong_phat(self):
        for record in self:
            if record.thang_nam_dau and record.thang_nam_cuoi and record.nhan_vien_id:
                # Lấy tất cả chấm công trong tháng của nhân viên
                cham_cong_records = self.env['cham_cong'].search([
                    ('nhan_vien_id', '=', record.nhan_vien_id.id),
                    ('ngay_cham_cong', '>=', record.thang_nam_dau),
                    ('ngay_cham_cong', '<=', record.thang_nam_cuoi)
                ])
                # Đếm số ngày đúng giờ và muộn
                record.so_ngay_dung_gio = len(cham_cong_records.filtered(lambda r: r.trang_thai == 'dung_gio'))
                record.so_ngay_muon = len(cham_cong_records.filtered(lambda r: r.trang_thai == 'muon'))
                # Tính thưởng: 10.000 VND/ngày đúng giờ
                record.thuong = record.so_ngay_dung_gio * 10000
                # Tính phạt: 10.000 VND/ngày muộn
                record.phat = record.so_ngay_muon * 10000
            else:
                record.so_ngay_dung_gio = 0
                record.so_ngay_muon = 0
                record.thuong = 0
                record.phat = 0

    @api.depends("so_cong", "luong_co_ban", "thuong", "phat")
    def _compute_luong_nhan(self):
        for record in self:
            # Đảm bảo thuong và phat có giá trị (mặc định 0 nếu None hoặc False)
            thuong_value = record.thuong or 0.0
            phat_value = record.phat or 0.0
            
            if record.so_cong > 0 and record.luong_co_ban > 0:
                # Lương cơ bản = Lương cơ bản 1 ngày công × Số công
                record.luong_thuc_nhan = record.luong_co_ban * record.so_cong
                # Lương nhận = Lương cơ bản 1 ngày công × Số công + Thưởng - Phạt
                record.luong_nhan = record.luong_thuc_nhan + thuong_value - phat_value
            else:
                record.luong_thuc_nhan = 0.0
                record.luong_nhan = 0.0
