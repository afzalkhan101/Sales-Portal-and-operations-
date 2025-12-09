from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class OperationsKPI(models.Model):
    _name = "operations.kpi"
    _description = "Operations KPI"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one(
    "hr.employee",
    string="Employee",
    required=True,
    default=lambda self: self.env.user.employee_id.id
    )
    role_id = fields.Many2one("kpi.role", string="Role", required=True , tracking=True )
    grade_id = fields.Many2one("kpi.grade", string="Grade" , tracking=True)
    total_operations = fields.Float(string="Total Operations" ,tracking=True)
    this_month_target = fields.Float(string="This Month Target" ,tracking=True)
    shortfall_amount = fields.Float(string="Shortfall Amount")
    Surplus = fields.Float( string="Surplus" )
    period_start = fields.Date('Period Start', required=True, 
                              default=lambda self: date(fields.Date.context_today(self).year, 
                                                 fields.Date.context_today(self).month, 1) - relativedelta(months=1))
    period_end = fields.Date('Period End', required=True,
                            default=lambda self: date(fields.Date.context_today(self).year, 
                                                     fields.Date.context_today(self).month, 1) - relativedelta(days=1))
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    state = fields.Selection([
    ('draft', 'Draft'),
    ('calculated', 'Calculated'),
    ('done', 'Confirmed'),
     ('paid', 'Paid'),
    ], string="Status", default='draft', tracking=True)
    bonus_amount =fields.Float(string="Bonus Amount",required=True)


    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for rec in self:
            if rec.period_start and rec.period_end and rec.period_start > rec.period_end:
                raise ValidationError(_("Start date must be before end date."))
    
    @api.onchange("employee_id")
    def _onchnage_employee_id(self):
        self.grade_id = self.employee_id.grade_id
        self.role_id = self.employee_id.role_id 
        self.this_month_target  = self.employee_id.this_mounth_target

    def action_calculate(self):
        self.ensure_one()
        operations = self.env['project.operation'].search([
            ('employee_id', '=', self.employee_id.id),
            ('delivery_date', '>=', self.period_start),
            ('delivery_date', '<=', self.period_end),
            ('operation_status', '=', 'delivered'),  
           ])
        total_operations = 0 
        if operations:
            for val in operations:
                total_operations = total_operations + val.monetary_value 
        self.total_operations = total_operations
        if self.total_operations >=self.this_month_target:
            self.Surplus = self.total_operations - self.this_month_target
        elif self.total_operations <= self.this_month_target:
            if self.shortfall_amount==0:
               self.shortfall_amount = self.this_month_target - self.total_operations 
            else:
                self.shortfall_amount = 0 
        bonus = 0

        if self.grade_id and self.Surplus > 0:

            level = self.env['kpi.level'].search([
                ('grade_id', '=', self.grade_id.id),
                ('min_amount', '<=', self.Surplus),
                '|',
                ('max_amount', '>=', self.Surplus),
                ('max_amount', '=', False)
            ], limit=1)

            self.bonus_amount = level.bonus_amount

        last_operation = self.env['operations.kpi'].search([
            ('employee_id', '=', self.employee_id.id),
            ('period_end', '<', self.period_start) 
        ], order='period_end desc', limit=1)

        self.state = 'calculated'

    def action_draft(self):
        if self.state =="draft":
            return 
        self.state = 'draft'

    def action_confirm(self):
        if self.state =="done":
            return 
        self.state = 'done'

    def action_mark_paid(self):
        if self.state =='paid':
            return 
        self.state = 'paid'
