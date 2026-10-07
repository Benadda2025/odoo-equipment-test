# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class Equipment(models.Model):
    _name = "equipment.equipment"
    _description = "Equipment"
    _order = "name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(string="Reference", required=True, copy=False, index=True)
    serial_number = fields.Char(index=True, copy=False)
    category_id = fields.Many2one("equipment.category", required=True, index=True)
    purchase_date = fields.Date()
    state = fields.Selection(
        [("available", "Available"), ("in_use", "In Use"),
         ("maintenance", "Maintenance"), ("retired", "Retired")],
        default="available", required=True, index=True,
    )
    # Stored copy of the open assignment: "who has what" never scans the history
    current_assignment_id = fields.Many2one(
        "equipment.assignment", string="Current Assignment", index=True, copy=False
    )
    current_employee_id = fields.Many2one(
        "hr.employee", string="Assigned To", index=True, copy=False
    )
    assignment_ids = fields.One2many("equipment.assignment", "equipment_id")
    assignment_count = fields.Integer(compute="_compute_assignment_count")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The reference must be unique."),
    ]

    def _compute_assignment_count(self):
        data = self.env["equipment.assignment"]._read_group(
            [("equipment_id", "in", self.ids)], ["equipment_id"], ["__count"]
        )
        counts = {equipment.id: count for equipment, count in data}
        for rec in self:
            rec.assignment_count = counts.get(rec.id, 0)

    def action_view_assignments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Assignment History",
            "res_model": "equipment.assignment",
            "view_mode": "list,form",
            "domain": [("equipment_id", "=", self.id)],
            "context": {"default_equipment_id": self.id},
        }

    def action_set_maintenance(self):
        if any(r.state == "in_use" for r in self):
            raise UserError("Return the equipment before sending it to maintenance.")
        self.write({"state": "maintenance"})

    def action_set_available(self):
        self.filtered(lambda r: r.state == "maintenance").write({"state": "available"})