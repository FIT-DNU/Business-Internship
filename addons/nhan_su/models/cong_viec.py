from odoo import models, fields, api

class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Danh sách tác vụ'

    name = fields.Char("Tên công việc", required=True)
    du_an_id = fields.Many2one('du_an', string="Thuộc dự án")
    nguoi_thuc_hien_id = fields.Many2one('nhan_vien', string="Người thực hiện") 
    thoi_han = fields.Date("Hạn chót")
    trang_thai = fields.Selection([
        ('todo', 'Chưa làm'),
        ('doing', 'Đang làm'),
        ('done', 'Hoàn thành')
    ], string="Trạng thái", default='todo')