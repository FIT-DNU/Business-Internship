from odoo import models, fields , api

class GiaiDoanCongViec(models.Model):
    _name = 'giai_doan_cong_viec'
    _description = 'Giai Đoạn Công Việc'
    _rec_name = 'ten_giai_doan'

    ten_giai_doan = fields.Char(string='Tên Giai Đoạn', required=True)
    thu_tu = fields.Integer(string='Thứ Tự')
    
    du_an_id = fields.Many2one('du_an', string='Dự Án', ondelete='cascade')


    # trang_thai = fields.Selection([
    #     ('chua_hoan_thanh', 'Chưa Hoàn Thành'),
    #     ('hoan_thanh', 'Hoàn Thành')
    # ], string='Trạng Thái', default='chua_hoan_thanh')

    # cong_viec_ids = fields.One2many('cong_viec', 'giai_doan_id', string='Công Việc Trong Giai Đoạn')

    # @api.depends('cong_viec_ids.trang_thai')
    # def _compute_trang_thai(self):
    #     for record in self:
    #         if all(cv.trang_thai == 'hoan_thanh' for cv in record.cong_viec_ids):
    #             record.trang_thai = 'hoan_thanh'
    #         else:
    #             record.trang_thai = 'chua_hoan_thanh'