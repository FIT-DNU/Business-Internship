from odoo import models, fields, api

class ChiTietSanPham(models.Model):
    _name = 'chi_tiet_san_pham'
    _description = 'Chi tiết sản phẩm linh kiện máy tính'

    name = fields.Char(string='Tên sản phẩm', required=True)
    
    category = fields.Selection([
        ('mainboard', 'Mainboard'),
        ('cpu', 'CPU'),
        ('gpu', 'GPU'),
        ('ram', 'RAM'),
        ('storage', 'Ổ cứng')
    ], string='Loại sản phẩm', required=True)

    brand = fields.Selection([
        ('gigabyte', 'Gigabyte'),
        ('asus', 'ASUS'),
        ('msi', 'MSI')
    ], string='Thương hiệu', required=True)

    price_unit = fields.Float(string='Đơn giá', required=True, default=0.0)
    stock_quantity = fields.Integer(string='Số lượng tồn kho', default=0)
    warranty = fields.Integer(string='Bảo hành (tháng)', default=12)

    total_value = fields.Float(string='Tổng giá trị kho', compute='_compute_total_value', store=True)

    @api.depends('price_unit', 'stock_quantity')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.price_unit * record.stock_quantity
