# -*- coding: utf-8 -*-
from odoo import  fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    pricelist_ids = fields.Many2many(
        'product.pricelist',
        string='For pricelist',
        help = 'Visible for sale orders with pricelist'
    )
