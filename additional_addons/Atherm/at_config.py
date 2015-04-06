# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from openerp.osv import fields, osv

class res_currency(osv.Model):
    _inherit = "res.currency"
    
    _columns={
              'number_name'     : fields.char("Number Name"),
              'decimal_name'    : fields.char("Decimal Name"),
              
              }
res_currency()

class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns={
              'your_tech_data'      :   fields.text("Your Technical Data"),
              'our_tech_data'       :   fields.text("Our Technical Data"),
              
              }

product_template()