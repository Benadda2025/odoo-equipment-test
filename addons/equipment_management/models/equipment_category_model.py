# -*- coding: utf-8 -*-
from odoo import fields, models


class EquipmentCategory(models.Model):
    _name = "equipment.category"
    _description = "Equipment Category"
    _order = "name"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "This category already exists."),
    ]