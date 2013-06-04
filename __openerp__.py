# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################
{
    "name" : "Account numergy",
    "version" : "0.1",
    "author" : "XCG Consulting",
    "category": 'Accounting',
    "description": """Enhancements to the account module to numergy its
    usage.
    """,
    'website': 'http://www.openerp-experts.com',
    'init_xml': [],
    "depends" : ['base', 'account_accountant', 'account_voucher', 'account_sequence', 'analytic_structure'],
    "data": [
        'data/partner_data.xml',
        'wizards/account_reconcile_view.xml',
        'wizards/account_reconcile_search_view.xml',
        'views/account_move_line_search_unreconciled.xml',
        'views/account_move_line_tree.xml',
        'views/account_move_view.xml',
        'views/account_view.xml',
        'views/partner_view.xml',
        'views/payment_selection.xml',
        'views/account_move_line_journal_items.xml',
        'views/account_menu_entries.xml'
    ],
    'js': [
        'static/src/js/account_numergy_move_reconcile.js',
    ],
    'qweb' : [
        'static/src/xml/account_numergy_move_reconcile.xml',
    ],
    #'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
