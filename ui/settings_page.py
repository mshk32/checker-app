# ui/settings_page.py
import configparser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from utils.get_config_path import config_path


class SettingsPage(QWidget):
    def __init__(self, back_callback, config_path=config_path):
        super().__init__()
        self.back_callback = back_callback
        self.config_path = config_path

        #Список поддерживаемых сетей
        self.networks = [
            "ethereum",
            "arbitrum",
            "optimism",
            "linea",
            "zksync",
            "scroll",
            "base",
            "arbitrum_nova"
        ]
        
        self.checkboxes = {}
        self.rpc_edits = {}
        
        # Виджет для задания директории сохранения результатов
        self.output_dir_edit = QLineEdit()
        self.output_dir_button = QPushButton("Обзор")
        self.output_dir_button.clicked.connect(self.browse_output_directory)

        # Читаем конфигурацию
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Настройки ETH balance check")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Секция для сетей: чекбоксы и поля RPC
        for net in self.networks:
            row_layout = QHBoxLayout()
            checkbox = QCheckBox(net)
            self.checkboxes[net] = checkbox

            rpc_edit = QLineEdit()
            self.rpc_edits[net] = rpc_edit

            row_layout.addWidget(checkbox)
            row_layout.addWidget(rpc_edit)
            layout.addLayout(row_layout)

        # Секция для задания директории сохранения результатов
        output_layout = QHBoxLayout()
        output_label = QLabel("Директория сохранения:")
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.output_dir_button)
        layout.addLayout(output_layout)

        # Кнопки "Сохранить" и "Назад"
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)

        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.back_callback)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(back_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите директорию сохранения")
        if directory:
            self.output_dir_edit.setText(directory)

    def load_settings(self):
        """Загружаем текущее состояние из config.ini и заполняем виджеты."""
        if "Networks" in self.config:
            for net in self.networks:
                enabled = self.config.getboolean("Networks", net, fallback=False)
                self.checkboxes[net].setChecked(enabled)

        if "RPCs" in self.config:
            for net in self.networks:
                rpc_url = self.config.get("RPCs", net, fallback="")
                self.rpc_edits[net].setText(rpc_url)

        # Загружаем настройки директории сохранения (из секции Output)
        if "Output" in self.config:
            output_dir = self.config.get("Output", "output_dir", fallback="")
            self.output_dir_edit.setText(output_dir)
        else:
            self.output_dir_edit.setText("")

    def save_settings(self):
        """Сохраняем изменения в config.ini."""
        if "Networks" not in self.config:
            self.config["Networks"] = {}
        if "RPCs" not in self.config:
            self.config["RPCs"] = {}
        if "Output" not in self.config:
            self.config["Output"] = {}

        for net in self.networks:
            self.config["Networks"][net] = str(self.checkboxes[net].isChecked())
            self.config["RPCs"][net] = self.rpc_edits[net].text()

        self.config["Output"]["output_dir"] = self.output_dir_edit.text()

        with open(self.config_path, "w") as f:
            self.config.write(f)

        print("Настройки сохранены!")
