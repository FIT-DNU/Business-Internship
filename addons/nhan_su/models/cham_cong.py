from odoo import models, fields, api
from datetime import datetime, timedelta


class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Bảng chấm công'
    _rec_name = 'ngay_cham_cong'
    _order = 'ngay_cham_cong desc'

    ngay_cham_cong = fields.Date("Ngày chấm công", required=True, default=fields.Date.today)
    gio_cham_cong = fields.Float("Giờ chấm công", help="Giờ chấm công cụ thể (ví dụ: 8.533 = 8h32). Dùng để xác định muộn hay đúng giờ")
    gio_vao = fields.Float("Giờ vào", required=True, default=8.5, help="Giờ vào làm việc (8.5 = 8h30)")
    gio_ra = fields.Float("Giờ ra", required=True, default=17.5, help="Giờ ra làm việc (17.5 = 17h30)")
    gio_nghi_bat_dau = fields.Float("Giờ nghỉ bắt đầu", default=12.5, help="Giờ bắt đầu nghỉ trưa (ví dụ: 12.5 = 12h30)")
    gio_nghi_ket_thuc = fields.Float("Giờ nghỉ kết thúc", default=13.5, help="Giờ kết thúc nghỉ trưa (ví dụ: 13.5 = 13h30)")
    so_gio_lam = fields.Float("Số giờ làm", compute="_compute_so_gio_lam", store=True, 
                               help="Số giờ làm = giờ ra - giờ chấm công - giờ nghỉ")
    trang_thai = fields.Selection(
        [
            ("vang", "Vắng"),
            ("dung_gio", "Đúng giờ"),
            ("muon", "Muộn"),
            ("vi_pham", "Vi phạm")
        ],
        string="Trạng thái",
        compute="_compute_trang_thai",
        store=True,
        help="Trạng thái tự động tính toán dựa trên giờ vào và giờ ra"
    )
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên", required=True, ondelete='cascade')
    ghi_chu = fields.Text("Ghi chú")

    @api.depends("gio_cham_cong", "gio_ra", "gio_nghi_bat_dau", "gio_nghi_ket_thuc")
    def _compute_so_gio_lam(self):
        for record in self:
            if record.gio_cham_cong and record.gio_ra:
                # Tính số giờ làm = giờ ra - giờ chấm công - (giờ nghỉ kết thúc - giờ nghỉ bắt đầu)
                gio_nghi = record.gio_nghi_ket_thuc - record.gio_nghi_bat_dau
                record.so_gio_lam = record.gio_ra - record.gio_cham_cong - gio_nghi
                if record.so_gio_lam < 0:
                    record.so_gio_lam = 0
            else:
                record.so_gio_lam = 0

    @api.depends("gio_cham_cong", "gio_vao", "gio_ra")
    def _compute_trang_thai(self):
        for record in self:
            # Giờ chuẩn: vào 8:30 (8.5), ra 17:30 (17.5)
            gio_vao_chuan = 8.5
            gio_ra_chuan = 17.5
            
            # Nếu không có giờ vào hoặc giờ ra -> Vắng
            if not record.gio_vao or not record.gio_ra:
                record.trang_thai = "vang"
            # Nếu không có giờ chấm công -> Vắng
            elif not record.gio_cham_cong:
                record.trang_thai = "vang"
            # Nếu giờ ra < 17:30 -> Vi phạm (về sớm) - ưu tiên kiểm tra trước
            elif record.gio_ra < gio_ra_chuan:
                record.trang_thai = "vi_pham"
            # Nếu giờ chấm công > 8:30 -> Muộn
            elif record.gio_cham_cong > gio_vao_chuan:
                record.trang_thai = "muon"
            # Nếu giờ chấm công <= 8:30 và giờ ra >= 17:30 -> Đúng giờ
            else:
                record.trang_thai = "dung_gio"

    @api.constrains('gio_vao', 'gio_ra', 'gio_nghi_bat_dau', 'gio_nghi_ket_thuc')
    def _check_gio(self):
        for record in self:
            if record.gio_ra <= record.gio_vao:
                raise models.ValidationError("Giờ ra phải lớn hơn giờ vào!")
            if record.gio_nghi_ket_thuc <= record.gio_nghi_bat_dau:
                raise models.ValidationError("Giờ nghỉ kết thúc phải lớn hơn giờ nghỉ bắt đầu!")
            if record.gio_nghi_bat_dau < record.gio_vao or record.gio_nghi_ket_thuc > record.gio_ra:
                raise models.ValidationError("Thời gian nghỉ phải nằm trong khoảng giờ làm việc!")
