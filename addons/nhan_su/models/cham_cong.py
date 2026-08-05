from odoo import models, fields, api

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Chấm công'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    thang = fields.Integer("Tháng", required=True)
    nam = fields.Integer("Năm", required=True)
    so_ngay_cong = fields.Float("Số ngày công", default=0)
    tang_ca = fields.Float("Giờ tăng ca", default=0)

    tong_luong = fields.Float(
        "Tổng lương", compute="_compute_luong", store=True
    )

    @api.depends('so_ngay_cong', 'tang_ca', 'nhan_vien_id.luong', 'nhan_vien_id.chuc_vu_id.phu_cap')
    def _compute_luong(self):
        for rec in self:
            luong_cb = rec.nhan_vien_id.luong or 0
            phu_cap = rec.nhan_vien_id.chuc_vu_id.phu_cap or 0
            luong_ngay = luong_cb / 26 if luong_cb else 0
            rec.tong_luong = rec.so_ngay_cong * luong_ngay + rec.tang_ca * 50000 + phu_cap