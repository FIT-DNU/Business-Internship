# -*- coding: utf-8 -*-

import json


def parse_ai_json_array(text):
    if not text:
        raise Exception("AI không trả về nội dung.")

    text = text.strip()

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise Exception("AI không trả về JSON array hợp lệ.")

    json_text = text[start:end + 1]

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as error:
        raise Exception(f"Không parse được JSON từ AI: {error}")

    if not isinstance(data, list):
        raise Exception("JSON AI trả về phải là một mảng.")

    return data


def normalize_task_item(item, index):
    if not isinstance(item, dict):
        raise Exception(f"Công việc thứ {index} không hợp lệ.")

    title = (
        item.get("title")
        or item.get("ten_cong_viec")
        or item.get("name")
        or f"Công việc AI {index}"
    )

    description = (
        item.get("description")
        or item.get("mo_ta")
        or ""
    )

    priority = item.get("priority") or "medium"
    if priority not in ("low", "medium", "high"):
        priority = "medium"

    try:
        estimated_days = int(item.get("estimated_days") or item.get("days") or 1)
    except Exception:
        estimated_days = 1

    if estimated_days < 1:
        estimated_days = 1
    if estimated_days > 30:
        estimated_days = 30

    return {
        "title": str(title).strip(),
        "description": str(description).strip(),
        "priority": priority,
        "estimated_days": estimated_days,
    }
