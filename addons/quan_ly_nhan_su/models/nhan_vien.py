# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Nhân viên'
    _rec_name = 'display_name'

    # Thông tin cơ bản
    ma_dinh_danh = fields.Char("Mã Định Danh", required=True)
    ho_ten_dem = fields.Char("Họ Tên Đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và Tên", compute='_compute_ho_va_ten', store=True)
    display_name = fields.Char(string='Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    # Thông tin cá nhân
    ngay_sinh = fields.Date("Ngày Sinh")
    gioi_tinh = fields.Selection(
        selection=[
            ('nam', 'Nam'),
            ('nu', 'Nữ'),
            ('khac', 'Khác'),
        ],
        string="Giới Tính"
    )
    que_quan = fields.Char("Quê Quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số Điện Thoại")
    image = fields.Binary("Ảnh nhân viên")
    
    # Thông tin công việc
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức vụ", ondelete="set null")
    phong_ban_id = fields.Many2one("phong_ban", string="Phòng ban", ondelete="set null")
    lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', 'nhan_vien_id', string="Lịch Sử Làm Việc")
    nhom_du_an_ids = fields.Many2many('nhom_du_an', 'nhan_vien_nhom_du_an_rel',
                                      'nhan_vien_id', 'nhom_du_an_id',
                                      string='Nhóm Dự Án')
    
    # Quan hệ với dự án và công việc - Để trống, sẽ được thêm bởi module mở rộng
    # Không định nghĩa ở đây để tránh lỗi khi cài module quan_ly_nhan_su trước

    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Email đã tồn tại, vui lòng chọn email khác!'),
        ('unique_ma_dinh_danh', 'UNIQUE(ma_dinh_danh)', 'Mã định danh đã tồn tại, vui lòng chọn mã khác!')
    ]

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = f"{record.ho_ten_dem} {record.ten}".strip()
            else:
                record.ho_va_ten = False

    @api.onchange("ten", "ho_ten_dem")
    def _onchange_tinh_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = ''.join([tu[0] for tu in record.ho_ten_dem.lower().split() if tu])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
            else:
                record.ma_dinh_danh = False

    @api.depends('ho_va_ten', 'ma_dinh_danh')
    def _compute_display_name(self):
        for record in self:
            if record.ho_va_ten and record.ma_dinh_danh:
                record.display_name = f"{record.ho_va_ten} ({record.ma_dinh_danh})"
            elif record.ho_va_ten:
                record.display_name = record.ho_va_ten
            else:
                record.display_name = ""
