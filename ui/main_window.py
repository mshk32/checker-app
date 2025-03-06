# ui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtGui import QAction
from .home_page import HomePage
from .eth_balance_checker_page import EthBalanceCheckerPage
from .atom_balance_checker_page import AtomBalanceCheckerPage
from .settings_page import SettingsPage  # Подключаем новый модуль

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checker app")
        self.resize(800, 600)  # Более адекватный размер окна

        self.scripts = ["ETH balance checker", "ATOM balance checker"]
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Создаём страницу настроек
        self.settings_page = SettingsPage(self.show_home)
        self.stack.addWidget(self.settings_page)

        # Главная страница (передаем колбэк для перехода на настройки)
        self.home_page = HomePage(self.scripts, self.switch_page, self.show_settings)
        self.stack.addWidget(self.home_page)

        # Страницы для скриптов, передаём функцию возврата на главную
        self.pages = {
            "ETH balance checker": EthBalanceCheckerPage(self.show_home),
            "ATOM balance checker": AtomBalanceCheckerPage(self.show_home)
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        # Меню для навигации
        home_action = QAction("Главная", self)
        home_action.triggered.connect(self.show_home)
        self.menuBar().addAction(home_action)

        script_menu = self.menuBar().addMenu("Выбрать скрипт")
        for script in self.scripts:
            action = QAction(script, self)
            action.triggered.connect(lambda checked, s=script: self.switch_page(s))
            script_menu.addAction(action)

        # Можно добавить отдельный пункт "Настройки" в меню (необязательно)
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        self.menuBar().addAction(settings_action)

        # При запуске показываем главную страницу
        self.show_home()

    def switch_page(self, script_name):
        page = self.pages.get(script_name)
        if page:
            self.stack.setCurrentWidget(page)
            print(f"Переключились на страницу: {script_name}")

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)
        print("Переход на главную страницу")

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_page)
        print("Переход на страницу настроек")
