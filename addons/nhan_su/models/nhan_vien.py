from odoo import models, fields, api

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Thông tin nhân viên hoàn thiện'
    _rec_name = 'ten_nhan_vien' # Giúp các module khác hiển thị Tên thay vì ID

    # --- Các trường cũ của ông ---
    ma_dinh_danh = fields.Char("Mã nhân viên", required=True)
    ten_nhan_vien = fields.Char("Họ và tên", required=True)
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")

    # --- Các trường mới thêm vào ---
    chuc_vu = fields.Char("Chức vụ")
    
    bang_cap = fields.Selection([
        ('trung_cap', 'Trung cấp'),
        ('cao_dang', 'Cao đẳng'),
        ('dai_hoc', 'Đại học (Cử nhân/Kỹ sư)'),
        ('thac_si', 'Thạc sĩ'),
        ('tien_si', 'Tiến sĩ')
    ], string="Bằng cấp cao nhất", default='dai_hoc')
    
    chuyen_nganh = fields.Char("Chuyên ngành đào tạo")
    
    ngay_vao_lam = fields.Date("Ngày vào làm")