# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EquipmentEquipment(models.Model):
    _name = "equipment.equipment"
    _description = "Equipment"
    _order = "name, id"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )

    code = fields.Char(
        string="Code",
        copy=False,
        index=True,
                    readonly=True,


    )

    category_id = fields.Many2one(
        "equipment.category",
        string="Category",
        index=True,
        ondelete="restrict",
    )

    serial_number = fields.Char(
        string="Serial Number",
        copy=False,
        index=True,
    )

    purchase_date = fields.Date(
        string="Purchase Date",
        index=True,
    )

    state = fields.Selection(
        [
            ("available", "Available"),
            ("in_use", "In Use"),
            ("maintenance", "Maintenance"),
            ("retired", "Retired"),
        ],
        string="Status",
        required=True,
        default="available",
        index=True,
    )

    current_employee_id = fields.Many2one(
        "hr.employee",
        string="Current Employee",
        index=True,
        copy=False,
        ondelete="set null",
    )

    assignment_ids = fields.One2many(
        "equipment.assignment",
        "equipment_id",
        string="Assignment History",
    )

    assignment_count = fields.Integer(
        string="Assignment Count",
        compute="_compute_assignment_count",
    )

    active = fields.Boolean(
        default=True,
    )

    note = fields.Text(
        string="Notes",
    )

    _sql_constraints = [
        (
            "equipment_code_unique",
            "unique(code)",
            "Equipment code must be unique.",
        ),
        (
            "equipment_serial_unique",
            "unique(serial_number)",
            "Serial number must be unique.",
        ),
    ]

    @api.depends("assignment_ids")
    def _compute_assignment_count(self):
        for equipment in self:
            equipment.assignment_count = len(equipment.assignment_ids)

   
    def action_assign_equipment(self):
        """Open the assignment form for this equipment."""
        self.ensure_one()

        if self.state != "available":
            raise UserError(
                _("%s is not available.") % self.display_name
            )

        return {
            "type": "ir.actions.act_window",
            "name": "Give Equipment",
            "res_model": "equipment.assignment",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_equipment_id": self.id,
            },
        }

    def action_send_to_maintenance(self):
        """Move equipment to maintenance."""
        for equipment in self:
            if equipment.state == "retired":
                raise UserError(
                    _("Retired equipment cannot be sent to maintenance.")
                )

            if equipment.state == "in_use":
                raise UserError(
                    _("Return the equipment before sending it to maintenance.")
                )

            equipment.write({
                "state": "maintenance",
                "current_employee_id": False,
            })

        return True

    def action_back_to_available(self):
        """Make equipment available again."""
        for equipment in self:
            if equipment.state == "retired":
                raise UserError(
                    _("Retired equipment cannot be made available.")
                )

            if equipment.state == "in_use":
                raise UserError(
                    _("Return the equipment before making it available.")
                )

            equipment.write({
                "state": "available",
                "current_employee_id": False,
            })

        return True

    def action_retire(self):
        """Retire equipment permanently."""
        for equipment in self:
            if equipment.state == "in_use":
                raise UserError(
                    _("Return the equipment before retiring it.")
                )

            equipment.write({
                "state": "retired",
                "current_employee_id": False,
            })

        return True

    def action_view_assignment_history(self):
        """Open the complete assignment history."""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Assignment History",
            "res_model": "equipment.assignment",
            "view_mode": "list,form",
            "domain": [
                ("equipment_id", "=", self.id),
            ],
            "context": {
                "default_equipment_id": self.id,
            },
        }

    def unlink(self):
        """Prevent deletion when equipment has assignment history."""
        if self.filtered("assignment_ids"):
            raise UserError(
                _(
                    "Equipment with assignment history cannot be deleted. "
                    "Archive it instead."
                )
            )

        return super().unlink()
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "equipment.equipment"
                )

        return super().create(vals_list)