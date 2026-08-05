# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DuAnNhanVien(models.Model):
    _name = 'du_an_nhan_vien'
    _description = 'Thành viên dự án'
    _rec_name = 'display_name'
    _order = 'ngay_tham_gia desc'

    du_an_id = fields.Many2one("du_an", string="Dự án", required=True, ondelete='cascade')
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True, ondelete='cascade')
    
    vai_tro = fields.Selection(
        [
            ("project_manager", "Trưởng dự án"),
            ("member", "Thành viên"),
            ("advisor", "Cố vấn"),
            ("observer", "Quan sát viên")
        ],
        string="Vai trò",
        default="member",
        required=True
    )
    
    ty_le_tham_gia = fields.Float("Tỷ lệ tham gia (%)", default=100.0, help="Tỷ lệ thời gian tham gia dự án (0-100%)")
    luong_du_an = fields.Float("Lương dự án", help="Lương dự án/giờ (VND). Nếu để trống sẽ dùng lương cơ bản")
    
    ngay_tham_gia = fields.Date("Ngày tham gia", required=True, default=fields.Date.today)
    ngay_roi = fields.Date("Ngày rời dự án")
    
    chi_phi_du_kien = fields.Float("Chi phí dự kiến", compute="_compute_chi_phi", store=True)
    
    ghi_chu = fields.Text("Ghi chú về vai trò và trách nhiệm")
    
    display_name = fields.Char("Tên hiển thị", compute="_compute_display_name", store=True)

    @api.depends("nhan_vien_id", "du_an_id", "vai_tro")
    def _compute_display_name(self):
        for record in self:
            if record.nhan_vien_id and record.du_an_id:
                vai_tro_dict = dict(record._fields['vai_tro'].selection)
                vai_tro_name = vai_tro_dict.get(record.vai_tro, record.vai_tro)
                record.display_name = f"{record.nhan_vien_id.ho_va_ten} - {record.du_an_id.ten_du_an} ({vai_tro_name})"
            else:
                record.display_name = "Thành viên dự án"

    @api.depends("nhan_vien_id", "luong_du_an", "ty_le_tham_gia")
    def _compute_chi_phi(self):
        for record in self:
            # Tính chi phí dự kiến dựa trên lương dự án và tỷ lệ tham gia
            if record.luong_du_an and record.ty_le_tham_gia:
                # Giả sử làm việc 8 giờ/ngày, 22 ngày/tháng
                # Chi phí = lương/giờ × 8 giờ × 22 ngày × (tỷ lệ tham gia/100)
                record.chi_phi_du_kien = record.luong_du_an * 8 * 22 * (record.ty_le_tham_gia / 100)
            else:
                record.chi_phi_du_kien = 0.0

    @api.constrains('ty_le_tham_gia')
    def _check_ty_le_tham_gia(self):
        for record in self:
            if record.ty_le_tham_gia < 0 or record.ty_le_tham_gia > 100:
                raise ValidationError("Tỷ lệ tham gia phải trong khoảng 0-100%!")

    @api.constrains('ngay_roi', 'ngay_tham_gia')
    def _check_ngay_roi(self):
        for record in self:
            if record.ngay_roi and record.ngay_tham_gia:
                if record.ngay_roi < record.ngay_tham_gia:
                    raise ValidationError("Ngày rời dự án phải lớn hơn hoặc bằng ngày tham gia!")

    _sql_constraints = [
        ('du_an_nhan_vien_unique', 'unique(du_an_id, nhan_vien_id)', 'Nhân viên không thể tham gia cùng một dự án nhiều lần!')
    ]
