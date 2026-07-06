# -*- coding: utf-8 -*-

from odoo import models


class DuAnAI(models.Model):
    _inherit = "du_an"

    def action_open_ai_generate_task_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "AI Tạo Công Việc",
            "res_model": "ai.generate.task.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_project_id": self.id,
            },
        }
