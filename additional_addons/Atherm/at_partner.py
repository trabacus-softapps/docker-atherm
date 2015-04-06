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
from openerp.osv.expression import get_unaccent_wrapper

class res_partner(osv.Model):
    _inherit = "res.partner"
    
    ecc_no      =   fields.Char(string="ECC NO")
    tin_no      =   fields.Char(string="TIN NO")