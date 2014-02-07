# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################
{
    "name": "Account Streamline",
    "version": "1.5",
    "author": "XCG Consulting",
    "category": 'Accounting',
    "description": """Enhancements to the account module to streamline its
    usage.
    """,
    'website': 'http://www.openerp-experts.com',
    'init_xml': [],
    "depends": [
        'base',
        'account_accountant',
        'account_voucher',
        'account_payment',
        'account_sequence',
        'mail',
        'analytic_structure',
        'advanced_filter',
        'report_webkit',
    ],
    "data": [
        'data/partner_data.xml',
        'wizards/account_reconcile_view.xml',
        'wizards/email_remittance.xml',
        'views/account_move_line_search_unreconciled.xml',
        'views/account_move_line_tree.xml',
        'views/account_move_view.xml',
        'views/account_view.xml',
        'views/account_voucher.xml',
        'views/partner_view.xml',
        'views/payment_selection.xml',
        'views/payment_suggestion.xml',
        'views/account_move_line_journal_items.xml',
        'views/account_move_line_journal_view.xml',
        'views/account_menu_entries.xml',
        'views/res_company.xml',
        'data/voucher_report_header.xml',
        'report/payment_suggestion.xml',
        'report/remittance_letter.xml',
        'data/remittance_letter_email_template.xml',
        'security/ir.model.access.csv',
    ],
    #'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
