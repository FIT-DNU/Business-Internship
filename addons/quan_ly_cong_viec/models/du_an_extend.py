# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DuAnExtend(models.Model):
    _inherit = 'du_an'

    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string='Công Việc')
    danh_gia_nhan_vien_ids = fields.One2many(
        'danh_gia_nhan_vien',
        'du_an_id',
        string='Đánh Giá Nhân Viên'
    )

    @api.depends('cong_viec_ids.phan_tram_cong_viec', 'cong_viec_ids.status')
    def _compute_phan_tram_du_an(self):
        for record in self:
            tasks = record.cong_viec_ids.filtered(
                lambda task: task.status != 'cancelled'
            )

            if not tasks:
                record.phan_tram_du_an = 0.0
                continue

            record.phan_tram_du_an = sum(
                tasks.mapped('phan_tram_cong_viec')
            ) / len(tasks)

    def _sync_project_status_from_progress(self):
        for record in self:
            if record.tien_do_du_an in ('huy_bo', 'tam_dung'):
                continue

            if record.phan_tram_du_an >= 100:
                record.tien_do_du_an = 'hoan_thanh'
            elif record.phan_tram_du_an > 0:
                record.tien_do_du_an = 'dang_thuc_hien'
            else:
                record.tien_do_du_an = 'chua_bat_dau'


class CongViecProjectSync(models.Model):
    _inherit = 'cong_viec'

    def _sync_related_projects(self):
        projects = self.mapped('du_an_id')
        if projects:
            projects._compute_phan_tram_du_an()
            projects._sync_project_status_from_progress()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._sync_related_projects()
        return record

    def write(self, vals):
        result = super().write(vals)
        if {'phan_tram_cong_viec', 'status', 'du_an_id', 'nhat_ky_cong_viec_ids'} & set(vals):
            self._sync_related_projects()
        return result

    def unlink(self):
        projects = self.mapped('du_an_id')
        result = super().unlink()
        if projects:
            projects._compute_phan_tram_du_an()
            projects._sync_project_status_from_progress()
        return result


class GiaiDoanCongViecExtend(models.Model):
    _inherit = 'giai_doan_cong_viec'

    cong_viec_ids = fields.One2many(
        'cong_viec',
        'giai_doan_id',
        string='Công Việc Trong Giai Đoạn'
    )
