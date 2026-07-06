# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    so_cong_viec_dang_lam = fields.Integer(
        string='Số công việc đang thực hiện',
        compute='_compute_so_cong_viec_dang_lam',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_so_cong_viec_dang_lam(self):
        CongViec = self.env['cong_viec']
        for nv in self:
            nv.so_cong_viec_dang_lam = CongViec.search_count([
                ('status', '=', 'in_progress'),
                '|',
                ('nguoi_phu_trach_id', '=', nv.id),
                ('nhan_vien_ids', 'in', nv.id),
            ])
