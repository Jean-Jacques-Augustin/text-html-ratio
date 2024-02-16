import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import nltk
import requests

nltk.download('punkt')


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            html_content = response.text

            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()

            sentences = sent_tokenize(text)

            total_text_chars = sum(len(sentence) for sentence in sentences)
            total_html_chars = len(html_content)

            ratio = total_text_chars / total_html_chars

            self.result_ready.emit(f"Ratio entre HTML/texte : {ratio:.3%}")

        except requests.exceptions.RequestException as e:
            # Gérer les erreurs de requête HTTP
            self.result_ready.emit(f"Erreur : {e}")


class HtmlTextRatioApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Ratio HTML/Texte')
        self.setGeometry(100, 100, 400, 200)

        # Widgets
        self.label = QLabel("Entrez l'URL à analyser:")
        self.url_input = QLineEdit()
        self.analyze_button = QPushButton('Analyser')
        self.progress_bar = QProgressBar()
        self.result_label = QLabel("")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.analyze_button.clicked.connect(self.start_analysis)

        self.progress_bar.setRange(0, 0)

    def start_analysis(self):
        url = self.url_input.text()

        self.url_input.setDisabled(True)
        self.analyze_button.setDisabled(True)

        self.worker_thread = WorkerThread(url)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.result_ready.connect(self.show_result)
        self.worker_thread.start()

    def update_progress(self, value):
        pass

    def show_result(self, result):
        self.url_input.setDisabled(False)
        self.analyze_button.setDisabled(False)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        self.result_label.setText(result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HtmlTextRatioApp()
    window.show()
    sys.exit(app.exec_())
