import sys
from PyQt6.QtWidgets import QApplication
from gui import Stepper

def main():
    app = QApplication(sys.argv)
    window = Stepper()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
