import os
import time
import threading
import asyncio
import pygame
import edge_tts

class VoiceModule:
    def __init__(self, voice_name="ru-RU-SvetlanaNeural"):
        """Оригинальный аудио-движок Юлии v5.2 из вашего бэкапа"""
        self.voice_name = voice_name
        self.audio_file = "response.mp3"
        self.is_speaking = False
        
        # Инициализация плеера Pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    def _speak_worker(self, text, on_finish_callback):
        self.is_speaking = True
        try:
            # Принудительно выгружаем прошлый файл, если он заблокирован в памяти Windows
            try:
                pygame.mixer.music.unload()
            except Exception:
                pass

            # Если старый файл остался на диске, удаляем его перед новой записью
            if os.path.exists(self.audio_file):
                try: os.remove(self.audio_file)
                except Exception: pass

            # Запускаем оригинальный Communicate из вашего бэкапа
            communicate = edge_tts.Communicate(text, self.voice_name)
            
            # Создаем новый цикл событий для асинхронного скачивания файла целиком
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(self.audio_file))
            loop.close()

            # Воспроизводим готовый файл через Mixer
            if os.path.exists(self.audio_file):
                pygame.mixer.music.load(self.audio_file)
                pygame.mixer.music.play()
                
                # Ждем окончания воспроизведения речи Юлии
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
                
                pygame.mixer.music.unload()

        except Exception as e:
            print(f"[VOICE ERROR] Ошибка генерации или проигрывания: {e}")
            
        self.is_speaking = False
        if on_finish_callback:
            on_finish_callback()

    def speak(self, full_text, on_phrase_start=None, on_speech_finish=None):
        """Главная функция запуска голоса. Работает в фоне, не вешая интерфейс чата"""
        if not full_text.strip():
            return
            
        # Запускаем озвучку ответа в отдельном изолированном потоке
        threading.Thread(
            target=self._speak_worker, 
            args=(full_text, on_speech_finish), 
            daemon=True
        ).start()

    def stop(self):
        """Мгновенное прерывание голоса"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass
        self.is_speaking = False
