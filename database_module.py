import os
import json
from datetime import datetime
from config_module import TOKENS_FILE, MEMORY_FILE, FACTS_FILE, CLOSENESS_FILE, MOOD_FILE, log

class TokenTracker:
    def __init__(self):
        self.total = 0
        self.today = 0
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.load()

    def load(self):
        if os.path.exists(TOKENS_FILE):
            try:
                with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.total = data.get("total", 0)
                    if data.get("date") == self.date:
                        self.today = data.get("today", 0)
            except Exception as e:
                log("ERROR", f"Ошибка трекера токенов: {e}")

    def save(self):
        try:
            with open(TOKENS_FILE, "w", encoding="utf-8") as f:
                json.dump({"total": self.total, "today": self.today, "date": self.date}, f)
        except Exception as e:
            log("ERROR", f"Не удалось сохранить токены: {e}")

    def add(self, text_in, text_out):
        # Простая эмуляция подсчета (для точного замените на ваш estimate_tokens)
        input_tok = len(text_in) // 4 + 1
        output_tok = len(text_out) // 4 + 1
        total = input_tok + output_tok
        self.total += total
        self.today += total
        self.save()
        log("TOKEN", f"Вход: {input_tok} | Выход: {output_tok} | Всего за день: {self.today}")
        return total

    def get_display(self):
        return f"Токены: {self.today} сегодня / {self.total} всего"

class MemoryManager:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.facts_file = FACTS_FILE
        self.closeness_file = CLOSENESS_FILE
        self.mood_file = MOOD_FILE
        
    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_memory(self, context):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=4)

    def load_closeness(self):
        if os.path.exists(self.closeness_file):
            with open(self.closeness_file, "r", encoding="utf-8") as f:
                return json.load(f).get("points", 0)
        return 0

    def save_closeness(self, points):
        with open(self.closeness_file, "w", encoding="utf-8") as f:
            json.dump({"points": points, "last_update": str(datetime.now())}, f)
