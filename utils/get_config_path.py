import sys
import os

def get_app_path():
    if getattr(sys, 'frozen', False):
        # Если приложение собрано (frozen) PyInstaller, используем директорию с исполняемым файлом
        return os.path.dirname(sys.executable)
    else:
        # Если запуск из IDE/консоли, используем директорию исходного файла
        return os.path.dirname(__file__)


config_path = os.path.join(get_app_path(), "config.ini")
