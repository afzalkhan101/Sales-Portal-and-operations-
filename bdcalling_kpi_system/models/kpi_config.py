
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KpiRole(models.Model):
    _name = 'kpi.role'
    _description = 'KPI Role'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Role Name', required=True ,tracking =True)
    is_active= fields.Boolean(default=True ,tracking =True)
    role_type = fields.Selection([
        ('sale', 'Sales'),('operation', 'Operation'),('other','Others')], string='Role Type',default='sale',tracking =True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True ,tracking =True)
    state = fields.Selection([('draft','Draft'),('done','Confirm')],string="Status", default='draft', tracking=True)

    def action_draft(self):
        if self.state =="draft":
            return 
        self.state = 'draft'

    def action_confirm(self):
        if self.state =="done":
            return 
        self.state = 'done'


class KpiGrade(models.Model):
    _name = 'kpi.grade'
    _description = 'KPI Grade'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    name = fields.Char('Grade Name',required=True)
    role_id = fields.Many2one('kpi.role', string='Role', required=True, domain="[('is_active', '=', True), ('company_id', '=', company_id)]" ,tracking =True)
    minimum_target = fields.Float('Minimum Target', required=True ,tracking =True)

    minimum_salary = fields.Float('Minimum Salary', required=True ,tracking =True)
    maximum_salary = fields.Float('Maximum Salary', required=True ,tracking =True)
    is_active = fields.Boolean(default=True ,tracking =True)
    level_ids = fields.One2many('kpi.level', 'grade_id', string='Levels' ,tracking =True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True ,tracking =True)
    state = fields.Selection([('draft','Draft'),('done','Confirm')],string="Status", default='draft', tracking=True)

    @api.constrains('minimum_target', 'minimum_salary', 'maximum_salary')
    def _check_values(self):
        for record in self:
            if record.minimum_target <= 0:
                raise ValidationError(_("Minimum target must be greater than zero."))
            if record.minimum_salary >= record.maximum_salary:
                raise ValidationError(_("Minimum salary must be less than maximum salary."))
    def action_draft(self):
        if self.state =="draft":
            return 
        self.state = 'draft'

    def action_confirm(self):
        if self.state =="done":
            return 
        self.state = 'done'

            
            
class KpiLevel(models.Model):

    _name = 'kpi.level'
    _description = 'KPI Level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
  
    
    name = fields.Char('Level Name', required=True)
    grade_id = fields.Many2one('kpi.grade', string='Grade', required=True, ondelete='cascade')
    min_amount = fields.Float('Minimum Amount', required=True)
    max_amount = fields.Float('Maximum Amount', required=False)
    bonus_amount = fields.Float('Bonus Amount', required=True)
    company_id = fields.Many2one(related='grade_id.company_id', store=True)
    
    @api.constrains('min_amount', 'max_amount')
    def _check_amount_range(self):
         for record in self:
            if record.max_amount and record.min_amount >= record.max_amount:
                raise ValidationError(_("Minimum amount must be less than maximum amount."))
            
            domain = [
                ('id', '!=', record.id),
                ('grade_id', '=', record.grade_id.id)
            ]

            existing_levels = self.search(domain)

            for level in existing_levels:
                level_max = level.max_amount if level.max_amount else float('inf')  
                record_max = record.max_amount if record.max_amount else float('inf')
                if not (record.min_amount >= level_max or record_max <= level.min_amount):
                    raise ValidationError(_("Level ranges cannot overlap within the same grade."))
   