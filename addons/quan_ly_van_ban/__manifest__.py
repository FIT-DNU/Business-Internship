# -*- coding: utf-8 -*-
{
    'name': "quan_ly_van_ban",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "FIT-DNU",
    'website': "https://ttdn1501.aiotlabdnu.xyz/web",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'nhan_su'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/van_ban_den.xml',
        'views/van_ban_di.xml',
        'views/loai_van_ban.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
