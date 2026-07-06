# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GiaiDoanCongViec(models.Model):
    _name = 'giai_doan_cong_viec'
    _description = 'Giai Đoạn Công Việc'
    _rec_name = 'ten_giai_doan'
    _order = 'thu_tu'

    ten_giai_doan = fields.Char(string='Tên Giai Đoạn', required=True)
    thu_tu = fields.Integer(string='Thứ Tự', required=True, default=1)
    mo_ta = fields.Text(string='Mô Tả')
    du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')
    # cong_viec_ids được thêm bởi module quan_ly_cong_viec


