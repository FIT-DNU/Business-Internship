from odoo import models, fields

class ChungChi(models.Model):
    _name = 'chung_chi'
    _description = 'Chứng chỉ'

    ten_chung_chi = fields.Char("Tên chứng chỉ", required=True)
    nhan_vien_id = fields.Many2one(
        'nhan_vien', string="Nhân viên", ondelete='cascade'
    )
    ngay_cap = fields.Date("Ngày cấp")
    noi_cap = fields.Char("Nơi cấp")