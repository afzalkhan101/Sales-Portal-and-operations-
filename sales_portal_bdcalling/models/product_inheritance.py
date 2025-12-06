from odoo import models, fields

class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    portal_available = fields.Boolean()
    is_portal = fields.Boolean(string="Is Portal")
    is_purchase_requisition = fields.Boolean(string="Is Purchase Requisition", default=False)
