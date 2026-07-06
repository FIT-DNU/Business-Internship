# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Phòng ban'
    _rec_name = 'ten_phong_ban'

    ma_phong_ban = fields.Char("Mã phòng ban", required=True)
    ten_phong_ban = fields.Char("Tên phòng ban", required=True)
    mo_ta = fields.Text("Mô tả phòng ban")
    nhan_vien_ids = fields.One2many('nhan_vien', 'phong_ban_id', string="Nhân viên")
    
    _sql_constraints = [
        ('unique_ma_phong_ban', 'UNIQUE(ma_phong_ban)', 'Mã phòng ban đã tồn tại!')
    ]





