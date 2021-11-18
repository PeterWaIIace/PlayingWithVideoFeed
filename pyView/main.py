import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from src.PvWindow import PyViewMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PyViewMainWindow()
    window.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint |
                          Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint |
                          Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint )
    window.show()

    sys.exit(app.exec_())
