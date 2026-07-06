# -*- coding: utf-8 -*-

from odoo import models, fields

class TaiNguyen(models.Model):
    _name = 'tai_nguyen'
    _description = 'Tài Nguyên Dự Án'
    _rec_name = 'ten_tai_nguyen'

    ten_tai_nguyen = fields.Char(string='Tên Tài Nguyên', required=True)
    so_luong = fields.Integer(string='Số Lượng', required=True, default=1)
    don_vi = fields.Char(string='Đơn Vị', default='cái')
    mo_ta = fields.Text(string='Mô Tả')
    du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')





