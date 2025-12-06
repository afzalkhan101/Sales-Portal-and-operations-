from odoo import models, fields

class AssignTeam(models.Model):
    _name = "bd.assign.team"
    _description = "Sales Team"
    _rec_name = "name"
    
    name = fields.Char(string="Team Name", required=True)
    leader_id = fields.Many2one('hr.employee', string="Team Leader")
    members_ids = fields.Many2many('hr.employee', string="Team Members") 
    company_id = fields.Many2one('res.company', string='Company', required=True)
