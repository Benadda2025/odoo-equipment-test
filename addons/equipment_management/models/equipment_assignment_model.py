# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class EquipmentAssignment(models.Model):
    _name = "equipment.assignment"
    _description = "Equipment Assignment"
    _order = "date_from desc, id desc"

    equipment_id = fields.Many2one(
        "equipment.equipment", required=True, index=True, ondelete="restrict"
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date_from = fields.Datetime(
        string="Given On", required=True, default=fields.Datetime.now, index=True
    )
    date_to = fields.Datetime(string="Returned On", index=True, copy=False)
    state = fields.Selection(
        [("active", "Active"), ("returned", "Returned")],
        default="active", required=True, index=True, copy=False,
    )
    note = fields.Text()

    def init(self):
        # Database-level guarantee: one active assignment per equipment (fast and race-safe)
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS equipment_assignment_one_active
            ON equipment_assignment (equipment_id) WHERE state = 'active'
        """)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            equipment = self.env["equipment.equipment"].browse(vals.get("equipment_id"))
            if equipment.state != "available":
                raise UserError(
                    f"{equipment.display_name} is not available (status: {equipment.state})."
                )
        records = super().create(vals_list)
        for rec in records:
            rec.equipment_id.write({
                "state": "in_use",
                "current_assignment_id": rec.id,
                "current_employee_id": rec.employee_id.id,
            })
        return records

    def action_return(self):
        active = self.filtered(lambda r: r.state == "active")
        active.write({"state": "returned", "date_to": fields.Datetime.now()})
        active.mapped("equipment_id").write({
            "state": "available",
            "current_assignment_id": False,
            "current_employee_id": False,
        })