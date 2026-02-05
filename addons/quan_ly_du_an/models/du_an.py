# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Quản lý dự án'
    _rec_name = 'ten_du_an'
    _order = 'ngay_bat_dau desc'

    # Thông tin cơ bản
    ma_du_an = fields.Char("Mã dự án", required=True, help="Mã định danh duy nhất cho dự án")
    ten_du_an = fields.Char("Tên dự án", required=True)
    mo_ta = fields.Text("Mô tả dự án")
    
    # Thời gian
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, default=fields.Date.today)
    ngay_ket_thuc_du_kien = fields.Date("Ngày kết thúc dự kiến", required=True)
    ngay_ket_thuc_thuc_te = fields.Date("Ngày kết thúc thực tế")
    
    # Trạng thái
    trang_thai = fields.Selection(
        [
            ("planned", "Sắp bắt đầu"),
            ("in_progress", "Đang thực hiện"),
            ("on_hold", "Tạm dừng"),
            ("done", "Hoàn thành"),
            ("cancelled", "Hủy bỏ")
        ],
        string="Trạng thái",
        default="planned",
        required=True
    )
    
    # Trạng thái tương thích với quan_ly_cong_viec
    tien_do_du_an = fields.Selection(
        [
            ('chua_bat_dau', 'Chưa Bắt Đầu'),
            ('dang_thuc_hien', 'Đang Thực Hiện'),
            ('hoan_thanh', 'Hoàn Thành'),
            ('tam_dung', 'Tạm Dừng')
        ],
        string="Trạng Thái Dự Án (Tương thích)",
        compute="_compute_tien_do_du_an",
        store=True
    )
    
    # Quản lý
    nguoi_quan_ly_id = fields.Many2one("nhan_vien", string="Người quản lý dự án", required=True)
    nguoi_phu_trach_id = fields.Many2one("nhan_vien", string="Người phụ trách", help="Tương thích với quan_ly_cong_viec")
    khach_hang = fields.Char("Khách hàng/Đối tác")
    
    # Ngân sách
    ngan_sach_du_an = fields.Float("Ngân sách dự án", default=0.0, help="Tổng ngân sách dự án (VND)")
    ngan_sach_da_su_dung = fields.Float("Ngân sách đã sử dụng", compute="_compute_ngan_sach", store=True)
    ngan_sach_con_lai = fields.Float("Ngân sách còn lại", compute="_compute_ngan_sach", store=True)
    
    # Tiến độ (đơn giản, không phụ thuộc module công việc để tránh vòng lặp)
    tien_do = fields.Float("Tiến độ (%)", default=0.0, help="Tiến độ dự án (được module công việc mở rộng)")
    
    # Quan hệ với nhân viên (Many2many qua du_an_nhan_vien)
    nhan_vien_ids = fields.Many2many(
        "nhan_vien",
        "du_an_nhan_vien_rel",
        "du_an_id",
        "nhan_vien_id",
        string="Danh sách nhân viên tham gia"
    )
    du_an_nhan_vien_ids = fields.One2many(
        "du_an_nhan_vien",
        "du_an_id",
        string="Chi tiết thành viên dự án"
    )
    
    # Các trường về công việc sẽ được module quan_ly_cong_viec kế thừa để tránh phụ thuộc vòng
    
    # Ghi chú
    ghi_chu = fields.Text("Ghi chú")
    
    # Display name
    display_name = fields.Char("Tên hiển thị", compute="_compute_display_name", store=True)

    @api.depends("ten_du_an", "ma_du_an")
    def _compute_display_name(self):
        for record in self:
            if record.ten_du_an and record.ma_du_an:
                record.display_name = f"[{record.ma_du_an}] {record.ten_du_an}"
            elif record.ten_du_an:
                record.display_name = record.ten_du_an
            else:
                record.display_name = "Dự án"

    @api.depends("ngan_sach_du_an", "du_an_nhan_vien_ids")
    def _compute_ngan_sach(self):
        for record in self:
            # Tính ngân sách đã sử dụng từ chi phí nhân sự
            chi_phi_nhan_su = sum(record.du_an_nhan_vien_ids.mapped('chi_phi_du_kien')) if record.du_an_nhan_vien_ids else 0.0
            record.ngan_sach_da_su_dung = chi_phi_nhan_su
            record.ngan_sach_con_lai = record.ngan_sach_du_an - record.ngan_sach_da_su_dung

    @api.constrains('ngay_ket_thuc_du_kien', 'ngay_bat_dau')
    def _check_ngay(self):
        for record in self:
            if record.ngay_ket_thuc_du_kien and record.ngay_bat_dau:
                if record.ngay_ket_thuc_du_kien < record.ngay_bat_dau:
                    raise ValidationError("Ngày kết thúc dự kiến phải lớn hơn hoặc bằng ngày bắt đầu!")

    @api.constrains('ngan_sach_du_an')
    def _check_ngan_sach(self):
        for record in self:
            if record.ngan_sach_du_an < 0:
                raise ValidationError("Ngân sách dự án không được âm!")

    @api.depends("trang_thai")
    def _compute_tien_do_du_an(self):
        """
        Map trang_thai sang tien_do_du_an để tương thích với quan_ly_cong_viec
        Logic này sẽ được override trong module quan_ly_cong_viec để tính theo công việc
        """
        for record in self:
            mapping = {
                "planned": "chua_bat_dau",
                "in_progress": "dang_thuc_hien",
                "on_hold": "tam_dung",
                "done": "hoan_thanh",
                "cancelled": "tam_dung"
            }
            record.tien_do_du_an = mapping.get(record.trang_thai, "chua_bat_dau")

    @api.model
    def create(self, vals):
        """Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi tạo dự án"""
        nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id') or vals.get('nguoi_quan_ly_id')
        nguoi_quan_ly_id = vals.get('nguoi_quan_ly_id')
        
        # Đồng bộ nguoi_phu_trach_id và nguoi_quan_ly_id
        if nguoi_phu_trach_id and not nguoi_quan_ly_id:
            vals['nguoi_quan_ly_id'] = nguoi_phu_trach_id
        elif nguoi_quan_ly_id and not nguoi_phu_trach_id:
            vals['nguoi_phu_trach_id'] = nguoi_quan_ly_id
        
        # Đảm bảo người phụ trách/quản lý có trong danh sách nhân viên tham gia
        nhan_vien_ids = vals.get('nhan_vien_ids', [(6, 0, [])])
        nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids and len(nhan_vien_ids) > 0 and len(nhan_vien_ids[0]) > 2 else set()
        
        if nguoi_phu_trach_id:
            nhan_vien_list.add(nguoi_phu_trach_id)
            vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]
        
        return super(DuAn, self).create(vals)

    def write(self, vals):
        """Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi cập nhật dự án"""
        for record in self:
            nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id', record.nguoi_phu_trach_id.id if record.nguoi_phu_trach_id else False)
            nguoi_quan_ly_id = vals.get('nguoi_quan_ly_id', record.nguoi_quan_ly_id.id if record.nguoi_quan_ly_id else False)
            
            # Đồng bộ nguoi_phu_trach_id và nguoi_quan_ly_id
            if 'nguoi_phu_trach_id' in vals:
                if not vals.get('nguoi_quan_ly_id'):
                    vals['nguoi_quan_ly_id'] = vals['nguoi_phu_trach_id']
            elif 'nguoi_quan_ly_id' in vals:
                if not vals.get('nguoi_phu_trach_id'):
                    vals['nguoi_phu_trach_id'] = vals['nguoi_quan_ly_id']
            
            # Đảm bảo người phụ trách/quản lý có trong danh sách nhân viên tham gia
            nhan_vien_ids = vals.get('nhan_vien_ids', [(6, 0, record.nhan_vien_ids.ids)])
            nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids and len(nhan_vien_ids) > 0 and len(nhan_vien_ids[0]) > 2 else set(record.nhan_vien_ids.ids)
            
            final_nguoi_phu_trach = nguoi_phu_trach_id or nguoi_quan_ly_id
            if final_nguoi_phu_trach:
                nhan_vien_list.add(final_nguoi_phu_trach)
                vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]
        
        return super(DuAn, self).write(vals)

    _sql_constraints = [
        ('ma_du_an_unique', 'unique(ma_du_an)', 'Mã dự án phải là duy nhất')
    ]
