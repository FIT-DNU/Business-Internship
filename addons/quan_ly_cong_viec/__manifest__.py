# -*- coding: utf-8 -*-
{
    'name': "Quản Lý Công Việc",
    'summary': """
        Module quản lý công việc - Kết hợp từ các project N6, N7
    """,
    'description': """
        Module quản lý công việc tích hợp:
        - Quản lý công việc trong dự án
        - Nhật ký công việc
        - Đánh giá nhân viên
        - Theo dõi tiến độ công việc
        - Quản lý mức độ ưu tiên
    """,
    'author': "CNTT 15-03",
    'website': "http://www.yourcompany.com",
    'category': 'Project',
    'version': '1.0',
    'depends': ['base', 'quan_ly_nhan_su', 'quan_ly_du_an'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/thong_bao_noi_bo_view.xml',
        'views/cong_viec_view.xml',
        'views/nhat_ky_cong_viec_view.xml',
        'views/danh_gia_nhan_vien_view.xml',
        'views/du_an_view_extend.xml',
        'views/nhan_vien_view_extend.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}


