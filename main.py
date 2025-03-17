from PyQt6.QtWidgets import QApplication
import sys
from app import DevSupportApp
from utils.debug import debug_print

def main():
    debug_print("Starting application")
    app = QApplication(sys.argv)
    window = DevSupportApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
