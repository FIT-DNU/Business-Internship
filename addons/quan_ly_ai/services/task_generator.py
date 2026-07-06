# -*- coding: utf-8 -*-

from .ollama_client import OllamaClient
from .prompt_builder import build_generate_tasks_prompt
from .json_parser import parse_ai_json_array, normalize_task_item


def generate_tasks_for_project(project):
    prompt = build_generate_tasks_prompt(project)
    raw_response = OllamaClient().generate(prompt)
    raw_items = parse_ai_json_array(raw_response)

    tasks = []
    for index, item in enumerate(raw_items, start=1):
        tasks.append(normalize_task_item(item, index))

    return tasks, raw_response
