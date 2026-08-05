from odoo import models, fields, api
from datetime import timedelta

from odoo.exceptions import ValidationError


class HoTroKhachHang(models.Model):
    _name = 'ho_tro_khach_hang'
    _description = 'Hỗ trợ khách hàng'
    _rec_name = 'ten_khach_hang'

    # Thông tin khách hàng
    ten_khach_hang = fields.Many2one(
        'thong_tin_khach_hang', string="Khách hàng", required=True
    )

    phuong_thuc_lien_lac = fields.Selection([
        ('call', 'Gọi điện'),
        ('email', 'Email'),
        ('chat', 'Nhắn tin'),
        ('direct', 'Gặp trực tiếp')
    ], string="Phương thức liên lạc", required=True)

    # Thời gian hỗ trợ
    thoi_gian_bat_dau = fields.Datetime(string="Thời gian bắt đầu", required=True)
    thoi_gian_ket_thuc = fields.Datetime(string="Thời gian kết thúc")

    ngay_ho_tro = fields.Integer(
        string="Số ngày hỗ trợ",
        compute="_compute_ngay_ho_tro",
        store=True
    )

    @api.depends('thoi_gian_bat_dau', 'thoi_gian_ket_thuc')
    def _compute_ngay_ho_tro(self):
        for record in self:
            if record.thoi_gian_bat_dau and record.thoi_gian_ket_thuc:
                delta = record.thoi_gian_ket_thuc - record.thoi_gian_bat_dau
                record.ngay_ho_tro = delta.total_seconds() / 86400.0  # Chia cho số giây trong 1 ngày
            else:
                record.ngay_ho_tro = 0

    # Yêu cầu & mô tả
    yeu_cau_cua_khach = fields.Text(string="Yêu cầu của khách hàng")
    mo_ta_chi_tiet = fields.Text(string="Mô tả chi tiết")

    # Trạng thái xử lý
    trang_thai = fields.Selection([
        ('pending', 'Đang chờ'),
        ('in_progress', 'Đang xử lý'),
        ('resolved', 'Đã giải quyết')
    ], string="Trạng thái", default='pending')

    nhan_vien_phu_trach = fields.Many2one(
        'nhan_vien',  # Model liên kết
        string="Nhân viên phụ trách",
        required=True
    )

    # Phản hồi & đánh giá từ khách hàng
    phan_hoi_khach_hang = fields.Text(string="Phản hồi của khách hàng")
    diem_danh_gia = fields.Integer(string="Điểm đánh giá từ khách hàng", default=0)

    # File đính kèm
    file_dinh_kem = fields.Many2many(
        'ir.attachment',
        'ho_tro_khach_hang_attachment_rel',
        'ho_tro_khach_hang_id',
        'attachment_id',
        string="File đính kèm"
    )

    # Ràng buộc dữ liệu: Điểm đánh giá phải từ 0 đến 5
    _sql_constraints = [
        ('check_diem_danh_gia', 'CHECK(diem_danh_gia BETWEEN 0 AND 5)',
         'Điểm đánh giá phải từ 0 đến 5!')
    ]

    @api.constrains('trang_thai', 'thoi_gian_ket_thuc', 'diem_danh_gia')
    def _check_thoi_gian_va_diem_danh_gia(self):
        for record in self:
            if record.trang_thai != 'resolved' and (record.thoi_gian_ket_thuc or record.diem_danh_gia):
                raise ValidationError(
                    "Chỉ được nhập thời gian kết thúc và điểm đánh giá khi trạng thái là 'Đã giải quyết'!")

    @api.model
    def create(self, vals):
        record = super(HoTroKhachHang, self).create(vals)
        # Cập nhật thống kê sau khi tạo bản ghi mới
        self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke()
        return record

    def write(self, vals):
        result = super(HoTroKhachHang, self).write(vals)
        if 'nhan_vien_phu_trach' in vals:
            self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke(self)
        return result

    def unlink(self):
        nhan_vien_ids = self.mapped('nhan_vien_phu_trach').ids
        result = super(HoTroKhachHang, self).unlink()
        if nhan_vien_ids:
            self.env['thong_ke_ho_tro_nhan_vien'].update_thong_ke(nhan_vien_ids)
        return result
