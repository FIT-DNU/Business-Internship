# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Nhân Sự",
    'summary': """
        Module quản lý nhân sự - Kết hợp từ các project N6, N7, N9
    """,
    'description': """
        Module quản lý nhân sự tích hợp:
        - Quản lý thông tin nhân viên
        - Quản lý chức vụ
        - Quản lý phòng ban
        - Quản lý nhóm dự án
        - Lịch sử làm việc
    """,
    'author': "CNTT 15-03",
    'website': "http://www.yourcompany.com",
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/chuc_vu.xml',
        'views/phong_ban.xml',
        'views/nhom_du_an.xml',
        'views/nhan_vien.xml',
        'views/lich_su_lam_viec.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}




