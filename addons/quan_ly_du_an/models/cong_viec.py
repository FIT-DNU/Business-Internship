from odoo import models, fields, api
from datetime import date

class CongViec(models.Model):
    _name = 'quan_ly.cong_viec'
    _description = 'Chi tiết công việc'

    name = fields.Char("Tên đầu việc", required=True)
    project_id = fields.Many2one('quan_ly.du_an', string="Thuộc dự án", ondelete='cascade')
    nguoi_thuc_hien_id = fields.Many2one('nhan_vien', string="Người thực hiện")
    
    deadline = fields.Date("Hạn chót")
    tien_do = fields.Float("Tiến độ (%)", default=0.0)
    trang_thai = fields.Selection([
        ('moi', 'Mới'),
        ('dang_lam', 'Đang thực hiện'),
        ('xong', 'Hoàn thành')
    ], string="Trạng thái", default='moi')

    is_overdue = fields.Boolean(compute="_compute_overdue")

    @api.depends('deadline', 'trang_thai')
    def _compute_overdue(self):
        for record in self:
            if record.deadline and record.trang_thai != 'xong':
                record.is_overdue = record.deadline < date.today()
            else:
                record.is_overdue = False