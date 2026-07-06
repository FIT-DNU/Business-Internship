# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Chức vụ nhân viên'
    _rec_name = 'ten_chuc_vu'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả chức vụ")
    nhan_vien_ids = fields.One2many("nhan_vien", "chuc_vu_id", string="Nhân viên")
    
    _sql_constraints = [
        ('unique_ma_chuc_vu', 'UNIQUE(ma_chuc_vu)', 'Mã chức vụ đã tồn tại!')
    ]





