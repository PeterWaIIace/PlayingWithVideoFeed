import sys

from os import listdir
from os.path import isfile, join

from PyQt5.QtCore    import Qt,QSize
from PyQt5.QtWidgets import QHBoxLayout,QScrollArea,QWidget,QLabel, QApplication
from PyQt5.QtGui     import QPixmap
from PyQt5.QtWidgets import QPushButton

class savedFrame(QLabel):

    def __init__(self,title,display):
        super().__init__()

        self.setText(title)

        self.org_pixmap = QPixmap(title)
        self.pixmap     = self.org_pixmap
        self.pixmap     = self.pixmap.scaledToWidth(128)
        self.pixmap     = self.pixmap.scaledToHeight(64)

        self.setFixedHeight(self.pixmap.height())
        self.setFixedWidth(self.pixmap.width())

        self.setContentsMargins(10,0,0,0)
        self.setPixmap(self.pixmap)

        self.display = display
        self.setMouseTracking(True)

    def sizeHint(self):
        return QSize(self.width(), self.height())

    def mousePressEvent(self, event):
        print("mouse pressed")
        self.display.changeView(self.org_pixmap)

class SavedFrames(QHBoxLayout):

    def __init__(self,display):
        super().__init__()

        self.display = display
        self.saved_items = []
        self.scroll = QScrollArea()
        
        self.addWidget(self.scroll)
        self.scroll.setFixedHeight(128)
        self.scroll.setWidgetResizable(True)

        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QHBoxLayout(self.scrollContent)

        self.scrollContent.setLayout(self.scrollLayout)
        
        self.scrollLayout.setAlignment(Qt.AlignLeft)
        self.scrollLayout.setSpacing(0)

        self.update_thumbnails()
        self.scroll.setWidget(self.scrollContent)

    def update_thumbnails(self):
        items = [f for f in listdir("saved_frames/") if isfile(join("saved_frames/", f))]

        for item in items:
            if("frame" in item and not ("dummy" in item)):
                if(item not in self.saved_items):
                    self.saved_items.append(item)
                    self.scrollLayout.insertWidget(0,savedFrame("saved_frames/"+item,self.display))
            else:
                pass


if __name__=="__main__":

    app = QApplication(sys.argv)
    window = QWidget()

    window.setLayout(SavedFrames())

    window.show()


    sys.exit(app.exec_())