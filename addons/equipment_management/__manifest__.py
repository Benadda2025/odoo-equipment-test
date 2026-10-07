# -*- coding: utf-8 -*-
{
    "name": "Equipment Management",
    "summary": """
        Manage company equipment, employee assignments and assignment history""",
    "description": """
        Equipment Management
        ====================
        * Register company equipment (computers, phones, tools, accessories)
        * Assign equipment to employees and track handover and return dates
        * See equipment status at a glance (available, in use, maintenance, retired)
        * Full assignment history per equipment and per employee
        * Filters, group-by options and a clear menu structure
        * Two access levels: operational users and managers
        * Designed for large datasets (indexed fields, stored status)
    """,
    "author": "Benadda Fatima Zohra Nesrine",
    "version": "0.1",
    "depends": ["base", "hr"],
    "data": [
        # "security/security.xml",
        "security/ir.model.access.csv",
        "views/equipment_category_views.xml",
        "views/equipment_views.xml",
        "views/equipment_assignment_views.xml",
        "views/hr_employee_views.xml",
        "views/menus.xml",
        "data/equipment_category_data.xml",
        "data/equipment_data.xml",
    ],
   
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}