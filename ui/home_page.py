# ui/home_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self, scripts, switch_callback, settings_callback=None):
        """
        :param scripts: Список названий скриптов (например, ["ETH balance checker", "ATOM balance checker"])
        :param switch_callback: Функция, вызываемая при выборе скрипта
        :param settings_callback: Функция, вызываемая при нажатии кнопки "Настройки" (может быть None, если не нужна)
        """
        super().__init__()
        self.scripts = scripts
        self.switch_callback = switch_callback
        self.settings_callback = settings_callback
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(50, 50, 50, 50)
        container.setLayout(container_layout)
        container.setMaximumWidth(500)
        
        label = QLabel("Выберите скрипт:")
        container_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        for script in self.scripts:
            button = QPushButton(script)
            button.clicked.connect(lambda checked, s=script: self.switch_callback(s))
            container_layout.addWidget(button)
        
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)

        # Добавляем кнопку "Настройки" в правый нижний угол, если передан settings_callback
        if self.settings_callback is not None:
            settings_layout = QHBoxLayout()
            settings_layout.addStretch(1)  # Чтобы прижать кнопку к правому краю
            settings_button = QPushButton("Настройки")
            settings_button.clicked.connect(self.settings_callback)
            settings_layout.addWidget(settings_button, alignment=Qt.AlignmentFlag.AlignRight)
            main_layout.addLayout(settings_layout)
        
        self.setLayout(main_layout)
