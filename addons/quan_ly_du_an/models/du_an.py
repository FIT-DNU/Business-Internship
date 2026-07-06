# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Dự Án'
    _rec_name = 'ten_du_an'

    # Thông tin cơ bản
    ma_du_an = fields.Char(string='Mã Dự Án', required=True)
    ten_du_an = fields.Char(string='Tên Dự Án', required=True)
    mo_ta = fields.Text(string='Mô Tả')
    
    # Người quản lý và nhân viên
    nguoi_phu_trach_id = fields.Many2one('nhan_vien', string='Người Phụ Trách', ondelete='set null')
    nhan_vien_ids = fields.Many2many('nhan_vien', 'du_an_nhan_vien_rel', 
                                     'du_an_id', 'nhan_vien_id', 
                                     string='Nhân Viên Tham Gia')

    # Thời gian
    ngay_bat_dau = fields.Date(string='Ngày Bắt Đầu', default=fields.Date.today)
    ngay_ket_thuc_du_kien = fields.Date(string='Ngày Kết Thúc Dự Kiến')
    ngay_ket_thuc_thuc_te = fields.Date(string='Ngày Kết Thúc Thực Tế')

    # Trạng thái và tiến độ
    tien_do_du_an = fields.Selection([
        ('chua_bat_dau', 'Chưa Bắt Đầu'),
        ('dang_thuc_hien', 'Đang Thực Hiện'),
        ('hoan_thanh', 'Hoàn Thành'),
        ('tam_dung', 'Tạm Dừng'),
        ('huy_bo', 'Hủy Bỏ')
    ], string="Trạng Thái Dự Án", default='chua_bat_dau')
    
    phan_tram_du_an = fields.Float(string="Tiến Độ Dự Án (%)", 
                                   compute="_compute_phan_tram_du_an", 
                                   store=True, default=0.0)
    
    ly_do_huy_bo = fields.Text(string="Lý do hủy bỏ", help="Lý do hủy bỏ dự án")

    # Quan hệ với các model khác
    # cong_viec_ids và danh_gia_nhan_vien_ids được thêm bởi module quan_ly_cong_viec
    tai_nguyen_ids = fields.One2many('tai_nguyen', 'du_an_id', string='Danh Sách Tài Nguyên')
    budget_ids = fields.One2many('budgets', 'du_an_id', string='Ngân Sách Dự Án')
    giai_doan_ids = fields.One2many('giai_doan_cong_viec', 'du_an_id', string='Giai Đoạn')

    _sql_constraints = [
        ('unique_ma_du_an', 'UNIQUE(ma_du_an)', 'Mã dự án đã tồn tại!')
    ]

    @api.depends('tien_do_du_an')
    def _compute_phan_tram_du_an(self):
        """Tính tiến độ dự án - sẽ được override bởi module quan_ly_cong_viec"""
        for record in self:
            # Nếu chưa có công việc, tính theo trạng thái
            if record.tien_do_du_an == 'chua_bat_dau':
                record.phan_tram_du_an = 0.0
            elif record.tien_do_du_an == 'dang_thuc_hien':
                # Sẽ được tính lại khi có công việc
                record.phan_tram_du_an = record.phan_tram_du_an or 0.0
            elif record.tien_do_du_an == 'hoan_thanh':
                record.phan_tram_du_an = 100.0
            else:
                record.phan_tram_du_an = record.phan_tram_du_an or 0.0

    @api.constrains('phan_tram_du_an', 'tien_do_du_an')
    def _check_phan_tram_du_an(self):
        """ Kiểm tra điều kiện hợp lệ cho phần trăm hoàn thành """
        for record in self:
            if record.tien_do_du_an == 'chua_bat_dau' and record.phan_tram_du_an != 0:
                raise ValidationError("Tiến độ dự án phải là 0% khi dự án ở trạng thái 'Chưa Bắt Đầu'.")
            if record.phan_tram_du_an < 0 or record.phan_tram_du_an > 100:
                raise ValidationError("Tiến độ dự án phải nằm trong khoảng từ 0% đến 100%.")

    @api.model
    def create(self, vals):
        """ Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi tạo dự án """
        nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id')
        nhan_vien_ids = vals.get('nhan_vien_ids', [(6, 0, [])])

        if nguoi_phu_trach_id:
            nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids and len(nhan_vien_ids[0]) > 2 else set()
            nhan_vien_list.add(nguoi_phu_trach_id)
            vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]

        return super(DuAn, self).create(vals)

    def write(self, vals):
        """ Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi cập nhật dự án """
        for record in self:
            nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id', record.nguoi_phu_trach_id.id if record.nguoi_phu_trach_id else False)
            nhan_vien_ids = vals.get('nhan_vien_ids', False)

            if nguoi_phu_trach_id:
                if nhan_vien_ids:
                    nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids and len(nhan_vien_ids[0]) > 2 else set()
                else:
                    nhan_vien_list = set(record.nhan_vien_ids.ids)
                nhan_vien_list.add(nguoi_phu_trach_id)
                vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]

        return super(DuAn, self).write(vals)


