# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Budgets(models.Model):
    _name = 'budgets'
    _description = 'Ngân sách dự án'
    _rec_name = 'budgets_name'

    budgets_id = fields.Char('Mã ngân sách', required=True)
    budgets_name = fields.Char(string="Tên Ngân Sách", required=True)
    du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')

    expense_ids = fields.One2many('expenses', 'budgets_id', string='Chi Phí')

    budget_planned = fields.Float(string="Ngân sách Dự toán", required=True)
    budget_allocated = fields.Float(string="Ngân sách Phân bổ", required=True)
    budget_reserved = fields.Float(string="Ngân sách Dự trù")
    budget_spent = fields.Float(string="Chi phí Thực tế", compute="_compute_budget_spent", store=True)
    budget_difference = fields.Float(string="Chênh lệch Ngân sách", compute="_compute_budget_difference", store=True)

    _sql_constraints = [
        ('unique_budgets_id', 'UNIQUE(budgets_id)', 'Mã ngân sách đã tồn tại!')
    ]

    @api.depends('expense_ids.amount')
    def _compute_budget_spent(self):
        for record in self:
            record.budget_spent = sum(record.expense_ids.mapped('amount'))

    @api.depends('budget_planned', 'budget_spent')
    def _compute_budget_difference(self):
        """Tính toán chênh lệch ngân sách"""
        for record in self:
            record.budget_difference = record.budget_planned - record.budget_spent





