# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Dự án và Công việc',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Quản lý dự án, chia nhỏ tác vụ và theo dõi tiến độ nhân sự',
    'author': 'Đối tác lập trình',
    'depends': ['base', 'nhan_su'],
    'data': [
        'security/ir.model.access.csv',
        'views/du_an_views.xml',
        'views/cong_viec_views.xml',
        'views/menu_views.xml',
        'data/demo_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}