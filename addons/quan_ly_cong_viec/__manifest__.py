# -*- coding: utf-8 -*-
{
    'name': "quan_ly_cong_viec",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'nhan_su', 'quan_ly_du_an'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',
        'views/du_an_view.xml',  # Inherit view từ module quan_ly_du_an
        'views/giai_doan_cong_viec_view.xml',
        'views/cong_viec_view.xml',
        'views/nhat_ky_cong_viec_view.xml',
        'views/tai_nguyen.xml',
        'views/danh_gia_nhan_vien_view.xml',
        'views/nhan_vien.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'icon': '/quan_ly_cong_viec/static/description/image.png',
    
    'assets': {
        'web.assets_backend': [
            '/quan_ly_cong_viec/static/css/dashboard.css',
        ],
    },
}
