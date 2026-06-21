import os
import json

# Фиксированные системные пути вашего проекта v3.2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")
FACTS_FILE = os.path.join(BASE_DIR, "facts.json")
CLOSENESS_FILE = os.path.join(BASE_DIR, "closeness.json")
MOOD_FILE = os.path.join(BASE_DIR, "mood.json")
VOSK_MODEL_PATH = os.path.join(BASE_DIR, "model")

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "tts_engine": "edge",
    "speech_rate_offset": 0,
    "microphone_index": None,
    "closeness_level": 1,
    "user_name": "Дима"
}

# Системный логгер (перенесен из вашего главного файла)
def log(category, message):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{category}] {message}")
    # При желании здесь можно раскомментировать запись в файл log.txt
    # with open("log.txt", "a", encoding="utf-8") as f:
    #     f.write(f"[{timestamp}] [{category}] {message}\n")

class ConfigManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log("ERROR", f"Ошибка чтения настроек settings.json: {e}")
        return DEFAULT_SETTINGS.copy()

    def save_settings(self, new_settings):
        self.settings.update(new_settings)
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
                log("INFO", "Настройки успешно сохранены.")
        except Exception as e:
            log("ERROR", f"Не удалось записать settings.json: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))
