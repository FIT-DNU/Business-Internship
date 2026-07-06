# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LichSuLamViec(models.Model):
    _name = 'lich_su_lam_viec'
    _description = 'Lịch sử làm việc'
    _rec_name = 'ten_cong_viec'

    ten_cong_viec = fields.Char("Tên công việc đã làm", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức Vụ", related="nhan_vien_id.chuc_vu_id", store=True, readonly=True)
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", related="nhan_vien_id.phong_ban_id", store=True, readonly=True)
    ngay_bat_dau = fields.Date("Ngày bắt đầu", default=fields.Date.today)
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    mo_ta = fields.Text("Mô tả công việc")





