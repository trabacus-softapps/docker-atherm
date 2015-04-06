# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import time
from openerp import tools
import math
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta

class sale_order(osv.Model):
    _inherit = 'sale.order'
    
    _columns={
              'dc_type'     :   fields.selection([('refund_dc', 'Refundable DC'), ('non_refund_dc', 'Non Refundable DC')], 
                                                 'Deliver Challan Type',track_visibility='onchange'),
              'contact_id'          : fields.many2one('res.partner','Contact Person'),
              
              
              }
    _defaults = {
                'dc_type'   :   'non_refund_dc',         
                 }
    

#     Auto Generation of Sale Number
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        today = time.strftime("%Y-%m-%d")
        cr.execute("select code from account_fiscalyear where date_start <= '" + str(today) + "' and date_stop >='" + str(today) + "'")
        code = cr.fetchone()
        if not code:
            raise osv.except_osv(_('Warning!'), _('Fiscal Year does not exist'))
        if code:
            code = code[0] 
        if vals['partner_id']:
            sale_no = 'ATSQUO/' + code + '/'
            cr.execute("select name from sale_order where name like '"+sale_no+"'|| '%' order by to_number(substr(name,(length('"+sale_no+"')+1)),'99999') desc limit 1")
            prev_format = cr.fetchone()
            if not prev_format:
                name = sale_no + '0001'
            else:
                auto_gen = prev_format[0][-4:]
                name = sale_no + str(int(auto_gen) + 1).zfill(4)
            vals.update({'name':name})
        return super(sale_order, self).create(cr, uid, vals, context=context)
    

    # On select of customer pop up contact person
    def onchange_partner_id(self, cr, uid, ids,part, context=None):
        if not context:
            context={}
        partner_obj = self.pool.get("res.partner")
        partner_vals = super(sale_order,self).onchange_partner_id(cr, uid, ids, part, context=context)
        if part:
            partner = partner_obj.browse(cr, uid, part)
            cont = partner_obj.search(cr, uid, [('parent_id','=',part)], limit=1)
            partner_vals['value'].update({
                                          'contact_id' : cont and cont[0] or False, 
                                          'pricelist_id': partner.property_product_pricelist.id
            })
        return partner_vals
    

 # Inheriting action_ship_create Method to update DC_TYPE in Delivery Order and Creating Delivery Order number Sequence
    def action_ship_create(self, cr, uid, ids, context=None):
        if not context:
            context={}
        pick_ids=[]
        res = super(sale_order, self).action_ship_create(cr, uid, ids,context)
        if res:
            pick_obj=self.pool.get('stock.picking')
            for case in self.browse(cr,uid,ids):
                pick_ids=pick_obj.search(cr,uid,[('group_id','=',case.procurement_group_id.id)])
            if pick_ids:
                pick_obj.write(cr,uid,pick_ids,{'dc_type':case.dc_type})
                pick_obj.generate_seq(cr, uid, pick_ids, context=context)
            
        return res
    
    
    