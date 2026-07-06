# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Expenses(models.Model):
    _name = 'expenses'
    _description = 'Chi phí thực tế'

    expenses_name = fields.Char(string="Tên Khoản Chi", required=True)
    cong_viec_id = fields.Many2one('cong_viec', string="Công việc", ondelete='cascade')
    budgets_id = fields.Many2one('budgets', string="Ngân sách", required=True, ondelete='cascade')
    du_an_id = fields.Many2one('du_an', string="Dự án", related='budgets_id.du_an_id', store=True, readonly=True)
    amount = fields.Float(string="Số tiền", required=True)
    date = fields.Date(string="Ngày chi tiêu", required=True, default=fields.Date.today)
    mo_ta = fields.Text(string="Mô tả")

    ly_do_vuot_ngan_sach = fields.Text(string="Lý do vượt ngân sách")

    def _create_thong_bao_ngan_sach(self, nhan_vien, loai, tieu_de, noi_dung, du_an=None):
        domain = [
            ('nhan_vien_id', '=', nhan_vien.id),
            ('loai', '=', loai),
            ('budgets_id', '=', False),
            ('du_an_id', '=', du_an.id if du_an else False),
            ('create_date', '>=', fields.Datetime.to_string(fields.Date.today())),
        ]
        # Không spam thông báo cùng loại trong ngày cho cùng dự án
        if self.env['thong_bao_noi_bo'].sudo().search_count(domain):
            return

        self.env['thong_bao_noi_bo'].sudo().create({
            'name': tieu_de,
            'noi_dung': noi_dung,
            'nhan_vien_id': nhan_vien.id,
            'loai': loai,
            'du_an_id': du_an.id if du_an else False,
        })

    def _check_budget_and_notify_or_block(self, new_vals=None):
        """Kiểm soát ngân sách:
        - >=80%: cảnh báo (thông báo nội bộ)
        - >100%: chặn nếu không có lý do
        """
        new_vals = new_vals or {}
        for rec in self:
            budgets = rec.budgets_id
            if not budgets or not budgets.budget_planned:
                continue

            new_amount = new_vals.get('amount', rec.amount)
            planned = budgets.budget_planned
            spent_current = budgets.budget_spent

            # Khi update, budget_spent đang bao gồm amount cũ của rec.
            # Nên tính lại spent_if_after.
            spent_if_after = spent_current - rec.amount + new_amount

            ratio = spent_if_after / planned if planned else 0.0

            # Cảnh báo 80%: gửi cho người phụ trách dự án nếu có
            if ratio >= 0.8 and budgets.du_an_id and budgets.du_an_id.nguoi_phu_trach_id:
                self.env['cong_viec']._create_thong_bao(
                    budgets.du_an_id.nguoi_phu_trach_id,
                    'budget_80',
                    f"Cảnh báo ngân sách >=80%: {budgets.du_an_id.ten_du_an}",
                    f"Ngân sách dự toán: {planned}. Chi phí dự kiến sau cập nhật: {spent_if_after}.",
                    du_an=budgets.du_an_id,
                    cong_viec=False,
                )

            # Chặn vượt 100% nếu không có lý do
            if ratio > 1.0:
                ly_do = new_vals.get('ly_do_vuot_ngan_sach', rec.ly_do_vuot_ngan_sach)
                if not ly_do:
                    raise ValidationError("Chi phí vượt 100% ngân sách. Vui lòng nhập 'Lý do vượt ngân sách'.")

                if budgets.du_an_id and budgets.du_an_id.nguoi_phu_trach_id:
                    self.env['cong_viec']._create_thong_bao(
                        budgets.du_an_id.nguoi_phu_trach_id,
                        'budget_over',
                        f"Vượt ngân sách >100%: {budgets.du_an_id.ten_du_an}",
                        f"Ngân sách dự toán: {planned}. Chi phí dự kiến sau cập nhật: {spent_if_after}.\nLý do: {ly_do}",
                        du_an=budgets.du_an_id,
                        cong_viec=False,
                    )

    @api.model
    def create(self, vals):
        record = super(Expenses, self).create(vals)
        record._check_budget_and_notify_or_block()
        return record

    def write(self, vals):
        res = super(Expenses, self).write(vals)
        for rec in self:
            rec._check_budget_and_notify_or_block(new_vals=vals)
        return res