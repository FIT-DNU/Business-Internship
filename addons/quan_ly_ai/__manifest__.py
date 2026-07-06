# -*- coding: utf-8 -*-

{
    "name": "Quản Lý AI",
    "summary": "AI Planning cho Quản lý dự án và công việc",
    "description": """
Module tích hợp AI cục bộ bằng Ollama + Qwen2.5.
- AI sinh danh sách công việc từ thông tin dự án
- Quản lý duyệt trước khi tạo task
- Chạy offline, không cần API key
""",
    "author": "K17",
    "website": "",
    "category": "Project",
    "version": "17.0.1.0",
    "license": "LGPL-3",
    "depends": [
        "base",
        "quan_ly_nhan_su",
        "quan_ly_du_an",
        "quan_ly_cong_viec",
    ],
    "external_dependencies": {
        "python": ["requests"]
    },
    "data": [
        "security/ir.model.access.csv",
        "views/ai_generate_task_wizard.xml",
        "views/du_an_ai_view.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
