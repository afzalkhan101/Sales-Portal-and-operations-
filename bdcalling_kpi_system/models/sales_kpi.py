from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class SalesKPI(models.Model):
    _name = "sales.kpi"
    _description = "Sales KPI"
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
    minimum_target = fields.Float(string="Minimum Target" ,tracking=True)
    total_operations = fields.Float(string="Total Operations" ,tracking=True)
    period_start = fields.Date('Period Start', required=True, 
                              default=lambda self: date(fields.Date.context_today(self).year, 
                                                 fields.Date.context_today(self).month, 1) - relativedelta(months=1))
    bonus_amount = fields.Float('Bonus Amount', required=True, default=0.0)
    this_month_target = fields.Float(string="This Month Target" ,tracking=True)
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
    Surplus = fields.Float( string="Surplus" )
    shortfall_amount = fields.Float('Shortfall Amount', default=0.0, help="Amount by which sales fell short of minimum target")
    is_penalty = fields.Boolean('Is Penalty', default=False, 
                               help="Indicates if this record represents a penalty for not meeting minimum target")
    
    @api.constrains("period_start", "period_end")
    def _check_period(self):
        for rec in self:
            if rec.period_start and rec.period_end and rec.period_start > rec.period_end:
                raise ValidationError(_("Start date must be before end date."))
    

    def action_calculate(self):
        
        self.ensure_one()
        self.minimum_target = self.grade_id.minimum_target
        operations = self.env['sale.order'].search([
            ('employee_id', '=', self.employee_id.id),
            ('delivery_date', '>=', self.period_start),
            ('delivery_date', '<=', self.period_end),
            ('order_status', '=', 'delivered'),  
           ])
        
        total_operations = 0 
        if operations:
            for val in operations:
                total_operations = total_operations + val.delivery_amount
        self.total_operations = total_operations

        if self.total_operations >=self.this_month_target:
            self.Surplus = self.total_operations - self.this_month_target
            self.this_month_target =  self.employee_id.minimum_target
            
        elif self.total_operations <= self.this_month_target:
            self.shortfall_amount = self.this_month_target - self.total_operations
            self.this_month_target = self.minimum_target  + self.shortfall_amount
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


        last_operation = self.env['sales.kpi'].search([
            ('employee_id', '=', self.employee_id.id),
            ('period_end', '<', self.period_start) 
        ], order='period_end desc', limit=1)

        print("############LLLLLLLLLL",last_operation)

        self.state = 'calculated'
    

    @api.onchange("employee_id")
    def _onchnage(self):
        self.role_id = self.employee_id.role_id
        self.grade_id = self.employee_id.grade_id
        self.this_month_target = self.employee_id.this_mounth_target
     

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

