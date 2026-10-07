# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    equipment_ids = fields.One2many(
        "equipment.equipment",
        "current_employee_id",
        string="Equipment",
    )

    equipment_count = fields.Integer(
        string="Equipment Count",
        compute="_compute_equipment_count",
    )

    history_count = fields.Integer(
    string="History Count",
    compute="_compute_history_count",
)

    def _compute_history_count(self):
        """Compute the number of equipment assignments for each employee."""
        data = self.env["equipment.assignment"]._read_group(
            [("employee_id", "in", self.ids)],
            ["employee_id"],
            ["__count"],
        )

        counts = {
            employee.id: count
            for employee, count in data
        }

        for employee in self:
            employee.history_count = counts.get(employee.id, 0)

    def _compute_equipment_count(self):
        """Compute the number of equipment currently assigned to each employee."""
        data = self.env["equipment.equipment"]._read_group(
            [("current_employee_id", "in", self.ids)],
            ["current_employee_id"],
            ["__count"],
        )

        counts = {
            employee.id: count
            for employee, count in data
        }

        for employee in self:
            employee.equipment_count = counts.get(employee.id, 0)

    def action_view_equipment(self):
        """Open equipment currently assigned to the employee."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Equipment",
            "res_model": "equipment.equipment",
            "view_mode": "list,form",
            "domain": [
                ("current_employee_id", "=", self.id)
            ],
        }

    def action_view_equipment_history(self):
        """Open all equipment assignments of the employee."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Equipment History",
            "res_model": "equipment.assignment",
            "view_mode": "list,form",
            "domain": [
                ("employee_id", "=", self.id)
            ],
            "context": {
                "default_employee_id": self.id,
            },
        }

    def action_assign_equipment(self):
        """Open the form to assign equipment to the employee."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Give Equipment",
            "res_model": "equipment.assignment",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_employee_id": self.id,
            },
        }