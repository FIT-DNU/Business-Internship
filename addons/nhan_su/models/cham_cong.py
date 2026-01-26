from odoo import models, fields, api
from datetime import timedelta

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Bảng chấm công nhân viên'
    _order = 'ngay_cham_cong desc'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    ngay_cham_cong = fields.Date(string="Ngày", default=fields.Date.context_today, required=True)
    
    gio_vao = fields.Datetime(string="Giờ vào", required=True)
    gio_ra = fields.Datetime(string="Giờ ra", required=True)
    
    tong_gio = fields.Float(string="Tổng giờ làm", compute="_compute_thong_tin_cham_cong", store=True)
    so_gio_ot = fields.Float(string="Số giờ OT", compute="_compute_thong_tin_cham_cong", store=True)
    tien_ot = fields.Float(string="Tiền OT (VNĐ)", compute="_compute_thong_tin_cham_cong", store=True)
    trang_thai = fields.Selection([
        ('binh_thuong', 'Bình thường'),
        ('ve_som', 'Về sớm/Thiếu giờ (Phạt)')
    ], string="Trạng thái", compute="_compute_thong_tin_cham_cong", store=True)

    @api.depends('gio_vao', 'gio_ra')
    def _compute_thong_tin_cham_cong(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                # Tính tổng thời gian (hiệu của gio_ra và gio_vao trả về timedelta)
                diff = record.gio_ra - record.gio_vao
                total_hours = diff.total_seconds() / 3600.0
                record.tong_gio = total_hours
                
                # Kiểm tra trạng thái làm việc (dưới 8 tiếng là về sớm/thiếu giờ)
                if total_hours < 8:
                    record.trang_thai = 've_som'
                    record.so_gio_ot = 0
                    record.tien_ot = 0
                else:
                    record.trang_thai = 'binh_thuong'
                    # Tính giờ OT (giờ thừa ra so với 8 tiếng)
                    ot = total_hours - 8
                    record.so_gio_ot = ot
                    
                    # Tính tiền OT theo các mức (ưu tiên mức cao nhất trước)
                    if ot >= 3:
                        record.tien_ot = 800000
                    elif ot >= 2:
                        record.tien_ot = 450000
                    elif ot >= 1:
                        record.tien_ot = 200000
                    else:
                        record.tien_ot = 0
            else:
                record.tong_gio = 0
                record.so_gio_ot = 0
                record.tien_ot = 0
                record.trang_thai = 'binh_thuong'