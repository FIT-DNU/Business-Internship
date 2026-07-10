# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from pathlib import Path
import json

from odoo import http, fields
from odoo.http import request


class FitFrontendController(http.Controller):

    def _selection_label(self, record, field_name, value):
        if not value:
            return ""
        try:
            return dict(record._fields[field_name].selection).get(value, value)
        except Exception:
            return value

    def _task_to_dict(self, task):
        employees = []
        for emp in task.nhan_vien_ids[:4]:
            name = emp.ho_va_ten or emp.display_name or ""
            employees.append({
                "id": emp.id,
                "name": name,
                "initial": name[:1].upper() if name else "?",
            })

        return {
            "id": task.id,
            "code": task.ma_cong_viec or "",
            "name": task.ten_cong_viec or "",
            "description": task.mo_ta or "",
            "project_id": task.du_an_id.id or False,
            "project": task.du_an_id.ten_du_an or "",
            "responsible_id": task.nguoi_phu_trach_id.id or False,
            "responsible": task.nguoi_phu_trach_id.ho_va_ten or "",
            "stage": task.giai_doan_id.ten_giai_doan or "",
            "priority": task.priority or "",
            "priority_label": self._selection_label(task, "priority", task.priority),
            "status": task.status or "",
            "status_label": self._selection_label(task, "status", task.status),
            "progress": int(task.phan_tram_cong_viec or 0),
            "deadline": task.han_chot.strftime("%d/%m/%Y %H:%M") if task.han_chot else "",
            "employees": employees,
            "extra_employee_count": max(len(task.nhan_vien_ids) - len(employees), 0),
        }

    def _work_log_to_dict(self, log):
        return {
            "id": log.id,
            "name": log.ten_nhat_ky or "",
            "task_id": log.cong_viec_id.id or False,
            "task": log.cong_viec_id.ten_cong_viec or "",
            "project": log.du_an_id.ten_du_an or "",
            "stage": log.giai_doan_id.ten_giai_doan or "",
            "employees": ", ".join(log.nhan_vien_ids.mapped("ho_va_ten")),
            "date": log.ngay_thuc_hien.strftime("%d/%m/%Y %H:%M") if log.ngay_thuc_hien else "",
            "progress": float(log.muc_do or 0),
            "state": log.trang_thai or "",
            "state_label": self._selection_label(log, "trang_thai", log.trang_thai),
            "description": log.mo_ta or "",
        }

    def _evaluation_to_dict(self, item):
        return {
            "id": item.id,
            "name": item.ten_danh_gia or "",
            "employee_id": item.nhan_vien_id.id or False,
            "employee": item.nhan_vien_id.ho_va_ten or item.nhan_vien_id.display_name or "",
            "task_id": item.cong_viec_id.id or False,
            "task": item.cong_viec_id.ten_cong_viec or "",
            "project_id": item.du_an_id.id or False,
            "project": item.du_an_id.ten_du_an or "",
            "score": item.diem_so or "",
            "comment": item.nhan_xet or "",
            "date": item.ngay_danh_gia.strftime("%d/%m/%Y %H:%M") if item.ngay_danh_gia else "",
        }

    def _project_to_dict(self, p):
        return {
            "id": p.id,
            "code": p.ma_du_an or "",
            "name": p.ten_du_an or "",
            "description": p.mo_ta or "",
            "responsible_id": p.nguoi_phu_trach_id.id or False,
            "responsible": p.nguoi_phu_trach_id.ho_va_ten or "",
            "employee_count": len(p.nhan_vien_ids),
            "employee_names": ", ".join(p.nhan_vien_ids.mapped("ho_va_ten")),
            "start_date": p.ngay_bat_dau.strftime("%d/%m/%Y") if p.ngay_bat_dau else "",
            "expected_end": p.ngay_ket_thuc_du_kien.strftime("%d/%m/%Y") if p.ngay_ket_thuc_du_kien else "",
            "actual_end": p.ngay_ket_thuc_thuc_te.strftime("%d/%m/%Y") if p.ngay_ket_thuc_thuc_te else "",
            "status": p.tien_do_du_an or "",
            "status_label": self._selection_label(p, "tien_do_du_an", p.tien_do_du_an),
            "progress": round(float(p.phan_tram_du_an or 0), 2),
        }

    def _stage_to_dict(self, s):
        return {
            "id": s.id,
            "name": s.ten_giai_doan or "",
            "order": s.thu_tu or 0,
            "description": s.mo_ta or "",
            "project_id": s.du_an_id.id or False,
            "project": s.du_an_id.ten_du_an or "",
        }

    def _budget_to_dict(self, b):
        return {
            "id": b.id,
            "code": b.budgets_id or "",
            "name": b.budgets_name or "",
            "project_id": b.du_an_id.id or False,
            "project": b.du_an_id.ten_du_an or "",
            "planned": float(b.budget_planned or 0),
            "allocated": float(b.budget_allocated or 0),
            "reserved": float(b.budget_reserved or 0),
            "spent": float(b.budget_spent or 0),
            "difference": float(b.budget_difference or 0),
        }

    def _expense_to_dict(self, e):
        return {
            "id": e.id,
            "name": e.expenses_name or "",
            "task": e.cong_viec_id.ten_cong_viec or "",
            "budget_id": e.budgets_id.id or False,
            "budget": e.budgets_id.budgets_name or "",
            "project": e.du_an_id.ten_du_an or "",
            "amount": float(e.amount or 0),
            "date": e.date.strftime("%d/%m/%Y") if e.date else "",
            "description": e.mo_ta or "",
            "over_reason": e.ly_do_vuot_ngan_sach or "",
        }

    def _resource_to_dict(self, r):
        return {
            "id": r.id,
            "name": r.ten_tai_nguyen or "",
            "quantity": int(r.so_luong or 0),
            "unit": r.don_vi or "",
            "description": r.mo_ta or "",
            "project_id": r.du_an_id.id or False,
            "project": r.du_an_id.ten_du_an or "",
        }

    def _employee_full_to_dict(self, emp):
        name = emp.ho_va_ten or emp.display_name or ""
        return {
            "id": emp.id,
            "code": emp.ma_dinh_danh or "",
            "name": name,
            "first_part": emp.ho_ten_dem or "",
            "last_name": emp.ten or "",
            "birth": emp.ngay_sinh.strftime("%d/%m/%Y") if emp.ngay_sinh else "",
            "gender": emp.gioi_tinh or "",
            "gender_label": self._selection_label(emp, "gioi_tinh", emp.gioi_tinh),
            "hometown": emp.que_quan or "",
            "email": emp.email or "",
            "phone": emp.so_dien_thoai or "",
            "position_id": emp.chuc_vu_id.id or False,
            "position": emp.chuc_vu_id.ten_chuc_vu or "",
            "department_id": emp.phong_ban_id.id or False,
            "department": emp.phong_ban_id.ten_phong_ban or "",
            "team_names": ", ".join(emp.nhom_du_an_ids.mapped("ten_nhom")),
            "initial": name[:1].upper() if name else "?",
        }

    def _position_to_dict(self, item):
        return {
            "id": item.id,
            "code": item.ma_chuc_vu or "",
            "name": item.ten_chuc_vu or "",
            "description": item.mo_ta or "",
            "employee_count": len(item.nhan_vien_ids),
        }

    def _department_to_dict(self, item):
        return {
            "id": item.id,
            "code": item.ma_phong_ban or "",
            "name": item.ten_phong_ban or "",
            "description": item.mo_ta or "",
            "employee_count": len(item.nhan_vien_ids),
        }

    def _team_to_dict(self, item):
        return {
            "id": item.id,
            "name": item.ten_nhom or "",
            "description": item.mo_ta or "",
            "employee_count": len(item.nhan_vien_ids),
            "employees": ", ".join(item.nhan_vien_ids.mapped("ho_va_ten")),
        }

    def _work_history_to_dict(self, item):
        return {
            "id": item.id,
            "name": item.ten_cong_viec or "",
            "employee_id": item.nhan_vien_id.id or False,
            "employee": item.nhan_vien_id.ho_va_ten or "",
            "position": item.chuc_vu_id.ten_chuc_vu or "",
            "department": item.phong_ban_id.ten_phong_ban or "",
            "start": item.ngay_bat_dau.strftime("%d/%m/%Y") if item.ngay_bat_dau else "",
            "end": item.ngay_ket_thuc.strftime("%d/%m/%Y") if item.ngay_ket_thuc else "",
            "description": item.mo_ta or "",
        }

    def _bootstrap_data(self):
        Task = request.env["cong_viec"].sudo()
        Project = request.env["du_an"].sudo()
        Employee = request.env["nhan_vien"].sudo()
        WorkLog = request.env["nhat_ky_cong_viec"].sudo()
        Evaluation = request.env["danh_gia_nhan_vien"].sudo()
        Stage = request.env["giai_doan_cong_viec"].sudo()
        Budget = request.env["budgets"].sudo()
        Expense = request.env["expenses"].sudo()
        Resource = request.env["tai_nguyen"].sudo()
        Position = request.env["chuc_vu"].sudo()
        Department = request.env["phong_ban"].sudo()
        Team = request.env["nhom_du_an"].sudo()
        WorkHistory = request.env["lich_su_lam_viec"].sudo()

        status_order = [
            ("delayed", "Trì hoãn"),
            ("in_progress", "Đang thực hiện"),
            ("not_started", "Chưa bắt đầu"),
            ("completed", "Hoàn thành"),
        ]

        total = Task.search_count([])
        in_progress = Task.search_count([("status", "=", "in_progress")])
        not_started = Task.search_count([("status", "=", "not_started")])
        completed = Task.search_count([("status", "=", "completed")])
        delayed = Task.search_count([("status", "=", "delayed")])

        def percent(value):
            return round(value * 100 / total, 1) if total else 0

        columns = []
        for status, label in status_order:
            tasks = Task.search(
                [("status", "=", status)],
                order="han_chot asc, id desc",
                limit=30,
            )
            columns.append({
                "status": status,
                "label": label,
                "count": Task.search_count([("status", "=", status)]),
                "tasks": [self._task_to_dict(task) for task in tasks],
            })

        all_tasks = Task.search([], order="id desc", limit=200)
        projects = Project.search([], order="id desc")
        employees = Employee.search([], order="id desc")

        project_items = []
        for p in projects:
            project_items.append({
                "id": p.id,
                "code": p.ma_du_an or "",
                "name": p.ten_du_an or "",
                "status": p.tien_do_du_an or "",
                "progress": int(p.phan_tram_du_an or 0),
                "employee_ids": p.nhan_vien_ids.ids,
                "responsible_id": p.nguoi_phu_trach_id.id or False,
            })

        employee_items = []
        for emp in employees:
            name = emp.ho_va_ten or emp.display_name or ""
            employee_items.append({
                "id": emp.id,
                "name": name,
                "email": emp.email or "",
                "phone": emp.so_dien_thoai or "",
                "position": emp.chuc_vu_id.display_name or "",
                "department": emp.phong_ban_id.display_name or "",
                "initial": name[:1].upper() if name else "?",
            })

        upcoming_tasks = Task.search(
            [("han_chot", "!=", False), ("status", "not in", ["completed", "cancelled"])],
            order="han_chot asc",
            limit=8,
        )

        work_logs = WorkLog.search([], order="ngay_thuc_hien desc, id desc", limit=200)
        evaluations = Evaluation.search([], order="ngay_danh_gia desc, id desc", limit=200)

        return {
            "user": {
                "name": request.env.user.name,
            },
            "today": fields.Date.context_today(request.env.user).strftime("%d/%m/%Y"),
            "work": {
                "stats": {
                    "total": total,
                    "in_progress": in_progress,
                    "not_started": not_started,
                    "completed": completed,
                    "delayed": delayed,
                    "logs": WorkLog.search_count([]),
                    "evaluations": Evaluation.search_count([]),
                    "projects": Project.search_count([]),
                    "employees": Employee.search_count([]),
                    "in_progress_percent": percent(in_progress),
                    "not_started_percent": percent(not_started),
                    "completed_percent": percent(completed),
                    "delayed_percent": percent(delayed),
                },
                "columns": columns,
                "tasks": [self._task_to_dict(task) for task in all_tasks],
                "upcoming_tasks": [self._task_to_dict(task) for task in upcoming_tasks],
                "logs": [self._work_log_to_dict(log) for log in work_logs],
                "evaluations": [self._evaluation_to_dict(item) for item in evaluations],
            },
            "hr": {
                "stats": {
                    "employees": Employee.search_count([]),
                    "positions": Position.search_count([]),
                    "departments": Department.search_count([]),
                    "teams": Team.search_count([]),
                    "histories": WorkHistory.search_count([]),
                    "male": Employee.search_count([("gioi_tinh", "=", "nam")]),
                    "female": Employee.search_count([("gioi_tinh", "=", "nu")]),
                },
                "employees": [self._employee_full_to_dict(e) for e in Employee.search([], order="id desc", limit=300)],
                "positions": [self._position_to_dict(p) for p in Position.search([], order="id desc", limit=200)],
                "departments": [self._department_to_dict(d) for d in Department.search([], order="id desc", limit=200)],
                "teams": [self._team_to_dict(t) for t in Team.search([], order="id desc", limit=200)],
                "histories": [self._work_history_to_dict(h) for h in WorkHistory.search([], order="id desc", limit=300)],
            },
            "project": {
                "stats": {
                    "total": Project.search_count([]),
                    "not_started": Project.search_count([("tien_do_du_an", "=", "chua_bat_dau")]),
                    "in_progress": Project.search_count([("tien_do_du_an", "=", "dang_thuc_hien")]),
                    "completed": Project.search_count([("tien_do_du_an", "=", "hoan_thanh")]),
                    "paused": Project.search_count([("tien_do_du_an", "=", "tam_dung")]),
                    "cancelled": Project.search_count([("tien_do_du_an", "=", "huy_bo")]),
                    "stages": Stage.search_count([]),
                    "budgets": Budget.search_count([]),
                    "expenses": Expense.search_count([]),
                    "resources": Resource.search_count([]),
                    "total_budget": sum(Budget.search([]).mapped("budget_planned")),
                    "total_spent": sum(Expense.search([]).mapped("amount")),
                },
                "projects": [self._project_to_dict(p) for p in Project.search([], order="id desc", limit=200)],
                "stages": [self._stage_to_dict(s) for s in Stage.search([], order="du_an_id, thu_tu, id", limit=300)],
                "budgets": [self._budget_to_dict(b) for b in Budget.search([], order="id desc", limit=300)],
                "expenses": [self._expense_to_dict(e) for e in Expense.search([], order="date desc, id desc", limit=300)],
                "resources": [self._resource_to_dict(r) for r in Resource.search([], order="id desc", limit=300)],
            },
            "projects": project_items,
            "employees": employee_items,
        }

    @http.route("/fit", type="http", auth="user")
    def fit_app(self):
        base_dir = Path(__file__).resolve().parents[1]

        css_path = base_dir / "static" / "src" / "css" / "fit_frontend.css"
        js_path = base_dir / "static" / "src" / "js" / "fit_frontend.js"

        css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8"/>
    <title>FIT Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <style>
__FIT_CSS__
    </style>
</head>
<body>
    <div id="fit-root">
        <div class="fit-loading-screen">Đang tải giao diện...</div>
    </div>

    <script>
__FIT_JS__
    </script>
</body>
</html>"""

        html = html.replace("__FIT_CSS__", css)
        html = html.replace("__FIT_JS__", js)

        return request.make_response(
            html,
            headers=[("Content-Type", "text/html; charset=utf-8")]
        )

    @http.route("/fit/api/bootstrap", type="json", auth="user")
    def api_bootstrap(self):
        return self._bootstrap_data()

    @http.route("/fit/api/project/create", type="json", auth="user")
    def api_project_create(self, **params):
        Project = request.env["du_an"].sudo()
        Employee = request.env["nhan_vien"].sudo()

        name = (params.get("name") or "").strip()
        code = (params.get("code") or "").strip() or "FE-DA-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        responsible_id = int(params.get("responsible_id") or 0)
        description = params.get("description") or ""

        if not name:
            return {"ok": False, "error": "Tên dự án không được để trống."}

        vals = {
            "ma_du_an": code,
            "ten_du_an": name,
            "mo_ta": description,
            "tien_do_du_an": "chua_bat_dau",
        }

        if responsible_id:
            employee = Employee.browse(responsible_id).exists()
            if not employee:
                return {"ok": False, "error": "Người phụ trách không hợp lệ."}
            vals["nguoi_phu_trach_id"] = employee.id
            vals["nhan_vien_ids"] = [(6, 0, [employee.id])]

        try:
            project = Project.create(vals)
            return {"ok": True, "project": self._project_to_dict(project)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/project/status", type="json", auth="user")
    def api_project_status(self, **params):
        Project = request.env["du_an"].sudo()

        project_id = int(params.get("project_id") or 0)
        status = params.get("status")

        allowed = ["chua_bat_dau", "dang_thuc_hien", "hoan_thanh", "tam_dung", "huy_bo"]
        if status not in allowed:
            return {"ok": False, "error": "Trạng thái dự án không hợp lệ."}

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Không tìm thấy dự án."}

        try:
            project.write({"tien_do_du_an": status})
            return {"ok": True, "project": self._project_to_dict(project)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/stage/create", type="json", auth="user")
    def api_stage_create(self, **params):
        Project = request.env["du_an"].sudo()
        Stage = request.env["giai_doan_cong_viec"].sudo()

        project_id = int(params.get("project_id") or 0)
        name = (params.get("name") or "").strip()
        order = int(params.get("order") or 1)
        description = params.get("description") or ""

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}
        if not name:
            return {"ok": False, "error": "Tên giai đoạn không được để trống."}

        try:
            stage = Stage.create({
                "du_an_id": project.id,
                "ten_giai_doan": name,
                "thu_tu": order,
                "mo_ta": description,
            })
            return {"ok": True, "stage": self._stage_to_dict(stage)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/budget/create", type="json", auth="user")
    def api_budget_create(self, **params):
        Project = request.env["du_an"].sudo()
        Budget = request.env["budgets"].sudo()

        project_id = int(params.get("project_id") or 0)
        name = (params.get("name") or "").strip()
        code = (params.get("code") or "").strip() or "FE-BG-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        planned = float(params.get("planned") or 0)
        allocated = float(params.get("allocated") or planned)
        reserved = float(params.get("reserved") or 0)

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}
        if not name:
            return {"ok": False, "error": "Tên ngân sách không được để trống."}

        try:
            budget = Budget.create({
                "du_an_id": project.id,
                "budgets_id": code,
                "budgets_name": name,
                "budget_planned": planned,
                "budget_allocated": allocated,
                "budget_reserved": reserved,
            })
            return {"ok": True, "budget": self._budget_to_dict(budget)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/expense/create", type="json", auth="user")
    def api_expense_create(self, **params):
        Budget = request.env["budgets"].sudo()
        Expense = request.env["expenses"].sudo()

        budget_id = int(params.get("budget_id") or 0)
        name = (params.get("name") or "").strip()
        amount = float(params.get("amount") or 0)
        date_value = params.get("date") or fields.Date.today()
        description = params.get("description") or ""
        over_reason = params.get("over_reason") or ""

        budget = Budget.browse(budget_id).exists()
        if not budget:
            return {"ok": False, "error": "Vui lòng chọn ngân sách hợp lệ."}
        if not name:
            return {"ok": False, "error": "Tên khoản chi không được để trống."}

        vals = {
            "budgets_id": budget.id,
            "expenses_name": name,
            "amount": amount,
            "date": date_value,
            "mo_ta": description,
            "ly_do_vuot_ngan_sach": over_reason,
        }

        try:
            expense = Expense.create(vals)
            return {"ok": True, "expense": self._expense_to_dict(expense)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/resource/create", type="json", auth="user")
    def api_resource_create(self, **params):
        Project = request.env["du_an"].sudo()
        Resource = request.env["tai_nguyen"].sudo()

        project_id = int(params.get("project_id") or 0)
        name = (params.get("name") or "").strip()
        quantity = int(params.get("quantity") or 1)
        unit = params.get("unit") or "cái"
        description = params.get("description") or ""

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}
        if not name:
            return {"ok": False, "error": "Tên tài nguyên không được để trống."}

        try:
            resource = Resource.create({
                "du_an_id": project.id,
                "ten_tai_nguyen": name,
                "so_luong": quantity,
                "don_vi": unit,
                "mo_ta": description,
            })
            return {"ok": True, "resource": self._resource_to_dict(resource)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _fit_ai_call_suggestions(self, project, note=""):
        try:
            import requests
        except Exception:
            return {
                "ok": False,
                "error": "Thiếu thư viện requests trong môi trường Python.",
            }

        prompt = f"""
Bạn là trợ lý quản lý dự án phần mềm.
Hãy gợi ý danh sách 5-8 công việc cho dự án sau.

Tên dự án: {project.ten_du_an}
Mô tả dự án: {project.mo_ta or ''}
Ghi chú thêm: {note}

Chỉ trả về JSON array, không giải thích ngoài JSON.
Mỗi item có dạng:
{{
  "title": "Tên công việc",
  "priority": "low|medium|high",
  "estimated_days": 3,
  "description": "Mô tả ngắn"
}}
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:1.5b",
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
        except Exception as e:
            return {
                "ok": False,
                "error": "Không gọi được Ollama. Hãy chạy terminal riêng: ollama serve. Chi tiết: %s" % str(e),
            }

        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            items = json.loads(raw[start:end])
        except Exception:
            return {
                "ok": False,
                "error": "AI trả về không đúng JSON. Xem phản hồi thô trong console.",
                "raw": raw,
            }

        suggestions = []
        default_employee = project.nguoi_phu_trach_id

        for index, item in enumerate(items[:10], start=1):
            title = (item.get("title") or "").strip()
            if not title:
                continue

            priority = item.get("priority") or "medium"
            if priority not in ["low", "medium", "high"]:
                priority = "medium"

            try:
                estimated_days = int(item.get("estimated_days") or 3)
            except Exception:
                estimated_days = 3

            suggestions.append({
                "temp_id": index,
                "title": title,
                "priority": priority,
                "estimated_days": estimated_days,
                "employee_id": default_employee.id if default_employee else False,
                "employee_name": default_employee.ho_va_ten if default_employee else "",
                "description": item.get("description") or "",
            })

        return {
            "ok": True,
            "raw": raw,
            "suggestions": suggestions,
        }

    @http.route("/fit/api/ai/suggest-tasks", type="json", auth="user")
    def api_ai_suggest_tasks(self, **params):
        Project = request.env["du_an"].sudo()

        project_id = int(params.get("project_id") or 0)
        note = params.get("note") or ""

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}

        return self._fit_ai_call_suggestions(project, note)

    @http.route("/fit/api/ai/create-suggested-tasks", type="json", auth="user")
    def api_ai_create_suggested_tasks(self, **params):
        Task = request.env["cong_viec"].sudo()
        Project = request.env["du_an"].sudo()
        Employee = request.env["nhan_vien"].sudo()

        project_id = int(params.get("project_id") or 0)
        items = params.get("items") or []

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}

        if not items:
            return {"ok": False, "error": "Chưa có công việc nào được chọn để tạo."}

        created = []

        for index, item in enumerate(items[:30], start=1):
            title = (item.get("title") or "").strip()
            if not title:
                continue

            priority = item.get("priority") or "medium"
            if priority not in ["low", "medium", "high"]:
                priority = "medium"

            try:
                estimated_days = int(item.get("estimated_days") or 0)
            except Exception:
                estimated_days = 0

            vals = {
                "ma_cong_viec": "AI-%s-%02d" % (datetime.now().strftime("%Y%m%d%H%M%S"), index),
                "ten_cong_viec": title,
                "du_an_id": project.id,
                "priority": priority,
                "status": "not_started",
                "mo_ta": item.get("description") or "",
            }

            if estimated_days > 0:
                vals["han_chot"] = fields.Datetime.to_string(datetime.now() + timedelta(days=estimated_days))

            employee_id = int(item.get("employee_id") or 0)
            employee = Employee.browse(employee_id).exists() if employee_id else project.nguoi_phu_trach_id

            if employee:
                vals["nguoi_phu_trach_id"] = employee.id
                vals["nhan_vien_ids"] = [(6, 0, [employee.id])]

            task = Task.create(vals)
            created.append(self._task_to_dict(task))

        return {
            "ok": True,
            "created_count": len(created),
            "tasks": created,
        }

    @http.route("/fit/api/ai/generate-tasks", type="json", auth="user")
    def api_ai_generate_tasks(self, **params):
        Task = request.env["cong_viec"].sudo()
        Project = request.env["du_an"].sudo()

        project_id = int(params.get("project_id") or 0)
        note = params.get("note") or ""

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}

        try:
            import requests
        except Exception:
            return {"ok": False, "error": "Thiếu thư viện requests trong môi trường Python."}

        prompt = f"""
Bạn là trợ lý quản lý dự án phần mềm.
Hãy sinh danh sách 5-8 công việc cho dự án sau.

Tên dự án: {project.ten_du_an}
Mô tả dự án: {project.mo_ta or ''}
Ghi chú thêm: {note}

Chỉ trả về JSON array, không giải thích ngoài JSON.
Mỗi item có dạng:
{{
  "title": "Tên công việc",
  "priority": "low|medium|high",
  "estimated_days": 3,
  "description": "Mô tả ngắn"
}}
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:1.5b",
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
        except Exception as e:
            return {
                "ok": False,
                "error": "Không gọi được Ollama. Hãy chạy terminal riêng: ollama serve. Chi tiết: %s" % str(e),
            }

        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            items = json.loads(raw[start:end])
        except Exception:
            return {
                "ok": False,
                "error": "AI trả về không đúng JSON. Xem phản hồi thô.",
                "raw": raw,
            }

        created = []
        for index, item in enumerate(items[:10], start=1):
            title = (item.get("title") or "").strip()
            if not title:
                continue

            priority = item.get("priority") or "medium"
            if priority not in ["low", "medium", "high"]:
                priority = "medium"

            vals = {
                "ma_cong_viec": "AI-%s-%02d" % (datetime.now().strftime("%Y%m%d%H%M%S"), index),
                "ten_cong_viec": title,
                "du_an_id": project.id,
                "priority": priority,
                "status": "not_started",
                "mo_ta": item.get("description") or "",
            }

            days = int(item.get("estimated_days") or 0)
            if days > 0:
                vals["han_chot"] = fields.Datetime.to_string(datetime.now() + timedelta(days=days))

            if project.nguoi_phu_trach_id:
                vals["nguoi_phu_trach_id"] = project.nguoi_phu_trach_id.id
                vals["nhan_vien_ids"] = [(6, 0, [project.nguoi_phu_trach_id.id])]

            task = Task.create(vals)
            created.append(self._task_to_dict(task))

        return {
            "ok": True,
            "created_count": len(created),
            "tasks": created,
            "raw": raw,
        }

    @http.route("/fit/api/hr/employee/create", type="json", auth="user")
    def api_hr_employee_create(self, **params):
        Employee = request.env["nhan_vien"].sudo()

        code = (params.get("code") or "").strip() or "FE-NV-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        first_part = (params.get("first_part") or "").strip()
        last_name = (params.get("last_name") or "").strip()
        email = (params.get("email") or "").strip()
        phone = (params.get("phone") or "").strip()
        gender = params.get("gender") or False
        position_id = int(params.get("position_id") or 0)
        department_id = int(params.get("department_id") or 0)

        if not first_part or not last_name:
            return {"ok": False, "error": "Vui lòng nhập họ tên đệm và tên."}

        vals = {
            "ma_dinh_danh": code,
            "ho_ten_dem": first_part,
            "ten": last_name,
            "email": email,
            "so_dien_thoai": phone,
        }

        if gender in ["nam", "nu", "khac"]:
            vals["gioi_tinh"] = gender
        if position_id:
            vals["chuc_vu_id"] = position_id
        if department_id:
            vals["phong_ban_id"] = department_id

        try:
            emp = Employee.create(vals)
            return {"ok": True, "employee": self._employee_full_to_dict(emp)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/hr/position/create", type="json", auth="user")
    def api_hr_position_create(self, **params):
        Position = request.env["chuc_vu"].sudo()

        code = (params.get("code") or "").strip() or "FE-CV-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        name = (params.get("name") or "").strip()
        description = params.get("description") or ""

        if not name:
            return {"ok": False, "error": "Tên chức vụ không được để trống."}

        try:
            item = Position.create({
                "ma_chuc_vu": code,
                "ten_chuc_vu": name,
                "mo_ta": description,
            })
            return {"ok": True, "position": self._position_to_dict(item)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/hr/department/create", type="json", auth="user")
    def api_hr_department_create(self, **params):
        Department = request.env["phong_ban"].sudo()

        code = (params.get("code") or "").strip() or "FE-PB-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
        name = (params.get("name") or "").strip()
        description = params.get("description") or ""

        if not name:
            return {"ok": False, "error": "Tên phòng ban không được để trống."}

        try:
            item = Department.create({
                "ma_phong_ban": code,
                "ten_phong_ban": name,
                "mo_ta": description,
            })
            return {"ok": True, "department": self._department_to_dict(item)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/hr/team/create", type="json", auth="user")
    def api_hr_team_create(self, **params):
        Team = request.env["nhom_du_an"].sudo()

        name = (params.get("name") or "").strip()
        description = params.get("description") or ""

        if not name:
            return {"ok": False, "error": "Tên nhóm dự án không được để trống."}

        try:
            item = Team.create({
                "ten_nhom": name,
                "mo_ta": description,
            })
            return {"ok": True, "team": self._team_to_dict(item)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/hr/history/create", type="json", auth="user")
    def api_hr_history_create(self, **params):
        Employee = request.env["nhan_vien"].sudo()
        WorkHistory = request.env["lich_su_lam_viec"].sudo()

        employee_id = int(params.get("employee_id") or 0)
        name = (params.get("name") or "").strip()
        description = params.get("description") or ""

        employee = Employee.browse(employee_id).exists()
        if not employee:
            return {"ok": False, "error": "Vui lòng chọn nhân viên hợp lệ."}
        if not name:
            return {"ok": False, "error": "Tên công việc đã làm không được để trống."}

        vals = {
            "nhan_vien_id": employee.id,
            "ten_cong_viec": name,
            "mo_ta": description,
        }

        if params.get("start"):
            vals["ngay_bat_dau"] = params.get("start")
        if params.get("end"):
            vals["ngay_ket_thuc"] = params.get("end")

        try:
            item = WorkHistory.create(vals)
            return {"ok": True, "history": self._work_history_to_dict(item)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _fit_normalize_kind(self, params):
        values = params.get("values") or {}
        if not isinstance(values, dict):
            values = {}

        raw_kind = (
            params.get("kind")
            or params.get("record_kind")
            or params.get("model_kind")
            or values.get("_kind")
        )

        kind = str(raw_kind or "").strip().lower()

        aliases = {
            "nhan_vien": "employee",
            "nhân viên": "employee",
            "employee": "employee",

            "chuc_vu": "position",
            "chức vụ": "position",
            "position": "position",

            "phong_ban": "department",
            "phòng ban": "department",
            "department": "department",

            "nhom_du_an": "team",
            "nhóm dự án": "team",
            "team": "team",

            "lich_su_lam_viec": "history",
            "lịch sử làm việc": "history",
            "history": "history",

            "du_an": "project",
            "dự án": "project",
            "project": "project",

            "giai_doan": "stage",
            "giai đoạn": "stage",
            "stage": "stage",

            "ngan_sach": "budget",
            "ngân sách": "budget",
            "budget": "budget",

            "chi_phi": "expense",
            "chi phí": "expense",
            "expense": "expense",

            "tai_nguyen": "resource",
            "tài nguyên": "resource",
            "resource": "resource",

            "cong_viec": "task",
            "công việc": "task",
            "task": "task",

            "nhat_ky_cong_viec": "work_log",
            "nhật ký công việc": "work_log",
            "work_log": "work_log",

            "danh_gia_nhan_vien": "evaluation",
            "đánh giá nhân viên": "evaluation",
            "evaluation": "evaluation",
        }

        return aliases.get(kind, kind)

    def _fit_record_config(self, kind):
        mapping = {
            "task": ("cong_viec", self._task_to_dict),
            "work_log": ("nhat_ky_cong_viec", self._work_log_to_dict),
            "evaluation": ("danh_gia_nhan_vien", self._evaluation_to_dict),

            "project": ("du_an", self._project_to_dict),
            "stage": ("giai_doan_cong_viec", self._stage_to_dict),
            "budget": ("budgets", self._budget_to_dict),
            "expense": ("expenses", self._expense_to_dict),
            "resource": ("tai_nguyen", self._resource_to_dict),

            "employee": ("nhan_vien", self._employee_full_to_dict),
            "position": ("chuc_vu", self._position_to_dict),
            "department": ("phong_ban", self._department_to_dict),
            "team": ("nhom_du_an", self._team_to_dict),
            "history": ("lich_su_lam_viec", self._work_history_to_dict),
        }

        if kind not in mapping:
            return None, None

        model_name, serializer = mapping[kind]
        return request.env[model_name].sudo(), serializer

    def _fit_float(self, value):
        try:
            return float(value or 0)
        except Exception:
            return 0.0

    def _fit_int(self, value):
        try:
            return int(value or 0)
        except Exception:
            return 0

    def _fit_prepare_values(self, kind, values, create=False):
        vals = {}

        if kind == "employee":
            if create:
                vals["ma_dinh_danh"] = values.get("code") or "FE-NV-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["ma_dinh_danh"] = values.get("code") or False

            field_map = {
                "first_part": "ho_ten_dem",
                "last_name": "ten",
                "email": "email",
                "phone": "so_dien_thoai",
                "gender": "gioi_tinh",
                "birth": "ngay_sinh",
                "hometown": "que_quan",
            }
            for src, dst in field_map.items():
                if src in values:
                    vals[dst] = values.get(src) or False

            if "position_id" in values:
                vals["chuc_vu_id"] = self._fit_int(values.get("position_id")) or False
            if "department_id" in values:
                vals["phong_ban_id"] = self._fit_int(values.get("department_id")) or False

        elif kind == "position":
            if create:
                vals["ma_chuc_vu"] = values.get("code") or "FE-CV-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["ma_chuc_vu"] = values.get("code") or False
            if "name" in values:
                vals["ten_chuc_vu"] = values.get("name") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "department":
            if create:
                vals["ma_phong_ban"] = values.get("code") or "FE-PB-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["ma_phong_ban"] = values.get("code") or False
            if "name" in values:
                vals["ten_phong_ban"] = values.get("name") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "team":
            if "name" in values:
                vals["ten_nhom"] = values.get("name") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "history":
            if "employee_id" in values:
                vals["nhan_vien_id"] = self._fit_int(values.get("employee_id")) or False
            if "name" in values:
                vals["ten_cong_viec"] = values.get("name") or False
            if "start" in values:
                vals["ngay_bat_dau"] = values.get("start") or False
            if "end" in values:
                vals["ngay_ket_thuc"] = values.get("end") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "project":
            if create:
                vals["ma_du_an"] = values.get("code") or "FE-DA-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["ma_du_an"] = values.get("code") or False
            if "name" in values:
                vals["ten_du_an"] = values.get("name") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False
            if "responsible_id" in values:
                vals["nguoi_phu_trach_id"] = self._fit_int(values.get("responsible_id")) or False
            if "status" in values:
                vals["tien_do_du_an"] = values.get("status") or False
            if "start_date" in values:
                vals["ngay_bat_dau"] = values.get("start_date") or False
            if "expected_end" in values:
                vals["ngay_ket_thuc_du_kien"] = values.get("expected_end") or False
            if "actual_end" in values:
                vals["ngay_ket_thuc_thuc_te"] = values.get("actual_end") or False

        elif kind == "stage":
            if "project_id" in values:
                vals["du_an_id"] = self._fit_int(values.get("project_id")) or False
            if "name" in values:
                vals["ten_giai_doan"] = values.get("name") or False
            if "order" in values:
                vals["thu_tu"] = self._fit_int(values.get("order")) or 1
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "budget":
            if create:
                vals["budgets_id"] = values.get("code") or "FE-BG-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["budgets_id"] = values.get("code") or False
            if "project_id" in values:
                vals["du_an_id"] = self._fit_int(values.get("project_id")) or False
            if "name" in values:
                vals["budgets_name"] = values.get("name") or False
            if "planned" in values:
                vals["budget_planned"] = self._fit_float(values.get("planned"))
            if "allocated" in values:
                vals["budget_allocated"] = self._fit_float(values.get("allocated"))
            if "reserved" in values:
                vals["budget_reserved"] = self._fit_float(values.get("reserved"))

        elif kind == "expense":
            if "budget_id" in values:
                vals["budgets_id"] = self._fit_int(values.get("budget_id")) or False
            if "name" in values:
                vals["expenses_name"] = values.get("name") or False
            if "amount" in values:
                vals["amount"] = self._fit_float(values.get("amount"))
            if "date" in values:
                vals["date"] = values.get("date") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False
            if "over_reason" in values:
                vals["ly_do_vuot_ngan_sach"] = values.get("over_reason") or False

        elif kind == "resource":
            if "project_id" in values:
                vals["du_an_id"] = self._fit_int(values.get("project_id")) or False
            if "name" in values:
                vals["ten_tai_nguyen"] = values.get("name") or False
            if "quantity" in values:
                vals["so_luong"] = self._fit_int(values.get("quantity")) or 0
            if "unit" in values:
                vals["don_vi"] = values.get("unit") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "task":
            if create:
                vals["ma_cong_viec"] = values.get("code") or "FE-%s" % datetime.now().strftime("%Y%m%d%H%M%S")
            elif "code" in values:
                vals["ma_cong_viec"] = values.get("code") or False
            if "name" in values:
                vals["ten_cong_viec"] = values.get("name") or False
            if "project_id" in values:
                vals["du_an_id"] = self._fit_int(values.get("project_id")) or False
            if "responsible_id" in values:
                vals["nguoi_phu_trach_id"] = self._fit_int(values.get("responsible_id")) or False
            if "priority" in values:
                vals["priority"] = values.get("priority") or "medium"
            if "status" in values:
                vals["status"] = values.get("status") or "not_started"
            if "progress" in values:
                vals["phan_tram_cong_viec"] = self._fit_float(values.get("progress"))
            if "deadline" in values:
                vals["han_chot"] = values.get("deadline") or False
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "work_log":
            if "task_id" in values:
                vals["cong_viec_id"] = self._fit_int(values.get("task_id")) or False
            if "progress" in values:
                vals["muc_do"] = self._fit_float(values.get("progress"))
            if "description" in values:
                vals["mo_ta"] = values.get("description") or False

        elif kind == "evaluation":
            if "employee_id" in values:
                vals["nhan_vien_id"] = self._fit_int(values.get("employee_id")) or False
            if "task_id" in values:
                vals["cong_viec_id"] = self._fit_int(values.get("task_id")) or False
            if "score" in values:
                vals["diem_so"] = str(values.get("score") or "")
            if "comment" in values:
                vals["nhan_xet"] = values.get("comment") or False

        return vals

    @http.route("/fit/api/record/read", type="json", auth="user")
    def api_record_read(self, **params):
        kind = self._fit_normalize_kind(params)
        record_id = self._fit_int(params.get("id"))

        Model, serializer = self._fit_record_config(kind)
        if Model is None:
            return {"ok": False, "error": "Loại dữ liệu không hợp lệ: %s" % (kind or "rỗng"), "debug": {"keys": list(params.keys())}}

        record = Model.browse(record_id).exists()
        if not record:
            return {"ok": False, "error": "Không tìm thấy bản ghi."}

        return {"ok": True, "record": serializer(record)}

    @http.route("/fit/api/record/create", type="json", auth="user")
    def api_record_create(self, **params):
        kind = self._fit_normalize_kind(params)
        values = params.get("values") or {}

        Model, serializer = self._fit_record_config(kind)
        if Model is None:
            return {"ok": False, "error": "Loại dữ liệu không hợp lệ: %s" % (kind or "rỗng"), "debug": {"keys": list(params.keys())}}

        vals = self._fit_prepare_values(kind, values, create=True)

        try:
            record = Model.create(vals)
            return {"ok": True, "record": serializer(record)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/record/update", type="json", auth="user")
    def api_record_update(self, **params):
        kind = self._fit_normalize_kind(params)
        record_id = self._fit_int(params.get("id"))
        values = params.get("values") or {}

        Model, serializer = self._fit_record_config(kind)
        if Model is None:
            return {"ok": False, "error": "Loại dữ liệu không hợp lệ: %s" % (kind or "rỗng"), "debug": {"keys": list(params.keys())}}

        record = Model.browse(record_id).exists()
        if not record:
            return {"ok": False, "error": "Không tìm thấy bản ghi."}

        vals = self._fit_prepare_values(kind, values, create=False)

        try:
            record.write(vals)
            return {"ok": True, "record": serializer(record)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/record/delete", type="json", auth="user")
    def api_record_delete(self, **params):
        kind = self._fit_normalize_kind(params)
        record_id = self._fit_int(params.get("id"))

        Model, serializer = self._fit_record_config(kind)
        if Model is None:
            return {"ok": False, "error": "Loại dữ liệu không hợp lệ: %s" % (kind or "rỗng"), "debug": {"keys": list(params.keys())}}

        record = Model.browse(record_id).exists()
        if not record:
            return {"ok": False, "error": "Không tìm thấy bản ghi."}

        try:
            record.unlink()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/task/create", type="json", auth="user")
    def api_task_create(self, **params):
        Task = request.env["cong_viec"].sudo()
        Project = request.env["du_an"].sudo()
        Employee = request.env["nhan_vien"].sudo()

        name = (params.get("name") or "").strip()
        project_id = int(params.get("project_id") or 0)
        responsible_id = int(params.get("responsible_id") or 0)
        priority = params.get("priority") or "medium"
        deadline = params.get("deadline") or False
        description = params.get("description") or ""

        if not name:
            return {"ok": False, "error": "Tên công việc không được để trống."}

        project = Project.browse(project_id).exists()
        if not project:
            return {"ok": False, "error": "Vui lòng chọn dự án hợp lệ."}

        vals = {
            "ma_cong_viec": "FE-%s" % datetime.now().strftime("%Y%m%d%H%M%S"),
            "ten_cong_viec": name,
            "du_an_id": project.id,
            "priority": priority,
            "status": "not_started",
            "mo_ta": description,
        }

        if deadline:
            try:
                vals["han_chot"] = fields.Datetime.to_string(
                    datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
                )
            except Exception:
                return {"ok": False, "error": "Định dạng hạn chót không hợp lệ."}

        if responsible_id:
            employee = Employee.browse(responsible_id).exists()
            if not employee:
                return {"ok": False, "error": "Nhân viên phụ trách không hợp lệ."}

            if employee.id not in project.nhan_vien_ids.ids:
                return {
                    "ok": False,
                    "error": "Người phụ trách phải thuộc danh sách nhân viên của dự án.",
                }

            vals["nguoi_phu_trach_id"] = employee.id
            vals["nhan_vien_ids"] = [(6, 0, [employee.id])]

        try:
            task = Task.create(vals)
            return {"ok": True, "task": self._task_to_dict(task)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/task/status", type="json", auth="user")
    def api_task_status(self, **params):
        Task = request.env["cong_viec"].sudo()

        task_id = int(params.get("task_id") or 0)
        status = params.get("status")

        allowed = ["not_started", "in_progress", "completed", "delayed", "cancelled"]
        if status not in allowed:
            return {"ok": False, "error": "Trạng thái không hợp lệ."}

        task = Task.browse(task_id).exists()
        if not task:
            return {"ok": False, "error": "Không tìm thấy công việc."}

        try:
            task.write({"status": status})
            return {"ok": True, "task": self._task_to_dict(task)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/work-log/create", type="json", auth="user")
    def api_work_log_create(self, **params):
        Task = request.env["cong_viec"].sudo()
        WorkLog = request.env["nhat_ky_cong_viec"].sudo()

        task_id = int(params.get("task_id") or 0)
        progress = float(params.get("progress") or 0)
        description = params.get("description") or ""

        task = Task.browse(task_id).exists()
        if not task:
            return {"ok": False, "error": "Không tìm thấy công việc."}

        if progress < 0 or progress > 100:
            return {"ok": False, "error": "Mức độ hoàn thành phải từ 0 đến 100."}

        if progress < 40:
            state = "chua_hoan_thanh"
        elif progress < 80:
            state = "hoan_thanh"
        else:
            state = "hoan_thanh_xuat_sac"

        try:
            log = WorkLog.create({
                "cong_viec_id": task.id,
                "nhan_vien_ids": [(6, 0, task.nhan_vien_ids.ids)],
                "muc_do": progress,
                "trang_thai": state,
                "mo_ta": description,
            })
            return {"ok": True, "log": self._work_log_to_dict(log)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @http.route("/fit/api/evaluation/create", type="json", auth="user")
    def api_evaluation_create(self, **params):
        Evaluation = request.env["danh_gia_nhan_vien"].sudo()
        Employee = request.env["nhan_vien"].sudo()
        Task = request.env["cong_viec"].sudo()

        employee_id = int(params.get("employee_id") or 0)
        task_id = int(params.get("task_id") or 0)
        score = str(params.get("score") or "")
        comment = params.get("comment") or ""

        employee = Employee.browse(employee_id).exists()
        if not employee:
            return {"ok": False, "error": "Vui lòng chọn nhân viên hợp lệ."}

        if score not in [str(i) for i in range(1, 11)]:
            return {"ok": False, "error": "Điểm số phải từ 1 đến 10."}

        vals = {
            "nhan_vien_id": employee.id,
            "diem_so": score,
            "nhan_xet": comment,
        }

        if task_id:
            task = Task.browse(task_id).exists()
            if not task:
                return {"ok": False, "error": "Không tìm thấy công việc."}
            vals["cong_viec_id"] = task.id
            vals["du_an_id"] = task.du_an_id.id

        try:
            item = Evaluation.create(vals)
            return {"ok": True, "evaluation": self._evaluation_to_dict(item)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
