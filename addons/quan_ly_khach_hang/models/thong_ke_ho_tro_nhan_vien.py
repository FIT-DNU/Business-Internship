from odoo import models, fields, api

class ThongKeHoTroNhanVien(models.Model):
    _name = 'thong_ke_ho_tro_nhan_vien'
    _description = 'Thống kê hỗ trợ nhân viên'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True)
    so_lan_ho_tro = fields.Integer(string="Số lần hỗ trợ", default=0)
    ho_tro_ids = fields.Many2many('ho_tro_khach_hang', string="Danh sách hỗ trợ")

    @api.model
    def update_thong_ke(self, nhan_vien_id=None):
        """
        Cập nhật thống kê cho một nhân viên hoặc tất cả nhân viên.
        """
        domain = [('nhan_vien_phu_trach', '!=', False)]
        if nhan_vien_id:
            domain.append(('nhan_vien_phu_trach', '=', nhan_vien_id))

        # Nhóm dữ liệu theo nhân viên
        ho_tro_data = self.env['ho_tro_khach_hang'].read_group(
            domain,
            ['nhan_vien_phu_trach'],
            ['nhan_vien_phu_trach']
        )

        for data in ho_tro_data:
            nhan_vien = data['nhan_vien_phu_trach'][0]  # Lấy ID nhân viên
            so_lan_ho_tro = data['nhan_vien_phu_trach_count']
            ho_tro_records = self.env['ho_tro_khach_hang'].search([('nhan_vien_phu_trach', '=', nhan_vien)])

            # Kiểm tra xem đã có thống kê chưa
            thong_ke = self.search([('nhan_vien_id', '=', nhan_vien)], limit=1)
            if thong_ke:
                # Cập nhật dữ liệu
                thong_ke.write({
                    'so_lan_ho_tro': so_lan_ho_tro,
                    'ho_tro_ids': [(6, 0, ho_tro_records.ids)]
                })
            else:
                # Tạo mới nếu chưa có
                self.create({
                    'nhan_vien_id': nhan_vien,
                    'so_lan_ho_tro': so_lan_ho_tro,
                    'ho_tro_ids': [(6, 0, ho_tro_records.ids)]
                })

    def action_update_thong_ke(self):
        """
        Nút trên giao diện để cập nhật thống kê.
        """
        self.update_thong_ke()
