from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from utils.eth_balance_check import run_balance_check

class EthBalanceWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, addresses_text):
        super().__init__()
        self.addresses_text = addresses_text
        self._is_interrupted = False  # Если потребуется добавить возможность прерывания
    
    def run(self):
        # Преобразуем введённый текст (адреса, по одному на строке) в список
        addresses = [line.strip() for line in self.addresses_text.splitlines() if line.strip()]
        
        try:
            # Определяем функцию для обновления прогресса
            def progress_update(value):
                self.progress.emit(value)
            # Вызываем основную функцию проверки балансов из отдельного файла
            run_balance_check(addresses, progress_callback=progress_update)
        except Exception as e:
            self.error.emit(str(e))
        self.finished.emit()
    
    def stop(self):
        # Механизм прерывания можно реализовать, если функция run_balance_check будет периодически проверять флаг
        self._is_interrupted = True

class EthBalanceCheckerPage(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self.thread = None
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Многострочное поле для ввода адресов (по одному на строке)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Введите адреса кошельков, по одному на строке")
        self.text_edit.setAcceptRichText(False)
        
        # Кнопка для запуска проверки
        self.start_button = QPushButton("Запустить ETH balance checker", self)
        self.start_button.clicked.connect(self.start_worker)
        
        # Кнопка для прерывания выполнения
        self.stop_button = QPushButton("Прервать выполнение", self)
        self.stop_button.clicked.connect(self.stop_worker)
        self.stop_button.setEnabled(False)
        
        # Индикатор выполнения (progress bar)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        
        # Кнопка для возврата на главную страницу
        self.back_button = QPushButton("Назад", self)
        self.back_button.clicked.connect(self.back_callback)
        
        layout.addWidget(self.text_edit)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.back_button)
        self.setLayout(layout)
    
    def start_worker(self):
        addresses_text = self.text_edit.toPlainText()
        if not addresses_text.strip():
            print("Нет введённых данных для проверки.")
            return
        
        self.thread = QThread()
        self.worker = EthBalanceWorker(addresses_text)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.error.connect(lambda err: print(f"Ошибка: {err}"))
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        
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
        print("ETH balance check завершён. XLSX файл сохранён в проекте.")
