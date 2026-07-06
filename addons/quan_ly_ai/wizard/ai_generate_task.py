# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time

from odoo import models, fields, api
from odoo.exceptions import UserError

from ..services.task_generator import generate_tasks_for_project


class AIGenerateTaskWizard(models.TransientModel):
    _name = "ai.generate.task.wizard"
    _description = "AI Generate Task Wizard"

    project_id = fields.Many2one(
        "du_an",
        string="Dự án",
        required=True,
        readonly=True,
    )

    ai_raw_response = fields.Text(
        string="Phản hồi gốc từ AI",
        readonly=True,
    )

    task_line_ids = fields.One2many(
        "ai.generate.task.line",
        "wizard_id",
        string="Danh sách công việc AI đề xuất",
    )

    note = fields.Text(
        string="Ghi chú",
        readonly=True,
        default=(
            "Bấm 'Sinh gợi ý AI' để Ollama/Qwen2.5 tạo danh sách công việc. "
            "Bạn có thể bỏ chọn hoặc chỉnh sửa từng dòng trước khi tạo công việc thật."
        ),
    )

    def action_generate_tasks(self):
        self.ensure_one()

        if not self.project_id:
            raise UserError("Thiếu dự án.")

        if not self.project_id.mo_ta:
            raise UserError("Dự án cần có mô tả để AI sinh công việc tốt hơn.")

        try:
            tasks, raw_response = generate_tasks_for_project(self.project_id)
        except Exception as error:
            raise UserError(str(error))

        if not tasks:
            raise UserError("AI không sinh được công việc nào.")

        commands = [(5, 0, 0)]
        for task in tasks:
            commands.append((0, 0, {
                "selected": True,
                "title": task["title"],
                "description": task["description"],
                "priority": task["priority"],
                "estimated_days": task["estimated_days"],
                "responsible_id": self.project_id.nguoi_phu_trach_id.id or False,
            }))

        self.write({
            "ai_raw_response": raw_response,
            "task_line_ids": commands,
        })

        return {
            "type": "ir.actions.act_window",
            "name": "AI Tạo Công Việc",
            "res_model": "ai.generate.task.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def _build_task_deadline(self, accumulated_days):
        base_date = self.project_id.ngay_bat_dau or fields.Date.context_today(self)
        deadline_date = base_date + timedelta(days=accumulated_days)
        return datetime.combine(deadline_date, time(hour=17, minute=0))

    def _generate_task_code(self, index):
        now_code = fields.Datetime.now().strftime("%Y%m%d%H%M%S")
        return f"AI-{self.project_id.id}-{now_code}-{index:02d}"

    def action_create_tasks(self):
        self.ensure_one()

        selected_lines = self.task_line_ids.filtered("selected")
        if not selected_lines:
            raise UserError("Bạn cần chọn ít nhất một công việc để tạo.")

        if not self.project_id.nhan_vien_ids:
            raise UserError("Dự án cần có nhân viên tham gia trước khi tạo công việc.")

        created_tasks = self.env["cong_viec"]

        accumulated_days = 0
        for index, line in enumerate(selected_lines, start=1):
            accumulated_days += line.estimated_days or 1

            responsible = line.responsible_id or self.project_id.nguoi_phu_trach_id
            member_ids = self.project_id.nhan_vien_ids.ids

            if responsible and responsible.id not in member_ids:
                member_ids.append(responsible.id)

            task_vals = {
                "ma_cong_viec": self._generate_task_code(index),
                "ten_cong_viec": line.title,
                "mo_ta": line.description,
                "du_an_id": self.project_id.id,
                "nguoi_phu_trach_id": responsible.id if responsible else False,
                "nhan_vien_ids": [(6, 0, member_ids)],
                "priority": line.priority,
                "status": "not_started",
                "han_chot": fields.Datetime.to_string(
                    self._build_task_deadline(accumulated_days)
                ),
            }

            created_tasks |= self.env["cong_viec"].create(task_vals)

        return {
            "type": "ir.actions.act_window",
            "name": "Công Việc Đã Tạo",
            "res_model": "cong_viec",
            "view_mode": "tree,form",
            "domain": [("id", "in", created_tasks.ids)],
            "target": "current",
        }


class AIGenerateTaskLine(models.TransientModel):
    _name = "ai.generate.task.line"
    _description = "AI Generate Task Line"

    wizard_id = fields.Many2one(
        "ai.generate.task.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )

    selected = fields.Boolean(
        string="Chọn",
        default=True,
    )

    title = fields.Char(
        string="Tên công việc",
        required=True,
    )

    description = fields.Text(
        string="Mô tả",
    )

    priority = fields.Selection(
        [
            ("low", "Thấp"),
            ("medium", "Trung bình"),
            ("high", "Cao"),
        ],
        string="Mức độ ưu tiên",
        default="medium",
        required=True,
    )

    estimated_days = fields.Integer(
        string="Số ngày dự kiến",
        default=1,
        required=True,
    )

    responsible_id = fields.Many2one(
        "nhan_vien",
        string="Người phụ trách",
    )

    @api.constrains("estimated_days")
    def _check_estimated_days(self):
        for record in self:
            if record.estimated_days < 1:
                raise UserError("Số ngày dự kiến phải lớn hơn hoặc bằng 1.")
