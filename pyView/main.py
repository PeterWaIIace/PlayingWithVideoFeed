import sys
import numpy as np
from PyQt5 import QtGui 
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QLabel, QLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QStackedLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore    import QRect, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui     import QPalette, QColor, QPainter, QPixmap, QImage, QPen

from zoom import ZoomScope, ROI, Point
from videoFeed import VidFeed

class VideoFeedThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        self.cap = VidFeed(None)
        self.cap.startPrev()

        self.__run = True
        while True:
            if self.cap.is_frame_ready() and self.__run:
                cv_img = self.cap.get_frame()
                self.change_pixmap_signal.emit(cv_img)

    def call_zoom(self,x,y,width,height):
        self.cap.zoom(x,y,width,height)

    def task_stop(self):
        self.__run = False

    def task_start(self):
        self.__run = True

class VideoDisplay(QLabel):

    def __init__(self):
        super().__init__()

        # self.setGeometry(QRect(530, 20, 256, 192))
        self.setObjectName("cameraWindow")
        self.setAttribute(0, 1); # AA_ImmediateWidgetCreation == 0
        self.setAttribute(3, 1); # AA_NativeWindow == 3

        self.Anchron = None
        self.Cursor = None

        self.draw_zoom = False
        self.curr_frame = None

        self.MicroScope = ZoomScope(self.rect().width(),self.rect().height())
        self.Region = ROI()

        self.pxman = QPixmap(640, 480)
        self.pxman.fill(QColor('darkGray'))
        # set the image image to the grey pixmap
        self.setPixmap(self.pxman)
        
        self.thread = VideoFeedThread()
        self.thread.change_pixmap_signal.connect(self.updateImage)
        self.thread.start()

        self.setMouseTracking(True)

    @pyqtSlot(np.ndarray)
    def updateImage(self, np_img):
        qt_img = self.convertFrame(np_img)
        self.curr_frame = qt_img.scaled(640,480, Qt.KeepAspectRatio)
        self.update()

    def convertFrame(self, frame):
        """Convert from an opencv image to QPixmap"""
        Qt_format = QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)  
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(Qt_format)

    def stop(self):
        self.thread.task_stop()

    def start(self):
        self.thread.task_start()

    def resetZoom(self):
        self.MicroScope.resetZoom(
            self.rect().width(),
            self.rect().height()
            )
        self.update()

    def paintEvent(self, event):
        if not (self.curr_frame is None):
            if self.MicroScope.isZoomSet():
                frame = self.MicroScope.cropImage(self.curr_frame,self.rect())
            else:
                frame = self.curr_frame

            painter = QPainter(self)
            painter.drawPixmap(self.rect(), frame)

            if self.draw_zoom:
                self.draw(painter, self.Anchron.x(), self.Anchron.y(), self.Cursor.x(), self.Cursor.y())
            
    def draw(self,painter,x_anchron, y_anchron, curr_x, curr_y):
        pen = QPen(Qt.red, 3)
        painter.setPen(pen)
        painter.drawLine(x_anchron, y_anchron, x_anchron, curr_y)
        painter.drawLine(x_anchron, y_anchron, curr_x, y_anchron)
        painter.drawLine(curr_x, curr_y, x_anchron, curr_y)
        painter.drawLine(curr_x, curr_y, curr_x, y_anchron)

    def saveView(self):
        if self.MicroScope.isZoomSet():
            view = self.MicroScope.cropImage(self.curr_frame,self.rect())
        else:
            view = self.curr_frame

        now = datetime.now() 
        time = now.strftime("%H:%M:%S")
        return view.save(f"saved_frames/frame_{time}.png")

    def mousePressEvent(self, event):
        self.Anchron = Point(event.x(),event.y())

        if(self.draw_zoom):
            self.draw_zoom = False
            
            self.Region.addPoint(self.Anchron)
            
            self.MicroScope.setZoom(
                self.Region,
                self.rect()
                )
        else:

            self.Region.addPoint(self.Anchron)
            self.Cursor = Point(event.x(),event.y())
            self.draw_zoom = True
        
        self.update()

    def mouseMoveEvent(self,event):
        if(self.draw_zoom):
            self.Cursor = Point(event.x(),event.y())
            self.update()
class MainWindow(QWidget):
    
    def __init__(self,display):
        super().__init__()

        self.setWindowTitle('PyView')
        self.setGeometry(QRect(530, 20, 256, 192))

        self.display = display
        
        self.reset_zoom = QPushButton('Reset Zoom')
        self.reset_zoom.clicked.connect(self.display.resetZoom)

        self.is_view_frozen = False
        self.froze_view = QPushButton('Freeze View')
        self.froze_view.clicked.connect(self.__froze_view_clicked)

        self.save_view = QPushButton('Save View') 
        self.save_view.clicked.connect(self.__save_view)

        layout = QGridLayout()
        layout.addWidget(display, 0, 1,6, 6)
        layout.addWidget(self.froze_view, 0, 0)
        layout.addWidget(self.save_view , 1, 0)
        layout.addWidget(self.reset_zoom, 2, 0)

        # self.setStyleSheet("background-color:black;")
        # self.setAutoFillBackground(True)
        
        self.setLayout(layout)

    def __froze_view_clicked(self):
        if self.is_view_frozen:
            self.froze_view.setText("Freeze View")
            self.display.start()
            self.is_view_frozen = False
        else:
            self.froze_view.setText("Unfreeze View")
            self.display.stop()
            self.is_view_frozen = True

    def __save_view(self):
        if self.display.saveView():
            pass
        else:
            print("Failed to save frame")

if __name__=="__main__":
    app = QApplication(sys.argv)
    # interface = videoInterface()
    display = VideoDisplay()

    window = MainWindow(display)
    window.show()

    # vid = VidFeed(display.get_id())
    # vid.startPrev()

    sys.exit(app.exec_())

