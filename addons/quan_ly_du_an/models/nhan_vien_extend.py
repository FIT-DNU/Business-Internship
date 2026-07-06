# -*- coding: utf-8 -*-

from odoo import models, fields

class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'
    
    # Thêm các field quan hệ với dự án và công việc
    du_an_ids = fields.Many2many('du_an', 'nhan_vien_du_an_rel', 
                                 'nhan_vien_id', 'du_an_id', 
                                 string='Dự Án Đang Tham Gia')
    cong_viec_ids = fields.Many2many('cong_viec', 'nhan_vien_cong_viec_rel', 
                                    'nhan_vien_id', 'cong_viec_id', 
                                    string='Công Việc Tham Gia')




