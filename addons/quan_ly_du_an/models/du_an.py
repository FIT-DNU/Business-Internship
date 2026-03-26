from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class DuAn(models.Model):
    _name = 'quan_ly.du_an'
    _description = 'Thông tin dự án'

    name = fields.Char("Tên dự án", required=True)
    ngay_bat_dau = fields.Date("Ngày bắt đầu")
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
    ngan_sach = fields.Float("Ngân sách (VNĐ)")
    
    manager_id = fields.Many2one('nhan_vien', string="Chủ nhiệm dự án")
    task_ids = fields.One2many('quan_ly.cong_viec', 'project_id', string="Danh sách công việc")

    tien_do_tong_the = fields.Float(
        string="Tiến độ tổng thể (%)", 
        compute="_compute_progress", 
        store=True
    )

    muc_do_uu_tien_logic = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Trung bình'),
        ('2', 'Cao'),
        ('3', 'Rất khẩn cấp')
    ], string="Xếp hạng ưu tiên", compute="_compute_priority", store=True)

    # Các trường phục vụ hiển thị trực quan
    is_high_value = fields.Boolean(compute="_compute_visual_flags")
    is_urgent = fields.Boolean(compute="_compute_visual_flags")

    @api.depends('task_ids.tien_do')
    def _compute_progress(self):
        for record in self:
            if record.task_ids:
                tong_tien_do = sum(task.tien_do for task in record.task_ids)
                record.tien_do_tong_the = tong_tien_do / len(record.task_ids)
            else:
                record.tien_do_tong_the = 0.0

    @api.depends('ngan_sach', 'ngay_ket_thuc')
    def _compute_priority(self):
        for record in self:
            # Mặc định mức độ ưu tiên là '0' (Thấp)
            priority = '0'
            
            # 1. Ưu tiên theo ngân sách: Dự án lớn thì bét nhất cũng phải là '2' (Cao)
            if record.ngan_sach > 500000000:
                priority = '2'
                
            # 2. Ưu tiên theo thời gian: Thời gian sẽ ghi đè lên ngân sách
            if record.ngay_ket_thuc:
                days_left = (record.ngay_ket_thuc - date.today()).days
                
                if days_left <= 3:
                    # Gần đến hạn hoặc quá hạn -> Rất khẩn cấp (Mức 3)
                    priority = '3'
                elif days_left <= 7 and priority == '0':
                    # Còn dưới 1 tuần nhưng không phải dự án lớn -> Trung bình (Mức 1)
                    priority = '1'
            
            # Cập nhật giá trị cho trường dữ liệu
            record.muc_do_uu_tien_logic = priority

    @api.depends('ngan_sach', 'ngay_ket_thuc')
    def _compute_visual_flags(self):
        for record in self:
            record.is_high_value = record.ngan_sach >= 500000000
            record.is_urgent = False
            if record.ngay_ket_thuc:
                days_left = (record.ngay_ket_thuc - date.today()).days
                record.is_urgent = 0 <= days_left <= 3
    
    @api.constrains('manager_id', 'ngan_sach')
    def _check_manager_position(self):
        for record in self:
            if not record.manager_id:
                continue
            
            # Lấy chức vụ và chuyển về chữ thường để so sánh không phân biệt hoa thường
            chuc_vu = (record.manager_id.chuc_vu or "").lower()
            
            if record.ngan_sach > 500000000:
                # Dự án trên 500tr: Chỉ Trưởng phòng
                if "trưởng phòng" not in chuc_vu:
                    raise ValidationError(
                        "LỖI NGHIỆP VỤ: Dự án lớn (trên 500 triệu) bắt buộc phải do Trưởng phòng quản lý!"
                    )
            else:
                # Dự án dưới 500tr: Trưởng phòng hoặc Trưởng nhóm
                if "trưởng phòng" not in chuc_vu and "trưởng nhóm" not in chuc_vu:
                    raise ValidationError(
                        "LỖI NGHIỆP VỤ: Dự án phải do Trưởng phòng hoặc Trưởng nhóm quản lý. "
                        "Nhân viên bình thường không được nhận làm quản lý dự án!"
                    )