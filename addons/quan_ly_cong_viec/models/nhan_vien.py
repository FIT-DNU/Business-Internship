# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVien(models.Model):
    _inherit = 'nhan_vien'

    # Liên kết với module công việc
    cong_viec_ids = fields.Many2many(
        "cong_viec",
        "cong_viec_nhan_vien_rel",
        "nhan_vien_id",
        "cong_viec_id",
        string="Danh sách công việc tham gia"
    )
