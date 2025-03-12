import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QFileDialog, QTextEdit, QCheckBox, QScrollArea,
    QLineEdit, QGridLayout, QProgressBar, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from superqt import QRangeSlider
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import fitz
from pdf_parser.pdf_parser import PDFParser
from nlp.qna_generator import QnAGenerator
from PyQt6.QtCore import qDebug
import logging
import tiktoken
import pyperclip
from PyQt6.QtGui import QMovie

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Dummy-Funktion zum Simulieren der PDF-Chunks
def chunk_pdf(file_path, start, end):
    return [f"Chunk {i}: Beispieltext aus der PDF" for i in range(start, end + 1)]

class Stepper(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Stepper-UI wird initialisiert.")

        # **QnAGenerator für alle Seiten initialisieren**
        self.qna_generator = None  # Wird später je nach API-Typ gesetzt

        # API-Seite laden (wo die API ausgewählt wird)
        self.api_page = ApiSelectionPage(self)

        # Navigation Buttons
        self.btn_cancel = QPushButton("Abbrechen")
        self.btn_prev = QPushButton("Zurück")
        self.btn_next = QPushButton("Weiter")

        self.setWindowTitle("PDF Wizard mit Stepper")
        self.resize(1000, 700)  # Setzt die Standardgröße auf 1000x700 Pixel
        self.setMinimumSize(800, 500)  # Minimale Fenstergröße, damit es nicht zu klein wird


        # Neue Schritte
        self.steps = ["Datei auswählen", "Textabschnitte prüfen", "Verarbeitung auswählen", "Ergebnisse überprüfen", "Speichern & Exportieren"]
        self.current_step = 0

        # Hauptlayout
        main_layout = QVBoxLayout()

        # Schritt-Visualisierung
        self.indicator_layout = QHBoxLayout()
        self.indicator_layout.setSpacing(10)

        self.step_circles = []
        self.step_lines = []

        for i in range(len(self.steps)):
            circle_label = QLabel(self.steps[i])
            circle_label.setFixedSize(140, 30)
            circle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle_label.setStyleSheet(self.get_circle_style(False))
            self.step_circles.append(circle_label)
            self.indicator_layout.addWidget(circle_label)

            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                line.setStyleSheet("background-color: lightgray; height: 2px;")
                line.setFixedWidth(50)
                self.step_lines.append(line)
                self.indicator_layout.addWidget(line)

        # Stacked Widget für die Seiten
        self.stacked_widget = QStackedWidget()

        self.selection_page = PdfSelectionPage(self)
        self.chunk_page = ChunkEditingPage(self)
        self.api_page = ApiSelectionPage(self)
        self.manual_page = ManualProcessingPage(self)
        self.card_page = CardSelectionPage(self)
        self.summary_page = SummaryPage(self)

        self.stacked_widget.addWidget(self.selection_page)
        self.stacked_widget.addWidget(self.chunk_page)
        self.stacked_widget.addWidget(self.api_page)
        self.stacked_widget.addWidget(self.manual_page)
        self.stacked_widget.addWidget(self.card_page)
        self.stacked_widget.addWidget(self.summary_page)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_next.clicked.connect(self.next_step)
        self.btn_next.setEnabled(False)
        self.btn_prev.setEnabled(False)

        # Button-Layout (Cancel links, Weiter/Zurück rechts)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_next)

        # Haupt-Layout zusammenfügen
        main_layout.addLayout(self.indicator_layout)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(button_layout)

        # Haupt-Widget setzen
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Ersten Schritt aktivieren
        self.update_stepper()

    def next_step(self):
        if self.current_step == 2:  # API-Seite
            if not self.api_page.show_cost_warning():
                return  # Abbrechen, wenn der Nutzer "Nein" gewählt hat

        if self.current_step == 2:  # API-Seite abgeschlossen → QnA-Generator erstellen
            api_type = "manual" if self.api_page.manual_radio.isChecked() else \
                    "openai" if self.api_page.openai_radio.isChecked() else "gemini"
            api_key = self.api_page.api_key_input.text() if api_type != "manual" else None
            
            self.qna_generator = QnAGenerator(api_type, api_key)
            logging.debug(f"✅ QnAGenerator für {api_type} initialisiert.")

        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            logging.debug(f"Wechsle zu Schritt {self.current_step}: {self.steps[self.current_step]}")
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_stepper()

            if self.current_step == 1:  # Zweite Seite (Chunks bearbeiten)
                logging.debug("DEBUG: Wechsle zu ChunkEditingPage – initializePage() aufrufen")
                self.chunk_page.initializePage()  

            if self.current_step == 3:  # Die richtige Seite für Karteikarten
                if self.api_page.manual_radio.isChecked():
                    logging.debug("DEBUG: Manuell-Modus gewählt → Wechsel zu ManualProcessingPage")
                    self.manual_page.initializePage()
                    self.stacked_widget.setCurrentWidget(self.manual_page)  # Manuell-Seite setzen
                else:
                    logging.debug("DEBUG: OpenAI oder Gemini gewählt → Wechsel zu CardSelectionPage")
                    self.card_page.initializePage()
                    self.stacked_widget.setCurrentWidget(self.card_page)  # QnA-Verarbeitung setzen

            if self.current_step == 4:  # Letzte Seite (Summary)
                logging.debug("DEBUG: Wechsle zur Zusammenfassung – SummaryPage")
                self.summary_page.initializePage()
                self.stacked_widget.setCurrentWidget(self.summary_page)  # Letzte Seite setzen


    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            logging.debug(f"Zurück zu Schritt {self.current_step}: {self.steps[self.current_step]}")
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_stepper()

    def update_stepper(self):
        """Aktualisiert den Stepper je nach Schritt."""
        for i, circle in enumerate(self.step_circles):
            if i <= self.current_step:
                circle.setStyleSheet(self.get_circle_style(True))
            else:
                circle.setStyleSheet(self.get_circle_style(False))

        for i, line in enumerate(self.step_lines):
            if i < self.current_step:
                line.setStyleSheet("background-color: #0078D4; height: 2px;")
            else:
                line.setStyleSheet("background-color: lightgray; height: 2px;")

        self.btn_prev.setEnabled(self.current_step > 0)
        #self.btn_next.setEnabled(self.current_step < len(self.steps) - 1)

    def get_circle_style(self, active):
        """Gibt das Styling für die Kreise zurück (Blau statt Lila)."""
        return """
            background-color: #0078D4; color: white; border-radius: 10px;
            font-weight: bold; border: 2px solid #0078D4;
        """ if active else """
            background-color: lightgray; color: black; border-radius: 10px;
            border: 2px solid gray;
        """

class PlainTextEdit(QTextEdit):
    def insertFromMimeData(self, source):
        """Verhindert das Einfügen von formatiertem Text."""
        if source.hasText():
            self.insertPlainText(source.text())  # Nur Klartext einfügen


from PyQt6.QtWidgets import QLineEdit, QGridLayout, QFileDialog

class PDFProcessingThread(QThread):
    logging.debug("PDFProcessingThread")
    progress_signal = pyqtSignal(int)  # Fortschrittsbalken-Update
    finished_signal = pyqtSignal(list)  # Gibt Chunks zurück

    def __init__(self, file_path, start_page, end_page):
        super().__init__()
        self.file_path = file_path
        self.start_page = start_page
        self.end_page = end_page

    def run(self):
        """Startet die PDF-Verarbeitung im Hintergrund."""
        parser = PDFParser(self.file_path)
        _ = parser.extract_text(start_page=self.start_page, end_page=self.end_page)
        chunks = parser.chunk_text(min_tokens=200, max_tokens=1000)

        # Chunks an Hauptthread zurückgeben
        self.finished_signal.emit(chunks)

class QnAProcessingThread(QThread):
    progress_signal = pyqtSignal(int, int)  # Fortschritt (aktuelle Zahl, Gesamtzahl)
    finished_signal = pyqtSignal(list)  # Ergebnis als Liste mit Karteikarten

    def __init__(self, chunks, api_type, api_key, prompt, system_prompt=None, tokens_per_question=150):
        super().__init__()
        self.chunks = chunks
        self.api_type = api_type
        self.api_key = api_key
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.tokens_per_question = tokens_per_question

    def run(self):
        """Startet die QnA-Generierung im Hintergrund."""
        from nlp.qna_generator import QnAGenerator  # Import hier, um Thread-Probleme zu vermeiden
        import tiktoken

        logging.debug("QnAProcessingThread gestartet.")
        logging.debug(f"API-Typ: {self.api_type}, Tokens pro Frage: {self.tokens_per_question}")

        qna_generator = QnAGenerator(api_type=self.api_type, api_key=self.api_key)

        enc = tiktoken.get_encoding("cl100k_base")
        cards = []

        logging.debug(f"Anzahl der Chunks: {len(self.chunks)}")

        for i, chunk in enumerate(self.chunks):
            token_count = len(enc.encode(chunk))
            num_questions = max(1, min(token_count // 150, 5))  # Mindestens 1, maximal 5 Fragen

            logging.debug(f"Chunk {i+1}/{len(self.chunks)} - Tokens: {token_count}, Fragen: {num_questions}")
            self.progress_signal.emit(i + 1, len(self.chunks))  # Fortschritt aktualisieren

            try:
                qna_pairs = qna_generator.generate_qna_pairs(chunk, num_questions=num_questions)

                if not qna_pairs:
                    logging.warning(f"⚠ Keine Fragen für Chunk {i+1} generiert.")
                    continue

                for question, answer in qna_pairs:
                    logging.debug(f"Frage {len(cards) + 1}: {question} | Antwort: {answer}")
                    cards.append({"question": question, "answer": answer, "selected": True})

            except Exception as e:
                logging.error(f"❌ Fehler bei der Verarbeitung von Chunk {i + 1}: {e}")
                cards.append({"question": "⚠ Fehler", "answer": str(e), "selected": False})

        logging.info(f"✅ Generierung abgeschlossen: {len(cards)} Karteikarten erstellt.")
        self.finished_signal.emit(cards)  # Ergebnis zurückgeben


class PdfSelectionPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setAcceptDrops(True)  # Drag & Drop aktivieren
        self.selected_file = None  # Datei speichern
        self.processing_thread = None  # Hintergrundprozess speichern
        
        # "Weiter"-Button beim Start deaktivieren
        self.wizard.btn_next.setEnabled(False)
        
        # Layout
        main_layout = QVBoxLayout()
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_widget.setFixedWidth(600)

        # Dropzone
        self.file_display = QLabel("📂 Ziehe eine Datei hierhin oder klicke auf 'Datei wählen'")
        self.file_display.setStyleSheet("border: 2px dashed gray; padding: 20px; font-size: 14px;")
        self.file_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_display.setFixedHeight(150)

        self.select_button = QPushButton("Datei wählen")
        self.select_button.setFixedWidth(180)
        self.select_button.clicked.connect(self.select_pdf)

        drop_layout = QVBoxLayout()
        drop_layout.addWidget(self.file_display)
        drop_layout.addWidget(self.select_button, alignment=Qt.AlignmentFlag.AlignCenter)

        content_layout.addLayout(drop_layout)

        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addSpacing(30) 
        content_layout.addWidget(line)
        content_layout.addSpacing(30) 

        # Seitenbereich (anfangs versteckt)
        self.page_section = QWidget()
        self.page_section.setVisible(False)  # Anfangs unsichtbar
        page_layout = QGridLayout(self.page_section)

        self.range_label = QLabel("Seitenbereich:")
        self.start_page_input = QLineEdit()
        self.start_page_input.setFixedWidth(50)
        self.end_page_input = QLineEdit()
        self.end_page_input.setFixedWidth(50)

        self.range_slider = QRangeSlider(Qt.Orientation.Horizontal)
        self.range_slider.valueChanged.connect(self.update_range_inputs)

        page_layout.addWidget(self.range_label, 0, 0)
        page_layout.addWidget(self.start_page_input, 0, 1)
        page_layout.addWidget(QLabel("bis"), 0, 2)
        page_layout.addWidget(self.end_page_input, 0, 3)
        page_layout.addWidget(self.range_slider, 1, 0, 1, 4)

        content_layout.addWidget(self.page_section)

        # Fortschrittsbalken
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)

        # Alles ins Hauptlayout setzen
        main_layout.addWidget(content_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def select_pdf(self):
        """Öffnet einen Dateidialog zur Auswahl einer PDF."""
        file_path, _ = QFileDialog.getOpenFileName(None, "PDF auswählen", "", "PDF Files (*.pdf)")
        if file_path:
            self.selected_file = file_path
            self.file_display.setText(f"📂 {file_path}")
            self.wizard.btn_next.setEnabled(True)

            # Seitenanzahl bestimmen
            doc = fitz.open(file_path)
            total_pages = doc.page_count
            doc.close()

            # Seitenbereich aktivieren & Werte setzen
            self.page_section.setVisible(True)
            self.range_slider.setMinimum(1)
            self.range_slider.setMaximum(total_pages)
            self.range_slider.setValue((1, total_pages))
            self.start_page_input.setText("1")
            self.end_page_input.setText(str(total_pages))

    def update_range_inputs(self, values):
        """Aktualisiert die Eingabefelder basierend auf dem Slider-Wert."""
        self.start_page_input.setText(str(values[0]))
        self.end_page_input.setText(str(values[1]))

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QScrollArea, QWidget

class ChunkEditingPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.processing_thread = None  # Speichert den Verarbeitungsprozess
        self.selected_chunks_label = QLabel("0 von 0 Chunks ausgewählt")  # Anzeige für die ausgewählten Chunks

        # Lade-Label
        self.label = QLabel("Lade Chunks...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Animierter Lade-Spinner (GIF)
        self.spinner_label = QLabel(self)
        self.spinner_movie = QMovie("loading.gif")  # Füge ein GIF mit einem Lade-Spinner hinzu
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setVisible(False)  # Anfangs versteckt

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spinner_label)  # Spinner ins Layout
        self.setLayout(layout)

    def initializePage(self):
        """Wird aufgerufen, wenn die Seite aktiv wird – startet die PDF-Verarbeitung."""
        logging.debug("ChunkEditingPage: Starte Verarbeitung der PDF.")
        self.start_processing()

    def start_processing(self):
        """Startet die PDF-Verarbeitung im Hintergrund mit Lade-Animation."""
        logging.debug("start_processing")
        selected_file = self.wizard.selection_page.selected_file
        start_page = int(self.wizard.selection_page.start_page_input.text())
        end_page = int(self.wizard.selection_page.end_page_input.text())

        if not selected_file:
            self.label.setText("❌ Fehler: Keine PDF ausgewählt")
            return

        self.wizard.chunks = []

        self.label.setText("⏳ Chunks werden erzeugt...")  # Lade-Text setzen
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()  # Animation starten

        if self.processing_thread:
            logging.debug("DEBUG: Alten Thread entfernen und neuen erstellen.")
            self.processing_thread.finished_signal.disconnect()
            self.processing_thread.quit()
            self.processing_thread.wait()
            self.processing_thread = None

        self.processing_thread = PDFProcessingThread(selected_file, start_page, end_page)
        self.processing_thread.finished_signal.connect(self.on_processing_finished)
        logging.debug("DEBUG: Neuer Thread wird gestartet.")
        self.processing_thread.start()

    def on_processing_finished(self, chunks):
        """Wird aufgerufen, wenn die Verarbeitung abgeschlossen ist."""
        self.spinner_movie.stop()
        self.spinner_label.setVisible(False)

        if not chunks:
            self.label.setText("❌ Keine Chunks gefunden.")
            return

        self.wizard.chunks = chunks
        self.label.setText(f"✅ Es wurden {len(chunks)} Chunks erzeugt.")

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.chunk_widgets = []

        for i, chunk in enumerate(chunks):
            chunk_layout = QHBoxLayout()
            text_edit = QTextEdit(chunk)
            text_edit.setFixedHeight(160)
            text_edit.setStyleSheet("background-color: #424242; border: 1px solid #d0d0d0; padding: 5px;")
            
            check_box = QCheckBox("Nutzen")
            check_box.setChecked(True)
            check_box.stateChanged.connect(self.update_selected_chunks_label)

            reset_button = QPushButton("Zurücksetzen")
            reset_button.clicked.connect(lambda _, te=text_edit, c=chunk: te.setText(c))

            chunk_layout.addWidget(check_box)
            chunk_layout.addWidget(text_edit)
            chunk_layout.addWidget(reset_button)
            
            scroll_layout.addLayout(chunk_layout)
            self.chunk_widgets.append((text_edit, check_box))

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        self.layout().addWidget(scroll_area)
        self.layout().addWidget(self.selected_chunks_label)
        self.update_selected_chunks_label()

    def update_selected_chunks_label(self):
        """Aktualisiert die Anzeige der Anzahl der ausgewählten Chunks."""
        total_chunks = len(self.chunk_widgets)
        selected_chunks = sum(1 for _, check_box in self.chunk_widgets if check_box.isChecked())
        self.selected_chunks_label.setText(f"{selected_chunks} von {total_chunks} Chunks ausgewählt")


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QLineEdit, QSpinBox, QTextEdit, QGroupBox, QHBoxLayout, QButtonGroup
from PyQt6.QtCore import Qt

class ApiSelectionPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard

        # Hauptlayout
        layout = QVBoxLayout()

        # Überschrift
        title_label = QLabel("Wie sollen die Chunks verarbeitet werden?")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # API-Auswahl (OpenAI, Gemini, Manuell)
        api_group_box = QGroupBox("API Auswahl")
        api_layout = QVBoxLayout()

        self.api_group = QButtonGroup(self)  # Gruppiert die Radio-Buttons

        self.manual_radio = QRadioButton("Manuell (keine KI)")
        self.openai_radio = QRadioButton("OpenAI (GPT-4)")
        self.gemini_radio = QRadioButton("Gemini (Google AI)")

        self.api_group.addButton(self.manual_radio)
        self.api_group.addButton(self.openai_radio)
        self.api_group.addButton(self.gemini_radio)

        self.manual_radio.setChecked(True)  # Manuell als Standardauswahl

        api_layout.addWidget(self.manual_radio)
        api_layout.addWidget(self.openai_radio)
        api_layout.addWidget(self.gemini_radio)
        api_group_box.setLayout(api_layout)

        layout.addWidget(api_group_box)

        # API-Key-Eingabe (nur wenn OpenAI oder Gemini gewählt)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API-Schlüssel hier eingeben")
        layout.addWidget(self.api_key_input)

        # Prompt-Bearbeitung
        self.system_prompt_label = QLabel("System Message (nur OpenAI)")
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("System Message für OpenAI eingeben...")

        self.dynamic_prompt_label = QLabel("Dynamischer Prompt")
        self.dynamic_prompt_edit = QTextEdit()
        self.dynamic_prompt_edit.setPlaceholderText("Dynamischer Prompt oder eigenes Prompt eingeben...")

        layout.addWidget(self.system_prompt_label)
        layout.addWidget(self.system_prompt_edit)
        layout.addWidget(self.dynamic_prompt_label)
        layout.addWidget(self.dynamic_prompt_edit)

        # Tokens pro Frage
        token_label = QLabel("Tokens pro Frage:")
        self.token_input = QSpinBox()
        self.token_input.setMinimum(50)
        self.token_input.setMaximum(1000)
        self.token_input.setValue(150)

        token_layout = QHBoxLayout()
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)

        # Kostenberechnung (Rot färben)
        self.cost_label = QLabel("Geschätzte Kosten: Keine")
        self.cost_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.cost_label)

        # Signale verbinden
        self.openai_radio.toggled.connect(self.update_ui)
        self.gemini_radio.toggled.connect(self.update_ui)
        self.manual_radio.toggled.connect(self.update_ui)
        self.token_input.valueChanged.connect(self.update_cost_estimate)

        self.setLayout(layout)
        self.update_ui()
        self.load_prompts()

    def update_ui(self):
        """Aktualisiert die UI-Elemente basierend auf der API-Auswahl."""
        if self.manual_radio.isChecked():
            self.api_key_input.setEnabled(False)
            self.api_key_input.setPlaceholderText("Manuelle Verarbeitung benötigt keinen API-Schlüssel")
            self.system_prompt_label.setVisible(False)
            self.system_prompt_edit.setVisible(False)
            self.cost_label.setText("Geschätzte Kosten: Keine")
        else:
            self.api_key_input.setEnabled(True)
            self.api_key_input.setPlaceholderText("API-Schlüssel hier eingeben")
            self.cost_label.setText("Geschätzte Kosten: 0.00 USD")

        if self.openai_radio.isChecked():
            self.system_prompt_label.setVisible(True)
            self.system_prompt_edit.setVisible(True)
        else:
            self.system_prompt_label.setVisible(False)
            self.system_prompt_edit.setVisible(False)

        self.update_cost_estimate()
        self.load_prompts()

    def update_cost_estimate(self):
        """Berechnet die geschätzten Kosten basierend auf der API-Auswahl und Token-Anzahl."""
        if self.manual_radio.isChecked():
            self.cost_label.setText("Geschätzte Kosten: Keine")
            return

        cost_per_token = 0.002  # Beispielwert für GPT-4
        tokens_per_question = self.token_input.value()
        total_cost = (tokens_per_question / 1000) * cost_per_token

        self.cost_label.setText(f"Geschätzte Kosten: {total_cost:.4f} USD")

    def load_prompts(self):
        """Lädt die Standard-Prompts aus den JSON-Dateien je nach API-Auswahl."""
        prompt_path = "data/prompts"

        if self.openai_radio.isChecked():
            system_prompt_file = os.path.join(prompt_path, "system_message.json")
            dynamic_prompt_file = os.path.join(prompt_path, "dynamic_prompt_openai.json")

            self.system_prompt_edit.setText(self.load_json(system_prompt_file))
            self.dynamic_prompt_edit.setText(self.load_json(dynamic_prompt_file))

        elif self.gemini_radio.isChecked():
            dynamic_prompt_file = os.path.join(prompt_path, "dynamic_prompt_gemini.json")
            self.system_prompt_edit.setText("")
            self.dynamic_prompt_edit.setText(self.load_json(dynamic_prompt_file))

        elif self.manual_radio.isChecked():
            dynamic_prompt_file = os.path.join(prompt_path, "dynamic_prompt_manual.json")
            self.system_prompt_edit.setText("")
            self.dynamic_prompt_edit.setText(self.load_json(dynamic_prompt_file))

    def load_json(self, file_path):
        """Lädt JSON-Datei und gibt den richtigen Inhalt als String zurück."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                # Wenn es eine System Message ist, nehme "content"
                if "system_message" in file_path:
                    return data.get("content", "")

                # Sonst gehe von einem dynamischen Prompt aus, nehme "template"
                return data.get("template", "")

        except (FileNotFoundError, json.JSONDecodeError):
            return "⚠ Fehler beim Laden des Prompts"

    def show_cost_warning(self):
        """Zeigt eine Warnung an, wenn eine API mit Kosten genutzt wird."""
        if self.manual_radio.isChecked():
            return True  # Kein Hinweis nötig

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Kostenhinweis")
        msg.setText("Die gewählte API kann Kosten verursachen. Möchtest du trotzdem fortfahren?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        response = msg.exec()

        return response == QMessageBox.StandardButton.Yes

class ManualProcessingPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.current_chunk_index = 0
        self.qna_pairs = {}  # Frage-Antwort-Paare
        self.edited_prompts = {}  # Speichert bearbeitete Prompts pro Chunk

        # Überschrift
        self.title_label = QLabel("Manuelle QnA-Erstellung")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Prompt-Anzeige (bearbeitbar)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Hier erscheint der generierte Prompt mit dem Chunk...")
        self.prompt_edit.setReadOnly(False)  # Prompt bearbeitbar machen

        # Buttons für Kopieren & Zurücksetzen
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("📋 Kopieren")
        self.reset_button = QPushButton("🔄 Zurücksetzen")
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.reset_button)

        # Antwort-Eingabe
        self.answer_edit = PlainTextEdit()  # Verwende PlainTextEdit für einheitliche Formatierung
        self.answer_edit.setPlaceholderText("Hier die generierte Antwort einfügen...")
        self.answer_edit.textChanged.connect(self.save_qna_pair)  # 🔥 Speichert Live!

        # Navigations-Buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("⬅ Vorheriger Chunk")
        self.next_button = QPushButton("Nächster Chunk ➡")
        self.preview_button = QPushButton("🔍 Vorschau")  # Vorschau-Button

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.preview_button)
        nav_layout.addWidget(self.next_button)

        # Layout zusammenstellen
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.prompt_edit)
        layout.addLayout(button_layout)
        layout.addWidget(self.answer_edit)
        layout.addLayout(nav_layout)
        self.setLayout(layout)

        # Button-Verbindungen
        self.copy_button.clicked.connect(self.copy_prompt)
        self.reset_button.clicked.connect(self.reset_prompt)
        self.prev_button.clicked.connect(self.prev_chunk)
        self.next_button.clicked.connect(self.next_chunk)
        self.preview_button.clicked.connect(self.show_preview)  # Vorschau

    def initializePage(self):
        self.load_chunk(0)

    def load_chunk(self, index):
        """Lädt den ausgewählten Chunk und setzt die gespeicherte Antwort zurück ins Eingabefeld."""
        if 0 <= index < len(self.wizard.chunks):
            self.current_chunk_index = index

            # 🟢 Prüfen, ob es eine bearbeitete Version des Prompts gibt
            if index in self.edited_prompts:
                prompt = self.edited_prompts[index]
            else:
                chunk = self.wizard.chunks[index]
                prompt_template = self.wizard.qna_generator.load_dynamic_prompt()
                enc = tiktoken.get_encoding("cl100k_base")
                token_count = len(enc.encode(chunk))
                tokens_per_question = self.wizard.api_page.token_input.value()
                num_questions = max(1, token_count // tokens_per_question)
                prompt = prompt_template.format(chunk=chunk, num_questions=num_questions)

            self.prompt_edit.setText(prompt)

            # 🟢 Antwort-Feld leeren
            self.answer_edit.clear()

            # 🔥 Falls eine gespeicherte Antwort existiert → Wiederherstellen!
            if hasattr(self.wizard, "manual_answers"):
                for entry in self.wizard.manual_answers:
                    if entry["chunk"] == index:
                        logging.debug(f"🔄 Geladene Antwort für Chunk {index}: {entry['answer']}")
                        self.answer_edit.setText(entry["answer"])
                        break  # Sobald wir die Antwort gefunden haben, abbrechen

            # 🟢 Buttons für Vor/Zurück aktivieren oder deaktivieren
            self.prev_button.setEnabled(index > 0)
            self.next_button.setEnabled(index < len(self.wizard.chunks) - 1)

    def copy_prompt(self):
        prompt_text = self.prompt_edit.toPlainText()
        pyperclip.copy(prompt_text)

    def reset_prompt(self):
        if self.current_chunk_index in self.edited_prompts:
            del self.edited_prompts[self.current_chunk_index]
        self.load_chunk(self.current_chunk_index)

    def save_qna_pair(self):
        """Speichert die aktuelle Antwort automatisch."""
        response_text = self.answer_edit.toPlainText().strip()
        prompt_text = self.prompt_edit.toPlainText().strip()

        if not response_text:
            return  # Falls das Feld leer ist, nichts speichern

        # Falls `manual_answers` nicht existiert, erstellen
        if not hasattr(self.wizard, "manual_answers"):
            self.wizard.manual_answers = []

        # Falls bereits ein Eintrag für diesen Chunk existiert → ersetzen
        for item in self.wizard.manual_answers:
            if item["chunk"] == self.current_chunk_index:
                item["answer"] = response_text
                logging.debug(f"🔄 Antwort für Chunk {self.current_chunk_index} aktualisiert.")
                return

        # Sonst neu hinzufügen
        self.wizard.manual_answers.append({"chunk": self.current_chunk_index, "answer": response_text})
        logging.debug(f"✅ Antwort für Chunk {self.current_chunk_index} gespeichert.")

    def prev_chunk(self):
        if self.current_chunk_index > 0:
            self.load_chunk(self.current_chunk_index - 1)

    def next_chunk(self):
        if self.current_chunk_index < len(self.wizard.chunks) - 1:
            self.load_chunk(self.current_chunk_index + 1)

    def show_preview(self):
        """Zeigt eine Vorschau der extrahierten Fragen & Antworten."""
        response_text = self.answer_edit.toPlainText().strip()

        if not response_text:
            QMessageBox.warning(self, "Fehler", "Keine Antwort vorhanden.")
            return

        qna_pairs = self.wizard.qna_generator.extract_qna_pairs(response_text)

        if not qna_pairs:
            QMessageBox.warning(self, "Vorschau", "⚠ Keine Frage-Antwort-Paare gefunden!")
            return

        preview_text = "\n\n".join([f"❓ {q['question']}\n💬 {q['answer']}" for q in qna_pairs])
        QMessageBox.information(self, "Vorschau der generierten Fragen", preview_text)


class CardSelectionPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.processing_thread = None  # Hintergrundprozess für die QnA-Erstellung
        self.cards = []  # Speichert die generierten Karteikarten

        # Ladeanimation
        self.label = QLabel("Karteikarten werden generiert...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner_label = QLabel(self)
        self.spinner_movie = QMovie("loading.gif")
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setVisible(False)

        # Fortschrittsanzeige
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.progress_label)
        self.setLayout(layout)

    def initializePage(self):
        """Startet die Verarbeitung der Chunks."""
        logging.debug("CardSelectionPage: Starte Verarbeitung der Chunks.")

        self.cards = []  # Reset vorherige Karten
        self.label.setText("⏳ Karteikarten werden generiert...")
        self.progress_label.setText("0 von 0 verarbeitet")
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        # Daten aus vorheriger Seite abrufen
        chunks = self.wizard.chunks
        api_type = "manual" if self.wizard.api_page.manual_radio.isChecked() else "openai" if self.wizard.api_page.openai_radio.isChecked() else "gemini"
        api_key = self.wizard.api_page.api_key_input.text()
        prompt = self.wizard.api_page.dynamic_prompt_edit.toPlainText()
        system_prompt = self.wizard.api_page.system_prompt_edit.toPlainText() if api_type == "openai" else None
        tokens_per_question = self.wizard.api_page.token_input.value()

        logging.debug(f"API-Typ: {api_type}, Tokens pro Frage: {tokens_per_question}, API-Key eingegeben: {'Ja' if api_key else 'Nein'}")
        logging.debug(f"Chunks zum Verarbeiten: {len(chunks)}")

        # Thread starten
        self.processing_thread = QnAProcessingThread(
            self.wizard.chunks, api_type, self.wizard.api_page.api_key_input.text(),
            self.wizard.api_page.dynamic_prompt_edit.toPlainText(),
            self.wizard.api_page.system_prompt_edit.toPlainText() if api_type == "openai" else None,
            self.wizard.api_page.token_input.value()
        )
        self.processing_thread.progress_signal.connect(self.update_progress)
        self.processing_thread.finished_signal.connect(self.on_processing_finished)
        self.processing_thread.start()

    def update_progress(self, current, total):
        """Aktualisiert die Fortschrittsanzeige."""
        logging.debug(f"Fortschritt: {current}/{total} verarbeitet.")
        self.progress_label.setText(f"{current} von {total} Chunks verarbeitet...")

    def on_processing_finished(self, cards):
        """Verarbeitung abgeschlossen, zeigt die generierten Karteikarten an."""
        logging.info(f"✅ Verarbeitung abgeschlossen: {len(cards)} Karteikarten erhalten.")

        self.spinner_movie.stop()
        self.spinner_label.setVisible(False)
        self.label.setText("✅ Karteikarten wurden generiert.")

        if not cards:
            logging.warning("⚠ Keine Karteikarten generiert!")
            QMessageBox.warning(self, "Fehler", "Keine Karteikarten wurden generiert.")
            return

        self.wizard.cards = cards  # Speichert die generierten Karten

        # Layout für Kartenanzeige vorbereiten
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.card_widgets = []
        for i, card in enumerate(cards):
            logging.debug(f"Karteikarte {i+1}: Frage: {card['question']} | Antwort: {card['answer']}")

            card_layout = QHBoxLayout()

            question_edit = QTextEdit(card["question"])
            question_edit.setFixedHeight(100)

            answer_edit = QTextEdit(card["answer"])
            answer_edit.setFixedHeight(100)

            check_box = QCheckBox("Nutzen")
            check_box.setChecked(card["selected"])
            check_box.stateChanged.connect(self.update_selected_cards_label)

            reset_button = QPushButton("Zurücksetzen")
            reset_button.clicked.connect(lambda _, q=question_edit, a=answer_edit, c=card: self.reset_card(q, a, c))

            card_layout.addWidget(check_box)
            card_layout.addWidget(question_edit)
            card_layout.addWidget(answer_edit)
            card_layout.addWidget(reset_button)

            scroll_layout.addLayout(card_layout)
            self.card_widgets.append((question_edit, answer_edit, check_box))

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)

        self.layout().addWidget(scroll_area)
        self.update_selected_cards_label()

    def reset_card(self, question_edit, answer_edit, card):
        """Setzt die Karteikarte auf den Originalzustand zurück."""
        logging.debug(f"Karteikarte zurückgesetzt: {card['question']}")
        question_edit.setText(card["question"])
        answer_edit.setText(card["answer"])

    def update_selected_cards_label(self):
        """Aktualisiert die Anzahl der ausgewählten Karteikarten."""
        total_cards = len(self.card_widgets)
        selected_cards = sum(1 for _, _, check_box in self.card_widgets if check_box.isChecked())
        logging.debug(f"{selected_cards} von {total_cards} Karteikarten ausgewählt.")
        self.label.setText(f"{selected_cards} von {total_cards} Karteikarten ausgewählt")


class SummaryPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.layout = QVBoxLayout()
        self.label = QLabel("Hier können die Karteikarten gespeichert werden.")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def initializePage(self):
        """Initialisiert die Seite – prüft, ob manuelle Verarbeitung nötig ist."""
        if hasattr(self.wizard, "manual_answers") and self.wizard.manual_answers:
            self.process_manual_qna_pairs()
        else:
            self.label.setText("✅ Alle Karteikarten wurden generiert.")

    def process_manual_qna_pairs(self):
        """Verarbeitet manuelle Antworten mit Fortschrittsanzeige."""
        logging.debug("SummaryPage: Starte Verarbeitung der manuellen Antworten...")
        
        manual_answers = self.wizard.manual_answers
        total_answers = len(manual_answers)
        processed_cards = []

        # Fortschrittsdialog anzeigen
        progress = QProgressDialog("Verarbeite Antworten...", "Abbrechen", 0, total_answers, self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(500)  # Verhindert zu schnelles Aufpoppen
        progress.setValue(0)

        for i, entry in enumerate(manual_answers):
            if progress.wasCanceled():
                logging.warning("⚠ Verarbeitung abgebrochen!")
                return

            qna_pairs = self.wizard.qna_generator.extract_qna_pairs(entry["answer"])
            if qna_pairs:
                processed_cards.extend([{"question": q["question"], "answer": q["answer"], "selected": True} for q in qna_pairs])
            else:
                logging.warning(f"⚠ Fehlerhafte Eingabe erkannt: {entry}")

            progress.setValue(i + 1)  # Fortschritt aktualisieren

        progress.close()

        if processed_cards:
            self.wizard.cards = processed_cards  # Speichert die generierten Karteikarten
            logging.info(f"✅ {len(processed_cards)} manuelle QnA-Paare erfolgreich verarbeitet!")
            self.label.setText(f"✅ {len(processed_cards)} Karteikarten bereit zum Speichern.")
        else:
            QMessageBox.warning(self, "Fehler", "⚠ Keine validen QnA-Paare gefunden!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Stepper()
    window.show()
    sys.exit(app.exec())
