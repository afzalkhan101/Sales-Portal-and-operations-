from odoo import models, fields, api
from datetime import datetime, date, timedelta
class SaleOrder(models.Model):
    _inherit = "sale.order"
    _rec_name = "order_number"

    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_barcode = fields.Char(string="Employee ID")
    company_id = fields.Many2one('res.company', string="Company")

    platform_source_id = fields.Many2one(
        comodel_name='bd.platform.source',
        string="Platform Source",
        tracking=True
    )

    profile_name_id = fields.Many2one(
        comodel_name='bd.profile.name',
        string="Profile Name",
        tracking=True
    )

    order_source_id = fields.Many2one(
        comodel_name='bd.order.source',
        string="Order Source",
        tracking=True
    )
    client_id =fields.Many2one('res.partner', string="Client Name")

    shift = fields.Selection(
        [
            ('morning', 'Morning'),
            ('evening', 'Evening'),
            ('night', 'Night')
        ],
        string="Shift",
        default='morning'
    )

    order_number = fields.Char(string="Order Number")
    order_link = fields.Char(string="Order Link")
    instruction_sheet_link = fields.Char(string="Instruction Sheet Link")

    service_type_id = fields.Many2one(
        'product.template',
        string="Service Type",
        domain=[('portal_available', '=', True)]
    )

    order_status = fields.Selection([
        ('nra', 'NRA'),
        ('wip', 'WIP'),
        ('delivered', 'Delivered'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
        ('revisions', 'Issues')
    ], string="Order Status", default='wip')

    incoming_date = fields.Date(string="Incoming Date")
    delivery_last_date = fields.Date(string="Delivery Last Date")
    deadline = fields.Datetime(string="Deadline", compute="_compute_deadline", store=True)
    sales_amount = fields.Float(string="Sales Amount")
    percentage = fields.Float(string="Percentage (%)")
    charges_amount =fields.Float(string="Charges Amount")
    delivery_amount = fields.Float(string="Delivery Amount", compute="_compute_delivery_amount", store=True)

    assign_team_id = fields.Many2one(
    'bd.assign.team',
    string="Assign Team"
    )

    tag_ids = fields.Many2many(
        'crm.tag',  
        string="Tags"
    )

    special_remarks = fields.Text(
        string="Special Remarks"
    )


    def name_get(self):
        result = []
        for record in self:
            name = record.order_number or record.client_id.name or 'Sale Order'
            result.append((record.id, name))
        return result

    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('order_number', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('client_id.name', operator, name)] + args, limit=limit)
        return recs.name_get()


    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'order_status' in vals or 'assign_team_id' in vals:
            for order in self:
                operations = self.env['project.operation'].search([('order_id', '=', order.id)])
                update_vals = {}
                if 'order_status' in vals:
                    update_vals['order_status'] = vals['order_status']
                if 'assign_team_id' in vals:
                    update_vals['assigned_team_id'] = vals.get('assign_team_id')
                
                if update_vals:
                    operations.write(update_vals)
        
        return res
    

    @api.depends('sales_amount', 'percentage')
    def _compute_delivery_amount(self):
        for record in self:
            if record.sales_amount and record.percentage is not None:
                record.delivery_amount = record.sales_amount - (record.sales_amount * record.percentage / 100)
                record.charges_amount = record.sales_amount - record.delivery_amount
            else:
                record.delivery_amount = 0

    @api.depends('delivery_last_date')
    def _compute_deadline(self):
        today = datetime.now()
        for record in self:
            if record.delivery_last_date:
                delivery_datetime = datetime.combine(record.delivery_last_date, datetime.max.time())
                record.deadline = delivery_datetime
                if delivery_datetime < today:
                    record.deadline = delivery_datetime 
            else:
                record.deadline = False

    @api.onchange("employee_id")
    def get_employee_barcode(self):
        if self.employee_id:
            self.employee_barcode = self.employee_id.barcode
            self.company_id = self.employee_id.company_id
        else:
            self.employee_barcode = False



class Team(models.Model):
    _name = "bd.team"
    _description = "Sales Team"
    _rec_name = "name"

    name = fields.Char(string="Team Name", required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)


class PlatformSource(models.Model):
    _name = 'bd.platform.source'
    _description = "Platform / Lead Source"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True, tracking=True)


class OrderSource(models.Model):
    _name = "bd.order.source"
    _description = "Order Source"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True, tracking=True)


class ProfileName(models.Model):
    _name = 'bd.profile.name'
    _description = "Profile Name"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    platform_source_id = fields.Many2one('bd.platform.source', string="Platform Source")
    company_id = fields.Many2one('res.company', string="Company")
