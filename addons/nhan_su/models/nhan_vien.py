from odoo import models, fields, api


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_va_ten = fields.Char("Họ và tên", required=True)
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string = "Danh sách lịch sử công tác")
