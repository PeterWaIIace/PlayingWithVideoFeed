import sys
import numpy as np
from PyQt5 import QtGui
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QRect, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPainter, QPixmap, QImage, QPen

from src.PvZoom import ZoomScope, ROI, Point
from src.PvFeed import VidFeed
from src.PvFrames import SavedFrames


class VideoFeedThread(QThread):
    '''
    
    Thread for reading frames from gstreamer appsink.

    '''

    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        self.cap = VidFeed()
        self.cap.startPrev()

        self.__run = True
        while True:
            if self.cap.isFrameReady() and self.__run:
                np_img = self.cap.getFrame()
                self.change_pixmap_signal.emit(np_img)

    def taskStop(self):
        self.__run = False

    def taskStart(self):
        self.__run = True


class VideoDisplay(QLabel):

    '''

    Main GUI display element.

    '''

    def __init__(self):
        super().__init__()

        self.setObjectName("cameraWindow")
        self.setAttribute(0, 1)  # AA_ImmediateWidgetCreation == 0
        self.setAttribute(3, 1)  # AA_NativeWindow == 3

        self.Anchron = None
        self.Cursor = None

        self.draw_zoom = False
        self.buffor_frame = None
        self.cp_buffor_frame = None

        self.__init__UI()

    def __init__UI(self):
        self.Region = ROI()
        self.Zoom = ZoomScope()

        self.pxman = QPixmap(640, 480)
        self.pxman.fill(QColor('darkGray'))
        self.setPixmap(self.pxman)

        self.thread = VideoFeedThread()
        self.thread.change_pixmap_signal.connect(self.__updateImage)
        self.thread.start()

        self.setMouseTracking(True)

    @pyqtSlot(np.ndarray)
    def __updateImage(self, np_img):
        qt_img = self.__convertFrame(np_img)
        self.buffor_frame = qt_img.scaled(640, 480, Qt.KeepAspectRatio)
        self.cp_buffor_frame = self.buffor_frame
        self.update()

    def __convertFrame(self, frame):
        """
        Convert from an numpy image to QPixmap

        """
        Qt_format = QImage(
            frame,
            frame.shape[1],
            frame.shape[0],
            QtGui.QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(Qt_format)

    def stop(self):
        """

        Stop videofeed thread.

        """

        self.thread.taskStop()

    def start(self):
        """

        Resume videofeed thread. 

        """

        self.buffor_frame = self.cp_buffor_frame
        self.thread.taskStart()

    def reset(self):
        """

        Reset set and applied zoom. 

        """

        self.Zoom.reset(
            self.rect().width(),
            self.rect().height()
        )
        self.update()

    def saveView(self):
        """

        Save current frame. 

        """

        if self.Zoom.isSet():
            view = self.Zoom.apply(self.buffor_frame, self.rect())
        else:
            view = self.buffor_frame

        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        return view.save(f"saved_frames/frame_{time}.png")

    def changeView(self, view):
        """

        Change currently browsed frame. 

        """

        self.stop()
        self.reset()
        self.parent().btnChngStateFreezeView()
        self.cp_buffor_frame = self.buffor_frame
        self.buffor_frame = view
        self.update()

    def draw(self, painter, x_anchron, y_anchron, curr_x, curr_y):
        """
        
        Draw rectangle based on 2 points.

        """

        pen = QPen(Qt.red, 3)
        painter.setPen(pen)
        painter.drawLine(x_anchron, y_anchron, x_anchron, curr_y)
        painter.drawLine(x_anchron, y_anchron, curr_x, y_anchron)
        painter.drawLine(curr_x, curr_y, x_anchron, curr_y)
        painter.drawLine(curr_x, curr_y, curr_x, y_anchron)


    # Below you can find PyQT events handlers 

    def paintEvent(self, event):
        if not (self.buffor_frame is None):
            if self.Zoom.isSet():
                frame = self.Zoom.apply(self.buffor_frame, self.rect())
            else:
                frame = self.buffor_frame

            painter = QPainter(self)
            painter.drawPixmap(self.rect(), frame)

            if self.draw_zoom:
                self.draw(
                    painter,
                    self.Anchron.x(),
                    self.Anchron.y(),
                    self.Cursor.x(),
                    self.Cursor.y())

    def mousePressEvent(self, event):
        self.Anchron = Point(event.x(), event.y())

        if(self.draw_zoom):
            self.draw_zoom = False

            self.Region.addPoint(self.Anchron)

            self.Zoom.set(
                self.Region,
                self.rect()
            )
        else:
            self.Region.addPoint(self.Anchron)
            self.Cursor = Point(event.x(), event.y())
            self.draw_zoom = True
        self.update()

    def mouseMoveEvent(self, event):
        if(self.draw_zoom):
            self.Cursor = Point(event.x(), event.y())
            self.update()


class PyViewMainWindow(QWidget):

    '''

    PyView Main window. It should be invoked in main to start entire application

    '''

    def __init__(self):
        super().__init__()
        self.__init__UI()
    
    def __init__UI(self):

        self.setWindowTitle('PyView')
        self.setGeometry(QRect(530, 20, 256, 192))

        self.display = VideoDisplay()
        self.listOfFrames = SavedFrames(self.display)

        self.reset_zoom = QPushButton('Reset Zoom')
        self.reset_zoom.clicked.connect(self.display.reset)

        self.is_view_frozen = False
        self.froze_view = QPushButton('Freeze View')
        self.froze_view.clicked.connect(self.__froze_view_clicked)

        self.save_view = QPushButton('Save View')
        self.save_view.clicked.connect(self.__save_view)

        layout = QGridLayout()
        layout.addWidget(self.display, 0, 1, 6, 6)
        layout.addWidget(self.froze_view, 0, 0)
        layout.addWidget(self.save_view, 1, 0)
        layout.addWidget(self.reset_zoom, 2, 0)
        layout.addLayout(self.listOfFrames, 7, 0, 1, 7)

        self.setLayout(layout)

    # state changed
    def btnChngStateFreezeView(self):
        '''
        Set the button text to Freeze View status
        '''
        self.froze_view.setText("Freeze View")
        self.is_view_frozen = True

    # state changed
    def btnChngStateUnFreezeView(self):
        '''
        Set the button text to UnFreeze View status
        '''
        self.froze_view.setText("Unfreeze View")
        self.is_view_frozen = False

    # state changed
    def __froze_view_clicked(self):
        if self.is_view_frozen:
            self.btnChngStateFreezeView()
            self.display.start()
        else:
            self.btnChngStateUnFreezeView()
            self.display.stop()

    def __save_view(self):
        if self.display.saveView():
            self.listOfFrames.update_images()
        else:
            print("Failed to save frame")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PyViewMainWindow()
    window.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint |
                          Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
    window.show()

    sys.exit(app.exec_())
