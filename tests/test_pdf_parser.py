from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt

class Stepper(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Stepper Navigation")
        self.setGeometry(100, 100, 700, 400)

        # Schritt-Namen
        self.steps = ["Schritt 1", "Schritt 2", "Schritt 3", "Schritt 4", "Schritt 5"]
        self.current_step = 0

        # Hauptlayout
        main_layout = QVBoxLayout()

        # Indikator-Layout (für Kreise & Linien)
        self.indicator_layout = QHBoxLayout()
        self.indicator_layout.setSpacing(10)

        self.step_circles = []  # Speichert die Kreis-Labels
        self.step_lines = []  # Speichert die Linien
        for i in range(len(self.steps)):
            # Kreis für den Schritt mit Text "Schritt X"
            circle_label = QLabel(self.steps[i])
            circle_label.setFixedSize(80, 30)
            circle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle_label.setStyleSheet(self.get_circle_style(False))
            self.step_circles.append(circle_label)
            self.indicator_layout.addWidget(circle_label)

            # Linie zwischen den Schritten (außer beim letzten)
            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                line.setStyleSheet("background-color: lightgray; height: 2px;")
                line.setFixedWidth(50)
                self.step_lines.append(line)
                self.indicator_layout.addWidget(line)

        # Stacked Widget für die Schritte
        self.stacked_widget = QStackedWidget()
        for i, step_name in enumerate(self.steps):
            step_page = QWidget()
            step_layout = QVBoxLayout()
            step_layout.addWidget(QLabel(f"Content for {step_name}"), alignment=Qt.AlignmentFlag.AlignCenter)
            step_page.setLayout(step_layout)
            self.stacked_widget.addWidget(step_page)

        # Navigation Buttons
        self.btn_prev = QPushButton("Previous")
        self.btn_next = QPushButton("Next")

        self.btn_prev.clicked.connect(self.prev_step)
        self.btn_next.clicked.connect(self.next_step)
        self.btn_prev.setEnabled(False)  # Anfangs deaktiviert

        # Button-Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_next)

        # Alles ins Hauptlayout setzen
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
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_stepper()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_stepper()

    def update_stepper(self):
        # Indikatoren aktualisieren (jetzt auch vergangene Schritte farbig!)
        for i, circle in enumerate(self.step_circles):
            if i <= self.current_step:  # Alle bisherigen Schritte markieren
                circle.setStyleSheet(self.get_circle_style(True))
            else:
                circle.setStyleSheet(self.get_circle_style(False))

        # Linien aktualisieren (hervorgehoben für vergangene Schritte)
        for i, line in enumerate(self.step_lines):
            if i < self.current_step:
                line.setStyleSheet("background-color: purple; height: 2px;")
            else:
                line.setStyleSheet("background-color: lightgray; height: 2px;")

        # Button-Zustände aktualisieren
        self.btn_prev.setEnabled(self.current_step > 0)
        self.btn_next.setEnabled(self.current_step < len(self.steps) - 1)

    def get_circle_style(self, active):
        """Gibt das Styling für die Schritt-Kreise zurück."""
        if active:
            return """
                background-color: purple; 
                color: white; 
                border-radius: 10px; 
                font-weight: bold;
                border: 2px solid purple;
            """
        else:
            return """
                background-color: lightgray; 
                color: black; 
                border-radius: 10px;
                border: 2px solid gray;
            """

if __name__ == "__main__":
    app = QApplication([])
    window = Stepper()
    window.show()
    app.exec()
