import sys

from os import listdir
from os.path import isfile, join

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QScrollArea, QWidget
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame


class savedFrame(QFrame):

    FRAME_WIDTH = 140

    def __init__(self, path, title, display):
        super().__init__()

        self.display = display
        self.__init__UI(path, title)

    def __init__UI(self, path, title):

        name = QLabel()
        name.setText(title)
        name.setFixedWidth(self.FRAME_WIDTH)
        name.setAlignment(Qt.AlignCenter)

        flayout = QVBoxLayout()
        picture = Picture(join(path, title), self.display)
        picture.setFixedWidth(self.FRAME_WIDTH)
        picture.setAlignment(Qt.AlignCenter)

        flayout.addWidget(name)
        flayout.addWidget(picture)
        self.setLayout(flayout)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)
        self.setMidLineWidth(1)

        self.setContentsMargins(10, 3, 10, 3)


class Picture(QLabel):

    def __init__(self, title, display):
        super().__init__()

        self.display = display
        self.__init__UI(title)

    def __init__UI(self, title):

        self.org_pixmap = QPixmap(title)

        self.pixmap = self.org_pixmap
        self.pixmap = self.pixmap.scaledToWidth(128)
        self.pixmap = self.pixmap.scaledToHeight(64)

        self.setPixmap(self.pixmap)

        self.setMouseTracking(True)

    def sizeHint(self):
        return QSize(self.width(), self.height())

    def mousePressEvent(self, event):
        print("mouse pressed")
        self.display.changeView(self.org_pixmap)


class SavedFrames(QHBoxLayout):

    PICTURE_NAME_PREFIX = "frame"
    PATH_TO_FRAMES = "saved_frames/"
    INSERT_IN_FRONT = 0

    def __init__(self, display):
        super().__init__()

        self.display = display
        self.saved_items = dict()

        self.__init__UI()
        self.update_images()

    def __init__UI(self):
        self.scroll = QScrollArea()

        self.addWidget(self.scroll)
        self.scroll.setFixedHeight(148)
        self.scroll.setWidgetResizable(True)

        self.scrollContent = QWidget(self.scroll)
        self.scrollLayout = QHBoxLayout(self.scrollContent)

        self.scrollLayout.setAlignment(Qt.AlignLeft)
        self.scrollLayout.setSpacing(0)

        self.scrollContent.setLayout(self.scrollLayout)

        self.scroll.setWidget(self.scrollContent)

    def update_images(self):
        images = [
            f for f in listdir(
                self.PATH_TO_FRAMES) if isfile(
                join(
                    self.PATH_TO_FRAMES,
                    f))]

        self.__find_image(images)

    def __find_image(self, images):
        for image in images:
            if image.startswith(self.PICTURE_NAME_PREFIX):
                self.__add_image(image)
            else:
                pass

    def __add_image(self, image):
        if(image not in self.saved_items):
            self.saved_items[image] = savedFrame(
                self.PATH_TO_FRAMES, image, self.display)

            self.scrollLayout.insertWidget(
                self.INSERT_IN_FRONT,
                self.saved_items[image]
            )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QWidget()

    window.setLayout(SavedFrames(window))
    window.show()

    sys.exit(app.exec_())
