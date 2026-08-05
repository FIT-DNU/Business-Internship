from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DanhGiaNhanVien(models.Model):
    _name = 'danh_gia_nhan_vien'
    _description = 'Đánh Giá Nhân Viên'
    
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân Viên', required=True, ondelete='cascade')
    cong_viec_id = fields.Many2one('cong_viec', string='Công Việc', ondelete='cascade')
    du_an_id = fields.Many2one('du_an', string='Dự Án', ondelete='cascade')
    diem_so = fields.Selection([(str(i), str(i)) for i in range(1, 11)], string='Điểm Số', required=True)
    nhan_xet = fields.Text(string='Nhận Xét')
    ngay_danh_gia = fields.Datetime(string='Ngày Đánh Giá', default=fields.Datetime.now, required=True)
    
    
    @api.onchange('cong_viec_id')
    def _onchange_cong_viec_id(self):
        if self.cong_viec_id:
            self.du_an_id = self.cong_viec_id.du_an_id
        else:
            self.du_an_id = False
    
    @api.constrains('diem_so')
    def _check_diem_so(self):
        for record in self:
            if not (1 <= int(record.diem_so) <= 10):
                raise ValidationError("Điểm số phải nằm trong khoảng từ 1 đến 10.")

    @api.model
    def create(self, vals):
        """Kiểm tra xem nhân viên có tham gia công việc hoặc dự án không trước khi đánh giá"""
        nhan_vien_id = vals.get('nhan_vien_id')
        cong_viec_id = vals.get('cong_viec_id')
        du_an_id = vals.get('du_an_id')
        
        if cong_viec_id:
            cong_viec = self.env['cong_viec'].browse(cong_viec_id)
            if nhan_vien_id not in cong_viec.nhan_vien_ids.ids:
                raise ValidationError("Nhân viên này không tham gia công việc đã chọn.")
        
        if du_an_id:
            du_an = self.env['du_an'].browse(du_an_id)
            if nhan_vien_id not in du_an.nhan_vien_ids.ids:
                raise ValidationError("Nhân viên này không tham gia dự án đã chọn.")
        
        return super(DanhGiaNhanVien, self).create(vals)
    
    @api.constrains('nhan_vien_id')
    def _check_nhan_vien_trong_du_an(self):
        for record in self:
            if record.du_an_id:
                nhan_vien_du_an_ids = record.du_an_id.nhan_vien_ids.ids
                if record.nhan_vien_id.id not in nhan_vien_du_an_ids:
                    raise ValidationError(f"Nhân viên {record.nhan_vien_id.display_name} không thuộc dự án này.")
