# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date

class DuAn(models.Model):
    _inherit = 'du_an'

    # Quan hệ với công việc
    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string='Danh sách công việc')
    
    # Tổng số công việc
    tong_so_cong_viec = fields.Integer(
        string="Tổng số công việc",
        compute="_compute_cong_viec_stats",
        store=True
    )
    
    # Số công việc hoàn thành
    so_cong_viec_hoan_thanh = fields.Integer(
        string="Số công việc hoàn thành",
        compute="_compute_cong_viec_stats",
        store=True
    )
    
    # Override field tien_do để thêm compute từ công việc
    tien_do = fields.Float(
        "Tiến độ (%)",
        compute="_compute_tien_do_tu_cong_viec",
        store=True,
        help="Tiến độ dự án tính từ % hoàn thành công việc"
    )

    @api.depends('cong_viec_ids', 'cong_viec_ids.phan_tram_cong_viec')
    def _compute_cong_viec_stats(self):
        """Tính toán thống kê công việc"""
        for record in self:
            cong_viec_ids = record.cong_viec_ids
            record.tong_so_cong_viec = len(cong_viec_ids)
            
            # Đếm công việc hoàn thành (100%)
            record.so_cong_viec_hoan_thanh = len([cv for cv in cong_viec_ids if cv.phan_tram_cong_viec >= 100.0])

    @api.depends('cong_viec_ids', 'cong_viec_ids.phan_tram_cong_viec')
    def _compute_tien_do_tu_cong_viec(self):
        """Tính tiến độ dự án dựa trên công việc"""
        for record in self:
            if record.tong_so_cong_viec > 0:
                # Tính trung bình tiến độ của tất cả công việc
                tong_tien_do = sum(record.cong_viec_ids.mapped('phan_tram_cong_viec'))
                record.tien_do = tong_tien_do / record.tong_so_cong_viec
            else:
                record.tien_do = 0.0

    @api.depends('tien_do', 'ngay_bat_dau', 'ngay_ket_thuc_du_kien')
    def _compute_tien_do_du_an(self):
        """
        Tự động cập nhật trạng thái dự án dựa trên:
        - Tiến độ công việc (ưu tiên cao nhất)
        - Ngày hiện tại so với kế hoạch
        """
        today = date.today()
        
        for record in self:
            # Nếu hoàn thành 100% công việc -> Hoàn thành
            if record.tien_do >= 100.0:
                record.tien_do_du_an = 'hoan_thanh'
                record.trang_thai = 'done'
            # Nếu chưa đến ngày bắt đầu -> Sắp bắt đầu
            elif record.ngay_bat_dau and today < record.ngay_bat_dau:
                record.tien_do_du_an = 'chua_bat_dau'
                record.trang_thai = 'planned'
            # Nếu đã bắt đầu nhưng chưa hoàn thành -> Đang thực hiện
            elif record.ngay_bat_dau and today >= record.ngay_bat_dau:
                record.tien_do_du_an = 'dang_thuc_hien'
                record.trang_thai = 'in_progress'
            # Mặc định
            else:
                record.tien_do_du_an = 'chua_bat_dau'
                record.trang_thai = 'planned'

