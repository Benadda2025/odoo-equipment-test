# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    equipment_ids = fields.One2many(
        "equipment.equipment", "current_employee_id", string="Equipment"
    )
    equipment_count = fields.Integer(compute="_compute_equipment_count")

    def _compute_equipment_count(self):
        # One grouped query for all employees instead of one query per record
        data = self.env["equipment.equipment"]._read_group(
            [("current_employee_id", "in", self.ids)],
            ["current_employee_id"],
            ["__count"],
        )
        counts = {employee.id: count for employee, count in data}
        for rec in self:
            rec.equipment_count = counts.get(rec.id, 0)

    def action_view_equipment(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Equipment",
            "res_model": "equipment.equipment",
            "view_mode": "list,form",
            "domain": [("current_employee_id", "=", self.id)],
            "context": {"default_current_employee_id": self.id},
        }