from odoo import models, fields, api

class ChiTietDonHang(models.Model):
    _name = 'chi_tiet_don_hang'
    _description = 'Chi tiết đơn hàng'
    _rec_name = 'order_id'

    order_id = fields.Char(string='Đơn hàng', required=True, copy=False, readonly=True,
                           default=lambda self: self.env['ir.sequence'].next_by_code('chi_tiet_don_hang'))

    ngay_dat_hang = fields.Date("Ngày đặt hàng", default=fields.Date.today)

    product_id = fields.Many2one('chi_tiet_san_pham', string='Tên sản phẩm', required=True)
    
    price_unit = fields.Float(string='Đơn giá', related='product_id.price_unit', store=True, readonly=True)
    
    quantity = fields.Integer(string='Số lượng', required=True, default=1)
    
    subtotal = fields.Float(string='Thành tiền', compute='_compute_subtotal', store=True)

    trang_thai = fields.Selection([
        ('moi', "Mới"),
        ('dang_xu_ly', "Đang xử lý"),
        ('hoan_thanh', "Hoàn thành"),
        ('huy', "Hủy")
    ], string="Trạng thái", default='moi')

    khach_hang_id = fields.Many2one('thong_tin_khach_hang', string="Khách hàng", required=True)


    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.price_unit