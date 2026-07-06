# -*- coding: utf-8 -*-

SYSTEM_PROMPT = """
Bạn là chuyên gia quản lý dự án phần mềm trong doanh nghiệp.

Luôn trả lời bằng tiếng Việt.

Nhiệm vụ:
Từ thông tin dự án, hãy đề xuất danh sách công việc cần làm.

Yêu cầu bắt buộc:
- Chỉ trả về JSON hợp lệ.
- Không markdown.
- Không giải thích.
- Không thêm chữ nào ngoài JSON.
- JSON phải là một mảng.
- Mỗi phần tử có đúng các khóa:
  title, description, priority, estimated_days.

priority chỉ được là một trong:
low, medium, high.

Ví dụ định dạng:
[
  {
    "title": "Phân tích yêu cầu",
    "description": "Thu thập và phân tích yêu cầu nghiệp vụ của dự án.",
    "priority": "high",
    "estimated_days": 2
  }
]
"""


def build_generate_tasks_prompt(project):
    project_members = ", ".join(project.nhan_vien_ids.mapped("display_name")) or "Chưa có nhân viên"

    return f"""
Thông tin dự án:

Tên dự án:
{project.ten_du_an or ""}

Mô tả dự án:
{project.mo_ta or ""}

Ngày bắt đầu:
{project.ngay_bat_dau or ""}

Ngày kết thúc dự kiến:
{project.ngay_ket_thuc_du_kien or ""}

Người phụ trách:
{project.nguoi_phu_trach_id.display_name if project.nguoi_phu_trach_id else "Chưa có"}

Nhân viên tham gia:
{project_members}

Hãy sinh từ 8 đến 12 công việc phù hợp cho dự án này.
Các công việc phải thực tế, có trình tự hợp lý, phù hợp với quản lý dự án phần mềm.
"""
