# -*- coding: utf-8 -*-
{
    'name': "Quản lý dự án",

    'summary': """
        Module quản lý dự án, theo dõi tiến độ, ngân sách và phân công nhân viên""",

    'description': """
        Module Quản lý dự án:
        - Quản lý thông tin dự án
        - Phân công nhân viên vào dự án
        - Theo dõi tiến độ và ngân sách
        - Tích hợp với module Quản lý nhân sự và Quản lý công việc
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'nhan_su'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/du_an.xml',
        'views/nhan_vien.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
