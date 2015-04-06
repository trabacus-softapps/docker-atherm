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


class purchase_order(osv.osv):
    _inherit='purchase.order'
    
    
    """
       Overriden
    """ 
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    """
           Convert Amount to words
    """   
    def _get_amount_words(self, cr, uid, ids, name, args, context=None):

       res = {} 
       
       for case in self.browse(cr, uid, ids, context):
           frac, whole = math.modf(case.amount_total)
           currency = case.journal_id.currency or case.journal_id.company_id.currency_id
           whole_word = frac_word = ''
           
           CurrName = (currency.number_name or '')
           DeciName = (currency.decimal_name or '')
           
           if currency.name.upper() == 'INR':
               cr.execute("select amount2words_indian(%d)"%int(whole))
               whole_word = cr.fetchone()
               
               if frac:
                   cr.execute("select amount2words_indian(%d)"%(frac * 100))
                   frac_word = cr.fetchone()
                   frac_word = (frac_word and frac_word[0] or '')
                   frac_word = ' and ' + frac_word + ' ' + DeciName
               
               whole_word = CurrName + ' ' + (whole_word and whole_word[0] or '')
               
           else:
               cr.execute("select amount2words_english(%d)"%int(whole))
               whole_word = cr.fetchone()
           
               if frac:    
                   cr.execute("select amount2words_english(%d)"%(frac * 100))
                   frac_word = cr.fetchone()
                   frac_word = (frac_word and frac_word[0] or '')
                   frac_word += ' ' + DeciName 
           
               whole_word = (whole_word and whole_word[0] or '') + ' ' + CurrName
               
           
           res[case.id] = whole_word + ' ' + frac_word
       return res
   
    
    
    
    
    _columns={
              'dc_type'         :   fields.selection([('refund_dc', 'Refundable DC'), ('non_refund_dc', 'Non Refundable DC')],
                                                  'Deliver Challan Type',track_visibility='onchange'),
              'contact_id'      :   fields.many2one('res.partner','Contact Person'),
              
              'amount_in_words' :   fields.function(_get_amount_words, method=True, string="Amount in Words", type="text",
                                    store={
                                    'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
                                    'purchase.order.line': (_get_order, ['order_id'], 20), # To Update the Lines Changes.
                                    } ),
              
              }
    _defaults = {
                'dc_type'   :   'non_refund_dc',         
                 }
    
    
    """
           On change of partner pop contact person
    """  
    def onchange_partner_id(self, cr, uid, ids,partner_id, context=None):
        if not context:
            context={}
        partner_obj = self.pool.get("res.partner")
        partner_vals = super(purchase_order,self).onchange_partner_id(cr, uid, ids, partner_id, context=context)
        if partner_id:
            partner = partner_obj.browse(cr, uid, partner_id)
            cont = partner_obj.search(cr, uid, [('parent_id','=',partner_id)], limit=1)
            partner_vals['value'].update({
                                          'contact_id' : cont and cont[0] or False, 
                                        })
        return partner_vals
    
    
    """
           Auto generation of PO NO
    """ 
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
            pur_no = 'ATSPO/' + code + '/'
            cr.execute("select name from purchase_order where name like '"+pur_no+"'|| '%' order by to_number(substr(name,(length('"+pur_no+"')+1)),'99999') desc limit 1")
            prev_format = cr.fetchone()
            if not prev_format:
                name = pur_no + '0001'
            else:
                auto_gen = prev_format[0][-4:]
                name = pur_no + str(int(auto_gen) + 1).zfill(4)
            vals.update({'name':name})
        return super(purchase_order, self).create(cr, uid, vals, context=context)
    
