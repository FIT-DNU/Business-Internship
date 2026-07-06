# -*- coding: utf-8 -*-

from odoo import models, fields


class ThongBaoNoiBo(models.Model):
    _name = 'thong_bao_noi_bo'
    _description = 'Thông báo nội bộ'
    _order = 'create_date desc'

    name = fields.Char(string='Tiêu đề', required=True)
    noi_dung = fields.Text(string='Nội dung')

    nhan_vien_id = fields.Many2one('nhan_vien', string='Người nhận', required=True, ondelete='cascade')

    cong_viec_id = fields.Many2one('cong_viec', string='Công việc', ondelete='set null')
    du_an_id = fields.Many2one('du_an', string='Dự án', ondelete='set null')

    loai = fields.Selection(
        [
            ('deadline_48h', 'Nhắc hạn (48h)'),
            ('deadline_24h', 'Nhắc hạn (24h)'),
            ('overdue', 'Quá hạn'),
            ('overdue_escalate', 'Quá hạn (escalate)'),
            ('budget_80', 'Ngân sách (>=80%)'),
            ('budget_over', 'Ngân sách (>100%)'),
            ('workload', 'Quá tải'),
        ],
        string='Loại',
        required=True,
    )

    trang_thai = fields.Selection(
        [
            ('unread', 'Chưa đọc'),
            ('read', 'Đã đọc'),
        ],
        string='Trạng thái',
        default='unread',
        required=True,
    )
