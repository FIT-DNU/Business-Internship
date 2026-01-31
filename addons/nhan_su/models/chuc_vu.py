from odoo import models, fields

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Chức vụ'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    phu_cap = fields.Float("Phụ cấp")
    mo_ta = fields.Text("Mô tả")