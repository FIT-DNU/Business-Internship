# -*- coding: utf-8 -*-

import requests

from .prompt_builder import SYSTEM_PROMPT


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:1.5b"


class OllamaClient:
    def __init__(self, model=OLLAMA_MODEL, url=OLLAMA_URL, timeout=180):
        self.model = model
        self.url = url
        self.timeout = timeout

    def generate(self, prompt):
        payload = {
            "model": self.model,
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            },
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Không kết nối được Ollama. Hãy chạy: ollama serve "
                "hoặc kiểm tra Ollama tại http://127.0.0.1:11434"
            )
        except requests.exceptions.Timeout:
            raise Exception("Ollama phản hồi quá lâu. Hãy thử lại hoặc dùng model nhỏ hơn.")
        except requests.exceptions.RequestException as error:
            raise Exception(f"Lỗi khi gọi Ollama: {error}")

        data = response.json()
        return data.get("response", "")
