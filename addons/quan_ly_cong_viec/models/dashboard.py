from odoo import models, fields, api

class Dashboard(models.Model):
    _name = 'dashboard'
    _description = 'Thống Kê Tổng Quan'
    
    so_luong_nhan_vien = fields.Integer(string="Số lượng nhân viên", compute="_compute_tong_quan", store=True)
    so_luong_du_an = fields.Integer(string="Số lượng dự án", compute="_compute_tong_quan", store=True)
    so_luong_cong_viec = fields.Integer(string="Số lượng công việc", compute="_compute_tong_quan", store=True)
    phan_tram_hoan_thanh = fields.Float(string="Tiến độ trung bình dự án (%)", compute="_compute_tong_quan", store=True)
    so_luong_danh_gia = fields.Integer(string="Số lượng danh gia", compute="_compute_tong_quan", store=True)
    
    du_an_hoan_thanh = fields.Integer(string="Dự án đã hoàn thành", compute="_compute_tong_quan", store=True)
    du_an_dang_thuc_hien = fields.Integer(string="Dự án đang thực hiện", compute="_compute_tong_quan", store=True)
    du_an_chua_bat_dau = fields.Integer(string="Dự án chưa bắt đầu", compute="_compute_tong_quan", store=True)
    du_an_tam_dung = fields.Integer(string="Dự án tạm dừng", compute="_compute_tong_quan", store=True)
    

    
    @api.depends('so_luong_nhan_vien', 'so_luong_du_an', 'so_luong_cong_viec', 'du_an_hoan_thanh', 'du_an_dang_thuc_hien',
                 'du_an_chua_bat_dau','du_an_tam_dung')
    def _compute_tong_quan(self):
        for record in self:
            record.so_luong_nhan_vien = self.env['nhan_vien'].search_count([])
            record.so_luong_du_an = self.env['du_an'].search_count([])
            record.so_luong_cong_viec = self.env['cong_viec'].search_count([])
            record.so_luong_danh_gia = self.env['danh_gia_nhan_vien'].search_count([])
            

            du_an_records = self.env['du_an'].search([])
            record.du_an_hoan_thanh = sum(1 for d in du_an_records if d.tien_do_du_an == 'hoan_thanh')
            record.du_an_dang_thuc_hien = sum(1 for d in du_an_records if d.tien_do_du_an == 'dang_thuc_hien')
            record.du_an_chua_bat_dau = sum(1 for d in du_an_records if d.tien_do_du_an == 'chua_bat_dau')
            record.du_an_tam_dung = sum(1 for d in du_an_records if d.tien_do_du_an == 'tam_dung')
