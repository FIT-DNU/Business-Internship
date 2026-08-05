from odoo import models, fields

class LichSuCongTac(models.Model):
    _name = 'lich_su_cong_tac'
    _description = 'Lịch sử công tác'

    nhan_vien_id = fields.Many2one(
        'nhan_vien', string="Nhân viên", required=True, ondelete='cascade'
    )
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    tu_ngay = fields.Date("Từ ngày")
    den_ngay = fields.Date("Đến ngày")
    ghi_chu = fields.Text("Ghi chú")