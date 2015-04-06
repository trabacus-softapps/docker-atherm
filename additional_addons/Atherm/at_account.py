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
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class account_invoice(models.Model):
    _inherit = "account.invoice"
   
    @api.multi
    @api.depends('amount_total','invoice_line','invoice_line.price_unit','invoice_line.invoice_line_tax_id',
                 'invoice_line.quantity','invoice_line.discount','invoice_line.invoice_id')
    def _get_amount_words(self):
       """
           Convert Amount to words
       """   
       res = {} 
       for case in self:
           frac, whole = math.modf(case.amount_total)
           currency = case.journal_id.currency or case.journal_id.company_id.currency_id
           whole_word = frac_word = ''
           
           CurrName = (currency.number_name or '')
           DeciName = (currency.decimal_name or '')
           
           if currency.name.upper() == 'INR':
               self._cr.execute("select amount2words_indian(%d)"%int(whole))
               whole_word = self._cr.fetchone()
               
               if frac:
                   self._cr.execute("select amount2words_indian(%d)"%(frac * 100))
                   frac_word = self._cr.fetchone()
                   frac_word = (frac_word and frac_word[0] or '')
                   frac_word = ' and ' + frac_word + ' ' + DeciName
               
               whole_word = CurrName + ' ' + (whole_word and whole_word[0] or '')
               
           else:
               self._cr.execute("select amount2words_english(%d)"%int(whole))
               whole_word = self._cr.fetchone()
           
               if frac:    
                   cr.execute("select amount2words_english(%d)"%(frac * 100))
                   frac_word = self._cr.fetchone()
                   frac_word = (frac_word and frac_word[0] or '')
                   frac_word += ' ' + DeciName 
           
               whole_word = (whole_word and whole_word[0] or '') + ' ' + CurrName
               
           if frac:
               self.amount_in_words = whole_word + ' ' + 'and' + ' ' + frac_word + ' ' +'Only.'
           else:
               self.amount_in_words = whole_word + ' ' + frac_word + ' ' +'Only.'     
                     
           
    
    
    destination    =    fields.Char(string='Destination')
    vehicle_no     =    fields.Char(string='Vehicle No')
    esugam_no      =    fields.Char(string='E-sugam No')
    are3_no        =    fields.Char(string='ARE-3 No')   
    are3_date      =    fields.Date(string='ARE-3 Date')
    ct3_no         =    fields.Char(string='CT-3 No')   
    ct3_date       =    fields.Date(string='CT-3 Date')
    adv_author_no  =    fields.Date(string='Advance Authorisation No')
    amount_in_words=    fields.Char(compute='_get_amount_words',string="Amount in Words", store=True)
#                     store={
#                     'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                     'account.invoice.tax': (_get_invoice_tax, None, 20),
#                     'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#                     },)
                        
    
    def action_create_InvNumber(self, cr, uid, ids, context=None):
        """
            Method: called from Workflow
            Sets Invoice Number
        """
        today = time.strftime("%Y-%m-%d")
        cr.execute("select code from account_fiscalyear where date_start <= '" + str(today) + "' and date_stop >='" + str(today) + "'")
        code = cr.fetchone()
        year = code and code[0] or ''
        if not year:
            raise osv.except_osv(_('Warning!'), _('Fiscal Year does not exist'))
        
        for case in self.browse(cr, uid, ids, context):
            updatevals = {}
            InvNum = ''
            
            # allocated number is used for re-validated invoices
            if case.internal_number: 
                InvNum = case.internal_number 
            else:
                # Invoice number if internal number is blank    
                InvNum = (case.type == 'out_refund') and 'ATSCR/' or \
                             (case.type == 'in_refund') and 'ATSSR/' or \
                             (case.type == 'in_invoice') and 'ATSS/' or \
                             (case.type == 'out_invoice') and 'ATSC/' 
                
                InvNum += year + '/'
                
                cr.execute(""" select id from account_invoice where internal_number ilike '""" + str(InvNum) + """%'  and id != """ + str(case.id) + """
                               order by to_number(substr(internal_number,(length('""" + str(InvNum) + """')+1)),'9999999999')
                               desc limit 1""")
                inv_rec = cr.fetchone()
                if inv_rec:
                    inv = self.browse(cr, SUPERUSER_ID, inv_rec[0])
                    auto_gen = inv.internal_number[len(InvNum) : ]
                    InvNum = InvNum + str(int(auto_gen) + 1).zfill(5)
                else:
                    InvNum = InvNum + '00001'
                 
            updatevals = {'internal_number': InvNum, 'number': InvNum}
            self.write(cr, uid, [case.id], updatevals, context) 
                       
        return True


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"
    
    
    cetsh          =    fields.Char(string='CETSH')
    ctn_box        =    fields.Char(string='CTN/BOX')
    
    
    
    
    
    

    