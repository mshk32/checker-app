import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from utils.atom_balance_check import get_address_data
import pandas as pd
import configparser
from utils.get_config_path import config_path

# Этот класс отвечает за выполнение логики проверки баланса Cosmos в отдельном потоке.
class AtomBalanceWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, input_data):
        super().__init__()
        self.input_data = input_data
        self._is_interrupted = False

    def run(self):
        addresses = []
        balances = []
        staked_values = []
        rewards_values = []

        config = configparser.ConfigParser()
        config.read(config_path)

        lines = self.input_data.splitlines()
        total = len(lines)
        for i, line in enumerate(lines):
            if self._is_interrupted:
                break
            address_data = get_address_data(line.strip())
            addresses.append(address_data[0])
            balances.append(address_data[1])
            staked_values.append(address_data[2])
            rewards_values.append(address_data[3])

            progress_percent = int((i + 1) / total * 100)
            self.progress.emit(progress_percent)
        
        df = pd.DataFrame({
            "address": addresses,
            "balance": balances,
            "staked": staked_values,
            "rewards": rewards_values
        })
        output_dir = config.get("Output", "output_dir", fallback="").strip()
        if output_dir:
            # Если указан, добавляем "/" или используем os.path.join для формирования пути
            import os
            excel_filename = os.path.join(output_dir, "atom_balances.xlsx")
        else:
            excel_filename = "atom_balances.xlsx"

        # Сохраняем в Excel-файл
        df.to_excel(excel_filename, index=False)
    
        self.finished.emit()

    def stop(self):
        """Метод для прерывания работы."""
        self._is_interrupted = True

# Страница интерфейса для проверки баланса Cosmos.
class AtomBalanceCheckerPage(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self.thread = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Многострочное поле для ввода данных (например, адреса кошелька)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Введите адреса кошельков, по одному на строке")
        self.text_edit.setAcceptRichText(False)

        # Кнопка для запуска проверки
        self.start_button = QPushButton("Запустить Atom balance checker", self)
        self.start_button.clicked.connect(self.start_worker)

        # Кнопка для прерывания выполнения
        self.stop_button = QPushButton("Прервать выполнение", self)
        self.stop_button.clicked.connect(self.stop_worker)
        self.stop_button.setEnabled(False)

        # Индикатор выполнения (progress bar)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)

        # Кнопка возврата на главную страницу
        self.back_button = QPushButton("Назад", self)
        self.back_button.clicked.connect(self.back_callback)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def start_worker(self):
        input_text = self.text_edit.toPlainText().strip()
        if not input_text:
            print("Нет введённых данных для проверки.")
            return

        # Создаем поток и рабочего объекта для выполнения долгой операции
        self.thread = QThread()
        self.worker = AtomBalanceWorker(input_text)
        self.worker.moveToThread(self.thread)

        # Соединяем сигналы и слоты
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Запуск потока
        self.thread.start()

        # Блокируем кнопку запуска и активируем кнопку прерывания
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.stop_button.setEnabled(False)

    def on_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        print("Atom balance check завершён. XLSX файл сохранён в проекте как 'atom_results.xlsx'.")
