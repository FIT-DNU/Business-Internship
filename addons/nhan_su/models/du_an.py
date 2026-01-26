from odoo import models, fields, api

class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Quản lý dự án'

    name = fields.Char("Tên dự án", required=True)
    nguoi_quan_tri_id = fields.Many2one('nhan_vien', string="Người quản trị") # Kết nối với nhân sự
    ngay_bat_dau = fields.Date("Ngày bắt đầu")
    ngay_ket_thuc = fields.Date("Ngày kết thúc dự kiến")
    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string="Danh sách công việc")
    tien_do = fields.Float("Tiến độ tổng thể (%)", compute="_compute_tien_do", store=True)

    @api.depends('cong_viec_ids.trang_thai')
    def _compute_tien_do(self):
        for record in self:
            if record.cong_viec_ids:
                hoan_thanh = len(record.cong_viec_ids.filtered(lambda x: x.trang_thai == 'done'))
                record.tien_do = (hoan_thanh / len(record.cong_viec_ids)) * 100
            else:
                record.tien_do = 0