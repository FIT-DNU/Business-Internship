# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DuAnExtend(models.Model):
    _inherit = 'du_an'
    
    # Thêm các field quan hệ với công việc
    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string='Công Việc')
    danh_gia_nhan_vien_ids = fields.One2many('danh_gia_nhan_vien', 'du_an_id', string='Đánh Giá Nhân Viên')

class GiaiDoanCongViecExtend(models.Model):
    _inherit = 'giai_doan_cong_viec'
    
    # Thêm field quan hệ với công việc
    cong_viec_ids = fields.One2many('cong_viec', 'giai_doan_id', string='Công Việc Trong Giai Đoạn')
    
    @api.depends('cong_viec_ids.phan_tram_cong_viec')
    def _compute_phan_tram_du_an(self):
        """Tính tiến độ dự án dựa trên tiến độ các công việc"""
        for record in self:
            if record.cong_viec_ids:
                total_progress = sum(record.cong_viec_ids.mapped('phan_tram_cong_viec'))
                record.phan_tram_du_an = total_progress / len(record.cong_viec_ids)
            else:
                # Nếu chưa có công việc, tính theo trạng thái
                if record.tien_do_du_an == 'chua_bat_dau':
                    record.phan_tram_du_an = 0.0
                elif record.tien_do_du_an == 'hoan_thanh':
                    record.phan_tram_du_an = 100.0
                else:
                    record.phan_tram_du_an = record.phan_tram_du_an or 0.0

