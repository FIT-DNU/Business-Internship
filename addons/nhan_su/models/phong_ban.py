from odoo import models, fields

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Phòng ban'
    _order = 'ten_phong asc'

    ma_phong = fields.Char("Mã phòng", required=True)
    ten_phong = fields.Char("Tên phòng", required=True)
    mo_ta = fields.Text("Mô tả")

    nhan_vien_ids = fields.One2many(
        'nhan_vien', 'phong_ban_id', string="Nhân viên"
    )