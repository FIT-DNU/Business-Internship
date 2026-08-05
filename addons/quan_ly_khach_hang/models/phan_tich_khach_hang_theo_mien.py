from odoo import models, fields, api

class PhanTichKhachHang(models.Model):
    _name = 'phan_tich_khach_hang_theo_mien'
    _description = 'Phân Tích Khách Hàng Theo Miền'

    vung_mien = fields.Selection(
        [('bac', 'Miền Bắc'), ('trung', 'Miền Trung'), ('nam', 'Miền Nam')],
        string="Vùng miền",
        required=True
    )
    so_luong_khach = fields.Integer("Số lượng khách hàng", compute="_compute_so_luong_khach", store=True)
    tong_doanh_thu = fields.Float("Tổng doanh thu", compute="_compute_tong_doanh_thu", store=True)

    @api.depends('vung_mien')
    def _compute_tong_doanh_thu(self):
        for record in self:
            khach_hang_data = self.env['thong_tin_khach_hang'].read_group(
                [('vung_mien', '=', record.vung_mien)],
                ['tong_tien_chi_tieu:sum'],
                []
            )
            record.tong_doanh_thu = khach_hang_data[0]['tong_tien_chi_tieu'] if khach_hang_data else 0

    @api.depends('vung_mien')
    def _compute_so_luong_khach(self):
        for record in self:
            record.so_luong_khach = self.env['thong_tin_khach_hang'].search_count([('vung_mien', '=', record.vung_mien)])

    def cap_nhat_du_lieu_phan_tich(self):
        """ Cập nhật dữ liệu khi khách hàng thay đổi """
        dashboard = self.env['dashboard'].search([], limit=1)

        # Nếu chưa có, tạo một bản ghi dashboard mới
        if not dashboard:
            dashboard = self.env['dashboard'].create({})

        for vung in ['bac', 'trung', 'nam']:
            phan_tich = self.env['phan_tich_khach_hang_theo_mien'].search([('vung_mien', '=', vung)], limit=1)

            if not phan_tich:
                phan_tich = self.env['phan_tich_khach_hang_theo_mien'].create({'vung_mien': vung})

            # Tính toán lại dữ liệu
            phan_tich._compute_so_luong_khach()
            phan_tich._compute_tong_doanh_thu()

            # Cập nhật giá trị vào dashboard
            dashboard.write({
                f"so_luong_khach_{vung}": phan_tich.so_luong_khach,
                f"tong_chi_tieu_{vung}": phan_tich.tong_doanh_thu
            })

