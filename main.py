# project/main.py
import sys
from PySide6.QtWidgets import QApplication
from folder_creation import FolderCreationApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderCreationApp()
    window.show()
    sys.exit(app.exec())