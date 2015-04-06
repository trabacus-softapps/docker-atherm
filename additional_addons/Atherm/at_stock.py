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


class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns={
              
                'dc_type'     :   fields.selection([('refund_dc', 'Refundable DC'), ('non_refund_dc', 'Non Refundable DC')], 'Deliver Challan Type',track_visibility='onchange'),
                'destination' :   fields.char("Destination", size=30),
                'vehicle_no'  :   fields.char("Vehicle No", size=30),
                'esugam_no'   :   fields.char("E-sugam No", size=30),
             }


    """ Auto Generation of Stock Number"""
    def generate_seq(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        today = time.strftime("%Y-%m-%d")
        cr.execute("select code from account_fiscalyear where date_start <= '" + str(today) + "' and date_stop >='" + str(today) + "'")
        code = cr.fetchone()
        if not code:
            raise osv.except_osv(_('Warning!'), _('Fiscal Year does not exist'))
        if code:
            code = code[0] 
            for case in self.browse(cr, uid, ids):
                if case.picking_type_id.code =="outgoing":
                    if case.dc_type =="refund_dc":
                        stock_no = 'ATSRDC/' + code + '/'
                    elif case.dc_type=="non_refund_dc":
                        stock_no = 'ATSNRDC/' + code + '/'
                elif case.picking_type_id.code =="incoming":
                    stock_no = 'ATS/GRN/' + code + '/'
                cr.execute("select name from stock_picking where name like '"+stock_no+"'|| '%' order by to_number(substr(name,(length('"+stock_no+"')+1)),'99999') desc limit 1")
                prev_format = cr.fetchone()
                if not prev_format:
                    name = stock_no + '0001'
                else:
                    auto_gen = prev_format[0][-4:]
                    name = stock_no + str(int(auto_gen) + 1).zfill(4)
                self.write(cr, uid, [case.id],{'name':name})
                
        return True    

        

    """Auto Generation of Stock Number when they directly create DC or incomingshipment."""
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        picktpe_obj = self.pool.get("stock.picking.type")
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        dc_type = vals.get('dc_type',False)
        pick_type_id = vals.get('picking_type_id',False)
        pick_type = picktpe_obj.browse(cr, uid,[pick_type_id] )
        if res and dc_type or pick_type.code=='incoming':
            self.generate_seq(cr, uid, [res], context)
        return res
    
    """ Inheriting  Preparing Invoice Vals"""
    
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, origin, context=None):
        if context is None:
            context = {}
        invoice_vals = super(stock_picking,self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, origin, context=context)
        for pick in self.browse(cr, uid, context.get('active_ids', [])):
            if len(context.get('active_ids', [])) == 1:
                invoice_vals.update({
                                     'destination'    : pick.destination or False,
                                     'vehicle_no'     : pick.vehicle_no and pick.vehicle_no or False,
                                     'esugam_no'      : pick.esugam_no and pick.esugam_no or False,
                                    })
                
        return invoice_vals
            
             

