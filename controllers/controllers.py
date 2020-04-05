# -*- coding: utf-8 -*-
from odoo import  _
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale



class WebsiteSalePaymentFilter(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        shipping_partner_id = False
        if order:
            shipping_partner_id = order.partner_shipping_id.id or order.partner_invoice_id.id

        values = dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url= '/shop/payment/validate',
            bootstrap_formatting= True
        )

        domain = expression.AND([
            [('pricelist_ids','=',order.pricelist_id.id)],
            ['&', ('website_published', '=', True), ('company_id', '=', order.company_id.id)],
            ['|', ('specific_countries', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)

        values['access_token'] = order.access_token
        values['form_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 'form' and acq.view_template_id]
        values['s2s_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 's2s' and acq.registration_view_template_id]
        values['tokens'] = request.env['payment.token'].search(
            [('partner_id', '=', order.partner_id.id),
            ('acquirer_id', 'in', acquirers.ids)])

        for acq in values['form_acquirers']:
            acq.form = acq.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                '/',
                order.amount_total,
                order.pricelist_id.currency_id.id,
                values={
                    'return_url': '/shop/payment/validate',
                    'partner_id': shipping_partner_id,
                    'billing_partner_id': order.partner_invoice_id.id,
                }
            )

        return values