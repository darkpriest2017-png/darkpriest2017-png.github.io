# -*- coding: utf-8 -*-
import os
import json
import logging

class JSONDatabase:
    """Класс для безопасного управления всеми JSON-файлами памяти Юли."""
    
    def __init__(self, base_dir=None):
        # Если директория не задана, берем текущую папку скрипта
        self.base_dir = base_dir if base_dir else os.path.dirname(os.path.abspath(__file__))
        
    def _get_path(self, filename):
        """Возвращает полный путь к файлу данных."""
        if not filename.endswith('.json'):
            filename += '.json'
        return os.path.join(self.base_dir, filename)

    def load_json(self, filename, default_factory=dict):
        """Безопасно загружает данные из JSON. Создает бэкап при ошибке."""
        path = self._get_path(filename)
        bak_path = path + '.bak'
        
        if not os.path.exists(path):
            # Если файла нет, но есть бэкап — восстанавливаем из бэкапа
            if os.path.exists(bak_path):
                try:
                    with open(bak_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.save_json(filename, data)
                    return data
                except Exception:
                    pass
            return default_factory()
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError) as e:
            logging.error(f"Ошибка чтения {filename}: {e}. Пробуем загрузить бэкап.")
            if os.path.exists(bak_path):
                try:
                    with open(bak_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    return default_factory()
            return default_factory()

    def save_json(self, filename, data):
        """Записывает данные в JSON с предварительным созданием бэкапа .bak"""
        path = self._get_path(filename)
        bak_path = path + '.bak'
        
        try:
            # Создаем резервную копию перед перезаписью
            if os.path.exists(path):
                if os.path.exists(bak_path):
                    os.remove(bak_path)
                os.rename(path, bak_path)
                
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"Критическая ошибка записи в файл {filename}: {e}")
            # Если запись сорвалась, пробуем вернуть бэкап на место
            if os.path.exists(bak_path) and not os.path.exists(path):
                os.rename(bak_path, path)
            return False

# Инициализируем один глобальный экземпляр для работы со всеми файлами
db = JSONDatabase()
