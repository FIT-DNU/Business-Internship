from odoo import models, fields, api

class BangXepHangKhachHang(models.Model):
    _name = 'bang_xep_hang_khach_hang'
    _description = 'Bảng Xếp Hạng Khách Hàng'
    _order = 'xep_hang asc'  # Sắp xếp theo xếp hạng tăng dần

    khach_hang_id = fields.Many2one(
        'thong_tin_khach_hang',
        string="Khách hàng",
        required=True,
        ondelete='cascade'
    )
    tong_tien_chi_tieu = fields.Float(
        "Tổng tiền đã chi tiêu",
        related='khach_hang_id.tong_tien_chi_tieu',
        store=True
    )
    xep_hang = fields.Integer("Xếp hạng", compute="_compute_xep_hang", store=True)

    @api.depends('tong_tien_chi_tieu')
    def _compute_xep_hang(self):
        # Lấy tất cả bản ghi trong bảng xếp hạng, sắp xếp theo tổng tiền chi tiêu giảm dần
        all_records = self.search([], order='tong_tien_chi_tieu desc')
        for rank, record in enumerate(all_records, 1):
            record.xep_hang = rank