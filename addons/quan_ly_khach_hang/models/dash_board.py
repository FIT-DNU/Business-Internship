from odoo import models, fields, api


class Dashboard(models.Model):
    _name = 'dashboard'
    _description = 'Dashboard Tổng Quan'

    # Các trường thống kê
    tong_so_khach = fields.Integer("Tổng số khách hàng", compute="_compute_dashboard", store=False)
    tong_doanh_thu = fields.Float("Tổng doanh thu", compute="_compute_dashboard", store=False)

    # Số lượng khách hàng theo miền
    so_luong_khach_bac = fields.Integer("Số lượng khách miền Bắc", compute="_compute_dashboard", store=True)
    so_luong_khach_trung = fields.Integer("Số lượng khách miền Trung", compute="_compute_dashboard", store=True)
    so_luong_khach_nam = fields.Integer("Số lượng khách miền Nam", compute="_compute_dashboard", store=True)

    # Tổng chi tiêu theo miền
    tong_chi_tieu_bac = fields.Float("Tổng chi tiêu miền Bắc", compute="_compute_dashboard", store=True)
    tong_chi_tieu_trung = fields.Float("Tổng chi tiêu miền Trung", compute="_compute_dashboard", store=True)
    tong_chi_tieu_nam = fields.Float("Tổng chi tiêu miền Nam", compute="_compute_dashboard", store=True)

    bang_xep_hang = fields.One2many('bang_xep_hang_khach_hang', 'khach_hang_id', string="Bảng xếp hạng khách hàng",
                                    compute="_compute_dashboard")


    @api.depends()
    def _compute_dashboard(self):
        data = self.env['phan_tich_khach_hang_theo_mien'].search([])

        # Tính tổng số khách & doanh thu
        self.tong_so_khach = sum(data.mapped('so_luong_khach'))
        self.tong_doanh_thu = sum(data.mapped('tong_doanh_thu'))

        # Tạo dictionary từ dữ liệu
        grouped_data = {x.vung_mien: x for x in data}

        self.so_luong_khach_bac = grouped_data['bac'].so_luong_khach if 'bac' in grouped_data else 0
        self.so_luong_khach_trung = grouped_data['trung'].so_luong_khach if 'trung' in grouped_data else 0
        self.so_luong_khach_nam = grouped_data['nam'].so_luong_khach if 'nam' in grouped_data else 0

        self.tong_chi_tieu_bac = grouped_data['bac'].tong_doanh_thu if 'bac' in grouped_data else 0
        self.tong_chi_tieu_trung = grouped_data['trung'].tong_doanh_thu if 'trung' in grouped_data else 0
        self.tong_chi_tieu_nam = grouped_data['nam'].tong_doanh_thu if 'nam' in grouped_data else 0

        self.bang_xep_hang = self.env['bang_xep_hang_khach_hang'].search([], order='xep_hang asc')
