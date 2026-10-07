from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EquipmentAssignment(models.Model):
    _name = "equipment.assignment"
    _description = "Equipment Assignment"
    _order = "date_from desc ,id desc"

    equipment_id = fields.Many2one(
        "equipment.equipment",
        string="Equipment",
        required=True,
        index=True,
        ondelete="restrict",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        index=True,
        ondelete="restrict",
    )

    date_from = fields.Datetime(
        string="Given On",
        required=True,
        index=True,
        default=fields.Datetime.now,
    )

    date_to = fields.Datetime(
        string="Returned On",
        readonly=True,
        index=True
    )

    is_active = fields.Boolean(
        string="Active",
        compute="_compute_is_active",
        store=True,
    )

    note = fields.Text(string="Notes")


    def init(self):
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS equipment_assignment_one_open
            ON equipment_assignment (equipment_id) WHERE date_to IS NULL
        """)

    @api.depends("date_to")
    def _compute_is_active(self):
        for record in self:
            record.is_active = not record.date_to

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_to and record.date_to < record.date_from:
                raise ValidationError(
                    _("Return date cannot be before the given date.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            equipment = self.env["equipment.equipment"].browse(
                vals.get("equipment_id")
            )

            if equipment.state != "available":
                raise UserError(
                    _("This equipment is not available.")
                )

        records = super().create(vals_list)

        for record in records:
            record.equipment_id.sudo().write({
                "state": "in_use",
                "current_employee_id": record.employee_id.id,
            })

        return records

    def action_return(self):
        for record in self:
            if not record.is_active:
                continue

            record.write({
                "date_to": fields.Datetime.now(),
            })

            record.equipment_id.sudo().write({
                "state": "available",
                "current_employee_id": False,
            })

        return True