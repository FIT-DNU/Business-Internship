# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công Việc Dự Án'
    _rec_name = 'ten_cong_viec'

    # Thông tin cơ bản
    ma_cong_viec = fields.Char(string='Mã Công Việc', required=True)
    ten_cong_viec = fields.Char(string='Tên Công Việc', required=True)
    mo_ta = fields.Text(string='Mô Tả')
    du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')
    giai_doan_id = fields.Many2one('giai_doan_cong_viec', string='Giai Đoạn')

    # Nhân viên
    nguoi_phu_trach_id = fields.Many2one('nhan_vien', string='Người Phụ Trách', ondelete='set null')

    nhan_vien_ids = fields.Many2many('nhan_vien', 'cong_viec_nhan_vien_rel',
                                     'cong_viec_id', 'nhan_vien_id',
                                     string='Nhân Viên Tham Gia')
    nhan_vien_display = fields.Char(string="Nhân Viên Tham Gia",
                                    compute="_compute_nhan_vien_display")

    # Thời gian
    ngay_bat_dau = fields.Date(string='Ngày Bắt Đầu', default=fields.Date.today)
    han_chot = fields.Datetime(string='Hạn Chót')
    thoi_gian_con_lai = fields.Char(string="Thời Gian Còn Lại",
                                    compute="_compute_thoi_gian_con_lai",
                                    store=True)

    # Trạng thái và tiến độ
    priority = fields.Selection(
        selection=[
            ('low', 'Thấp'),
            ('medium', 'Trung bình'),
            ('high', 'Cao'),
        ],
        string='Mức độ ưu tiên',
        default='medium'
    )

    status = fields.Selection(
        selection=[
            ('not_started', 'Chưa bắt đầu'),
            ('in_progress', 'Đang thực hiện'),
            ('completed', 'Hoàn thành'),
            ('delayed', 'Trì hoãn'),
            ('cancelled', 'Hủy bỏ')
        ],
        string='Trạng thái',
        default='not_started'
    )

    phan_tram_cong_viec = fields.Float(
        string="Phần Trăm Hoàn Thành",
        compute="_compute_phan_tram_cong_viec",
        store=True,
        default=0.0
    )

    ly_do_huy_bo = fields.Text(string="Lý do hủy bỏ", help="Lý do hủy bỏ công việc")

    # Quan hệ với các model khác
    nhat_ky_cong_viec_ids = fields.One2many('nhat_ky_cong_viec', 'cong_viec_id',
                                           string='Nhật Ký Công Việc')
    danh_gia_nhan_vien_ids = fields.One2many('danh_gia_nhan_vien', 'cong_viec_id',
                                            string='Đánh Giá Nhân Viên')
    expense_ids = fields.One2many('expenses', 'cong_viec_id', string="Chi phí")

    _sql_constraints = [
        ('unique_ma_cong_viec', 'UNIQUE(ma_cong_viec)', 'Mã công việc đã tồn tại!')
    ]

    @api.depends('nhat_ky_cong_viec_ids.muc_do')
    def _compute_phan_tram_cong_viec(self):
        for record in self:
            if record.nhat_ky_cong_viec_ids:
                total_progress = sum(record.nhat_ky_cong_viec_ids.mapped('muc_do'))
                record.phan_tram_cong_viec = total_progress / len(record.nhat_ky_cong_viec_ids)
            else:
                record.phan_tram_cong_viec = 0.0

    @api.depends('nhan_vien_ids')
    def _compute_nhan_vien_display(self):
        for record in self:
            record.nhan_vien_display = ', '.join(record.nhan_vien_ids.mapped('display_name'))

    @api.depends('han_chot')
    def _compute_thoi_gian_con_lai(self):
        for record in self:
            if record.han_chot:
                now = datetime.now()
                delta = record.han_chot - now
                if delta.total_seconds() > 0:
                    days = delta.days
                    hours = delta.seconds // 3600
                    record.thoi_gian_con_lai = f"{days} ngày, {hours} giờ"
                else:
                    record.thoi_gian_con_lai = "Hết hạn"
            else:
                record.thoi_gian_con_lai = "Chưa có hạn chót"

    @api.onchange('du_an_id')
    def _onchange_du_an_id(self):
        if self.du_an_id and self.du_an_id.nhan_vien_ids:
            self.nhan_vien_ids = [(6, 0, self.du_an_id.nhan_vien_ids.ids)]
        else:
            self.nhan_vien_ids = [(5, 0, 0)]

    @api.onchange('nguoi_phu_trach_id')
    def _onchange_nguoi_phu_trach_id(self):
        if self.nguoi_phu_trach_id and self.nguoi_phu_trach_id not in self.nhan_vien_ids:
            self.nhan_vien_ids = [(4, self.nguoi_phu_trach_id.id)]

    @api.constrains('du_an_id')
    def _check_du_an_tien_do(self):
        for record in self:
            if record.du_an_id and record.du_an_id.tien_do_du_an == 'hoan_thanh':
                raise ValidationError("Không thể thêm công việc vào dự án đã hoàn thành.")

    @api.constrains('nhan_vien_ids', 'nguoi_phu_trach_id')
    def _check_nhan_vien_trong_du_an(self):
        for record in self:
            if record.du_an_id:
                nhan_vien_du_an_ids = record.du_an_id.nhan_vien_ids.ids
                for nhan_vien in record.nhan_vien_ids:
                    if nhan_vien.id not in nhan_vien_du_an_ids:
                        raise ValidationError(f"Nhân viên {nhan_vien.display_name} không thuộc dự án này.")

                if record.nguoi_phu_trach_id and record.nguoi_phu_trach_id.id not in nhan_vien_du_an_ids:
                    raise ValidationError("Người phụ trách phải thuộc dự án này.")

                if record.nguoi_phu_trach_id and record.nguoi_phu_trach_id not in record.nhan_vien_ids:
                    raise ValidationError("Người phụ trách phải nằm trong danh sách nhân viên tham gia.")

    def _create_thong_bao(self, nhan_vien, loai, tieu_de, noi_dung=None, du_an=None, cong_viec=None):
        cong_viec = cong_viec or (self if self and len(self) == 1 else False)
        du_an = du_an or (cong_viec.du_an_id if cong_viec and cong_viec.du_an_id else False)

        domain = [
            ('nhan_vien_id', '=', nhan_vien.id),
            ('loai', '=', loai),
            ('cong_viec_id', '=', cong_viec.id if cong_viec else False),
            ('du_an_id', '=', du_an.id if du_an else False),
            ('create_date', '>=', fields.Datetime.to_string(fields.Date.today())),
        ]
        if self.env['thong_bao_noi_bo'].sudo().search_count(domain):
            return

        self.env['thong_bao_noi_bo'].sudo().create({
            'name': tieu_de,
            'noi_dung': noi_dung or '',
            'nhan_vien_id': nhan_vien.id,
            'loai': loai,
            'cong_viec_id': cong_viec.id if cong_viec else False,
            'du_an_id': du_an.id if du_an else False,
        })

    @api.model
    def _cron_deadline_reminder(self):
        now = fields.Datetime.now()
        in_48h = now + timedelta(hours=48)
        in_24h = now + timedelta(hours=24)
        overdue_2d = now - timedelta(days=2)

        tasks = self.search([('han_chot', '!=', False), ('status', 'not in', ['completed', 'cancelled'])])
        for task in tasks:
            if not task.nguoi_phu_trach_id:
                continue

            if now <= task.han_chot <= in_48h:
                task._create_thong_bao(
                    task.nguoi_phu_trach_id,
                    'deadline_48h',
                    f"Nhắc hạn (48h): {task.ten_cong_viec}",
                    f"Công việc sắp đến hạn: {task.ten_cong_viec}. Hạn chót: {task.han_chot}",
                    cong_viec=task,
                )

            if now <= task.han_chot <= in_24h:
                task._create_thong_bao(
                    task.nguoi_phu_trach_id,
                    'deadline_24h',
                    f"Nhắc hạn (24h): {task.ten_cong_viec}",
                    f"Công việc còn 24h đến hạn: {task.ten_cong_viec}. Hạn chót: {task.han_chot}",
                    cong_viec=task,
                )

            if task.han_chot < now:
                if task.status != 'delayed':
                    task.status = 'delayed'

                task._create_thong_bao(
                    task.nguoi_phu_trach_id,
                    'overdue',
                    f"Quá hạn: {task.ten_cong_viec}",
                    f"Công việc đã quá hạn: {task.ten_cong_viec}. Hạn chót: {task.han_chot}",
                    cong_viec=task,
                )

                if task.han_chot <= overdue_2d and task.du_an_id and task.du_an_id.nguoi_phu_trach_id:
                    task._create_thong_bao(
                        task.du_an_id.nguoi_phu_trach_id,
                        'overdue_escalate',
                        f"Quá hạn > 2 ngày: {task.ten_cong_viec}",
                        f"Công việc quá hạn hơn 2 ngày: {task.ten_cong_viec}. Hạn chót: {task.han_chot}",
                        du_an=task.du_an_id,
                        cong_viec=task,
                    )