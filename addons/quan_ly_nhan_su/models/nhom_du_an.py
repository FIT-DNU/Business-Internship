# -*- coding: utf-8 -*-

from odoo import models, fields

class NhomDuAn(models.Model):
    _name = 'nhom_du_an'
    _description = 'Nhóm Dự Án'
    _rec_name = 'ten_nhom'

    ten_nhom = fields.Char(string='Tên Nhóm', required=True)
    mo_ta = fields.Text(string='Mô tả')
    nhan_vien_ids = fields.Many2many('nhan_vien', 'nhom_du_an_nhan_vien_rel', 
                                      'nhom_du_an_id', 'nhan_vien_id', 
                                      string='Thành Viên')





