
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    
    role_id = fields.Many2one("kpi.role",string="Role",required=True)
    salary = fields.Integer("Salary")
    grade_id  = fields.Many2one("kpi.grade",string="Grade",required=True)
    minimum_target = fields.Integer(string="Minimum Target",required=True)
    this_mounth_target =fields.Integer(string="This Month Target")
    penalty_amount_ = fields.Integer( string="Penalty Amount",default=0)

    @api.onchange('role_id', 'salary')
    def _onchange_role_salary(self):
        if self.role_id and self.salary:
            grade = self.env['kpi.grade'].search([
                ('role_id', '=', self.role_id.id),
                ('minimum_salary', '<=', self.salary),
                ('maximum_salary', '>=', self.salary),
                ('is_active', '=', True),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            
            if grade:
                self.grade_id = grade.id
                self.minimum_target = grade.minimum_target
            else:
                self.grade_id = False
                self.minimum_target = 0