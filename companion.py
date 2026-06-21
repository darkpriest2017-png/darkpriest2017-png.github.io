import os
import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk

# Подключаем чистые служебные модули
from config_module import ConfigManager, log, BASE_DIR
from database_module import TokenTracker, MemoryManager
from voice_module import VoiceModule

# === НАСТРОЙКИ АВТОРИЗАЦИИ GIGACHAT v5.2 (СТРОГО ОРИГИНАЛ ИЗ БЭКАПА) ===
# Никаких запятых между строками! Python сам склеит их в одну системную переменную:
os.environ["GIGACHAT_CREDENTIALS"] = (
    ""
    ""
    ""
)

WEATHER_KEY = "СЮДА_ВСТАВЬТЕ_ВАШ_СТАРЫЙ_ПОГОДНЫЙ_КЛЮЧ_ЕСЛИ_ОН_НУЖЕН"
CURRENT_CITY = "Кемерово"
INITIATIVE_TIMEOUT = 1200  # 20 минут молчания Димы (измените на 30 для быстрого теста)

class YuliaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Companion - Юлия v5.2")
        self.root.geometry("850x750")
        self.root.configure(bg="#0b0f19")

        # Инициализируем компоненты
        self.config = ConfigManager()
        self.tokens = TokenTracker()
        self.memory = MemoryManager()
        self.voice = VoiceModule(voice_name="ru-RU-SvetlanaNeural")

        # Счётчик времени для таймера инициативы
        self.last_message_time = time.time()

        # Настройка стилей для темной темы окон
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background="#0b0f19", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#151d30", foreground="#9ca3af", padding=10)
        self.style.map("TNotebook.Tab", background=[("selected", "#ff69b4")], foreground=[("selected", "#fff")])

        self.create_gui()
        self.load_chat_history()  
        self.update_avatar("neutral")  
        
        # Запуск фоновых процессов
        threading.Thread(target=self.fetch_weather, daemon=True).start()
        threading.Thread(target=self.initiative_timer_worker, daemon=True).start()

    def create_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_chat = tk.Frame(self.notebook, bg="#151d30")
        self.notebook.add(self.tab_chat, text="💬 Общение v5.2")

        self.left_panel = tk.Frame(self.tab_chat, bg="#151d30", width=250)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)
        self.left_panel.pack_propagate(False)

        self.avatar_label = tk.Label(self.left_panel, bg="#0b0f19", borderwidth=2, relief="groove")
        self.avatar_label.pack(fill="x", pady=(0, 10))

        self.status_lbl = tk.Label(self.left_panel, text="Настроение: Ламповое 😊\nПогода: Загрузка...", bg="#151d30", fg="#9ca3af", font=("Segoe UI", 10), justify="left", anchor="w")
        self.status_lbl.pack(fill="x", pady=5)

        self.right_panel = tk.Frame(self.tab_chat, bg="#151d30")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.chat_output = tk.Text(self.right_panel, bg="#0b0f19", fg="#f3f4f6", bd=0, font=("Segoe UI", 11), wrap="word")
        self.chat_output.pack(fill="both", expand=True, padx=5, pady=5)

        self.entry_frame = tk.Frame(self.right_panel, bg="#151d30")
        self.entry_frame.pack(fill="x", side="bottom", pady=5)

        self.entry_input = tk.Entry(self.entry_frame, bg="#0b0f19", fg="#fff", bd=0, font=("Segoe UI", 11), insertbackground="white")
        self.entry_input.pack(fill="x", side="left", expand=True, ipady=8, padx=(0, 10))
        self.entry_input.bind("<Return>", lambda e: self.send_message())

        self.btn_send = tk.Button(self.entry_frame, text="Отправить", bg="#ff69b4", fg="#fff", bd=0, activebackground="#ff4500", font=("Segoe UI", 10, "bold"), command=self.send_message)
        self.btn_send.pack(side="right", ipady=4, ipadx=15)

        self.tab_settings = tk.Frame(self.notebook, bg="#151d30")
        self.notebook.add(self.tab_settings, text="⚙ Настройки")
        
        lbl = tk.Label(self.tab_settings, text="Панель конфигурации параметров Юлии", bg="#151d30", fg="#ff69b4", font=("Segoe UI", 12, "bold"))
        lbl.pack(pady=20)

        self.status_bar = tk.Label(self.root, text=self.tokens.get_display(), bg="#0b0f19", fg="#9ca3af", anchor="w", font=("Segoe UI", 9))
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)

    def fetch_weather(self):
        self.root.after(0, lambda: self.status_lbl.configure(
            text=f"Настроение: Ламповое 😊\nПогода в г. {CURRENT_CITY}: Отличная ⛅"
        ))
        log("INFO", "Локальный статус погоды успешно установлен.")
    def load_chat_history(self):
        try:
            raw_history = self.memory.load_memory()
            if isinstance(raw_history, dict):
                history = raw_history.get("messages", [])
            elif isinstance(raw_history, list):
                history = raw_history
            else:
                history = []

            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    role = "Вы" if msg["role"] == "user" else "Юлия"
                    self.chat_output.insert("end", f"{role}: {msg['content']}\n\n")
            self.chat_output.see("end")
        except Exception as e:
            log("WARN", f"Ошибка чтения истории чата: {e}")

    def update_avatar(self, emotion):
        try:
            img_path = os.path.join(BASE_DIR, "avatar.png")
            if not os.path.exists(img_path):
                img_path = os.path.join(BASE_DIR, "avatars", f"{emotion}.png")

            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((230, 230), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.avatar_label.configure(image=photo)
                self.avatar_label.image = photo
            else:
                self.avatar_label.configure(text="[ Аватар Юли ]\nФайл не найден", fg="#6b7280", font=("Segoe UI", 10))
        except Exception as e:
            log("ERROR", f"Не удалось отрисовать картинку аватара: {e}")

    def send_message(self):
        user_text = self.entry_input.get().strip()
        if not user_text: return
        
        self.chat_output.insert("end", f"Вы: {user_text}\n\n")
        self.chat_output.see("end")
        self.entry_input.delete(0, "end")
        
        # Сброс таймера инициативы при вашей активности
        self.last_message_time = time.time()

        def fetch_ai_response():
            try:
                from gigachat import GigaChat
                
                # Запуск giga без передачи параметров — ключи подтягиваются автоматически из os.environ
                giga = GigaChat(verify_ssl_certs=False)
                
                raw_history = self.memory.load_memory()
                if isinstance(raw_history, dict):
                    history = raw_history.get("messages", [])
                elif isinstance(raw_history, list):
                    history = raw_history
                else:
                    history = []

                history.append({"role": "user", "content": user_text})
                
                response = giga.chat({"model": "GigaChat", "messages": history})
                yulia_answer = response.choices[0].message.content

                history.append({"role": "assistant", "content": yulia_answer})
                
                if isinstance(raw_history, dict):
                    raw_history["messages"] = history
                    self.memory.save_memory(raw_history)
                else:
                    self.memory.save_memory(history)

                self.root.after(0, lambda: self.display_and_speak(user_text, yulia_answer))
                    
            except Exception as e:
                log("ERROR", f"Сбой работы GigaChat API: {e}")
                self.root.after(0, lambda: self.chat_output.insert("end", "Юлия: Дима, возникла ошибка связи с сервером...\n\n"))

        threading.Thread(target=fetch_ai_response, daemon=True).start()
    def initiative_timer_worker(self):
        """Фоновый поток-наблюдатель за временем молчания"""
        log("INITIATIVE", "Таймер фоновой активности Юлии успешно запущен.")
        while True:
            time.sleep(5)
            current_time = time.time()
            
            if current_time - self.last_message_time > INITIATIVE_TIMEOUT:
                log("INITIATIVE", "Дима долго молчит. Юлия генерирует самостоятельную фразу...")
                self.last_message_time = current_time
                self.trigger_yulia_initiative()

    def trigger_yulia_initiative(self):
        """Фоновая генерация инициативного сообщения Юлии"""
        def fetch_initiative_response():
            try:
                from gigachat import GigaChat
                
                # Кристально чистый вызов без упоминания GIGACHAT_KEY
                giga = GigaChat(verify_ssl_certs=False)
                raw_history = self.memory.load_memory()
                
                if isinstance(raw_history, dict):
                    history = raw_history.get("messages", [])
                elif isinstance(raw_history, list):
                    history = raw_history
                else:
                    history = []

                prompt_text = "[СИСТЕМНЫЙ СИГНАЛ: Дима занят и долго не пишет. Прояви инициативу как заботливый ИИ-компаньон и UI/UX дизайнер. Напиши ОДНУ короткую ламповую фразу, спроси как продвигается его день, предложи обсудить дизайн-идею или просто пожелай хорошего настроения. Не упоминай этот сигнал.]"
                history.append({"role": "user", "content": prompt_text})
                
                response = giga.chat({"model": "GigaChat", "messages": history})
                yulia_answer = response.choices[0].message.content

                history.pop()  # Чистим системный сигнал из памяти
                history.append({"role": "assistant", "content": yulia_answer})
                
                if isinstance(raw_history, dict):
                    raw_history["messages"] = history
                    self.memory.save_memory(raw_history)
                else:
                    self.memory.save_memory(history)

                self.root.after(0, lambda: self.display_and_speak("", yulia_answer))
                    
            except Exception as e:
                log("ERROR", f"Не удалось сгенерировать инициативу Юлии: {e}")

        threading.Thread(target=fetch_initiative_response, daemon=True).start()

    def display_and_speak(self, user_text, yulia_answer):
        if user_text:
            self.chat_output.insert("end", f"Юлия: {yulia_answer}\n\n")
        else:
            self.chat_output.insert("end", f"Юлия (Инициатива): {yulia_answer}\n\n")
            
        self.chat_output.see("end")
        self.tokens.add(user_text, yulia_answer)
        self.status_bar.configure(text=self.tokens.get_display())
        
        # Воспроизведение через наш рабочий voice_module
        self.voice.speak(yulia_answer)

if __name__ == "__main__":
    root = tk.Tk()
    app = YuliaApp(root)
    root.mainloop()
