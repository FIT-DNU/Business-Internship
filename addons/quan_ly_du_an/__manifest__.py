# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Dự Án",
    'summary': """
        Module quản lý dự án - Kết hợp từ các project N6, N7
    """,
    'description': """
        Module quản lý dự án tích hợp:
        - Quản lý thông tin dự án
        - Quản lý ngân sách và chi phí
        - Quản lý tài nguyên
        - Quản lý giai đoạn công việc
        - Theo dõi tiến độ dự án
    """,
    'author': "CNTT 15-03",
    'website': "http://www.yourcompany.com",
    'category': 'Project',
    'version': '1.0',
    'depends': ['base', 'quan_ly_nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/du_an_view.xml',
        'views/budgets_view.xml',
        'views/expenses_view.xml',
        'views/tai_nguyen_view.xml',
        'views/giai_doan_cong_viec_view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}





