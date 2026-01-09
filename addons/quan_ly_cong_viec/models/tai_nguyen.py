from odoo import models, fields

class TaiNguyen(models.Model):
    _name = 'tai_nguyen'
    _description = 'Tài Nguyên Dự Án'

    ten_tai_nguyen = fields.Char(string='Tên Tài Nguyên', required=True)
    so_luong = fields.Integer(string='Số Lượng', required=True, default=1)
    du_an_id = fields.Many2one('du_an', string='Dự Án', ondelete='cascade')
 