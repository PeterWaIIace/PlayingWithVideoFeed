import sys 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore    import QRect
from PyQt5.QtGui     import QPalette, QColor

from videoFeed import VidFeed

class VideoDisplay(QWidget):

    def __init__(self):
        super().__init__()

        self.setGeometry(QRect(530, 20, 256, 192))
        self.setObjectName("cameraWindow")
        self.setAttribute(0, 1); # AA_ImmediateWidgetCreation == 0
        self.setAttribute(3, 1); # AA_NativeWindow == 3
        
        self.setStyleSheet("background-color: black")

    def get_id(self):
        return self.winId()

class MainWindow(QWidget):
    
    def __init__(self,display):
        super().__init__()

        self.setWindowTitle('PyView')
        self.setGeometry(QRect(530, 20, 256, 192))

        layout = QGridLayout()
        layout.addWidget(display, 0, 1,3, 3)
        layout.addWidget(QPushButton('Button0'), 0, 0)
        layout.addWidget(QPushButton('Button0'), 1, 0)
        
        self.setLayout(layout)

app = QApplication(sys.argv)


display = VideoDisplay()
window = MainWindow(display)
window.show()

vid = VidFeed(display.get_id())
vid.startPrev()

sys.exit(app.exec_())

