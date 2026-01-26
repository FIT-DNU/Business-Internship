# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    # --- Các trường dữ liệu ---
    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    anh = fields.Binary("Ảnh")
    
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    
    # Đã sửa: compute="_compute_so_nguoi_bang_tuoi" để khớp với tên hàm bên dưới
    so_nguoi_bang_tuoi = fields.Integer(
        "Số người bằng tuổi", 
        compute="_compute_so_nguoi_bang_tuoi",
        store=True
    )

    luong_co_ban = fields.Float(string="Lương cơ bản", default=0)
    phu_cap = fields.Float(string="Phụ cấp", default=0)

    # Quan hệ với các bảng khác
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string="Danh sách lịch sử công tác"
    )
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap", 
        inverse_name="nhan_vien_id", 
        string="Danh sách chứng chỉ bằng cấp"
    )

    # Đã sửa lỗi chính tả: _sql_constraints (phải có chữ 't')
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất!')
    ]

    # --- Các hàm xử lý logic (Methods) ---

    @api.depends("tuoi")
    def _compute_so_nguoi_bang_tuoi(self):
        """Tính số người có cùng tuổi, tránh lỗi ID tạm thời (NewId) khi tạo mới"""
        for record in self:
            if record.tuoi:
                # Sử dụng _origin để lấy ID thật từ database
                real_id = record._origin.id
                domain = [('tuoi', '=', record.tuoi)]
                
                # Nếu bản ghi đã có ID thật (đã lưu), loại trừ chính nó ra khỏi danh sách đếm
                if real_id:
                    domain.append(('id', '!=', real_id))
                
                # Sử dụng search_count để tối ưu hiệu năng thay vì len(search)
                record.so_nguoi_bang_tuoi = self.env['nhan_vien'].search_count(domain)
            else:
                record.so_nguoi_bang_tuoi = 0

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        """Tự động ghép Họ tên đệm và Tên"""
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = f"{record.ho_ten_dem} {record.ten}".strip()
            else:
                record.ho_va_ten = record.ten or record.ho_ten_dem or ""

    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        """Gợi ý mã định danh dựa trên tên và các chữ cái đầu của họ đệm"""
        for record in self:
            if record.ho_ten_dem and record.ten:
                # Lấy các chữ cái đầu của họ và tên đệm
                chu_cai_dau = ''.join([tu[0].lower() for tu in record.ho_ten_dem.split() if tu])
                record.ma_dinh_danh = f"{record.ten.lower()}{chu_cai_dau}"

    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        """Tính tuổi dựa trên năm sinh so với năm hiện tại"""
        for record in self:
            if record.ngay_sinh:
                year_now = date.today().year
                record.tuoi = year_now - record.ngay_sinh.year
            else:
                record.tuoi = 0

    @api.constrains('tuoi')
    def _check_tuoi(self):
        """Ràng buộc không cho phép nhân viên dưới 18 tuổi"""
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Nhân viên phải từ 18 tuổi trở lên!")