# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVien(models.Model):
    _inherit = 'nhan_vien'

    # Liên kết với module dự án
    du_an_ids = fields.Many2many(
        "du_an",
        "du_an_nhan_vien_rel",
        "nhan_vien_id",
        "du_an_id",
        string="Danh sách dự án tham gia"
    )
    # Note: du_an_nhan_vien_ids được truy cập qua du_an.du_an_nhan_vien_ids.filtered(lambda r: r.nhan_vien_id == self)
    # Hoặc có thể thêm sau khi module đã được cài đặt thành công
