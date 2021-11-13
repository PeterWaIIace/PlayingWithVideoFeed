import sys
import numpy as np
from PyQt5 import QtGui 

from PyQt5.QtWidgets import QApplication, QLabel, QLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QStackedLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore    import QRect, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui     import QPalette, QColor, QPainter, QPixmap, QImage, QPen

from videoFeed import VidFeed

class VideoFeedThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    

    def run(self):
        # capture from web cam
        self.cap = VidFeed(None)
        self.cap.startPrev()

        while True:
            if self.cap.is_frame_ready():
                cv_img = self.cap.get_frame()
                self.change_pixmap_signal.emit(cv_img)

    def call_zoom(self,x,y,width,height):
        self.cap.zoom(x,y,width,height)

class VideoDisplay(QLabel):

    def __init__(self):
        super().__init__()

        # self.setGeometry(QRect(530, 20, 256, 192))
        self.setObjectName("cameraWindow")
        self.setAttribute(0, 1); # AA_ImmediateWidgetCreation == 0
        self.setAttribute(3, 1); # AA_NativeWindow == 3

        self.x_anchron = 0
        self.y_anchron = 0
        self.curr_x = 0
        self.curr_y = 0

        self.zoom_x = 0
        self.zoom_y = 0
        self.zoom_w = self.rect().width()
        self.zoom_h = self.rect().height()

        self.draw_zoom = False
        self.crop_image = False
        self.curr_frame = None

        self.pxman = QPixmap(640, 480)
        self.pxman.fill(QColor('darkGray'))
        # set the image image to the grey pixmap
        self.setPixmap(self.pxman)
        
        self.thread = VideoFeedThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        self.setMouseTracking(True)
        
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_frame_qt(cv_img)
        self.curr_frame = qt_img.scaled(640,480, Qt.KeepAspectRatio)
        self.update()

    def convert_frame_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        Qt_format = QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)  
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(Qt_format)

    def setZoom(self):
        if(self.pos1_x < self.pos2_x):
            self.zoom_x = self.pos1_x
            self.zoom_w = self.pos2_x - self.pos1_x
        else:
            self.zoom_x = self.pos2_x
            self.zoom_w = self.pos1_x - self.pos2_x
        if(self.pos1_y < self.pos2_y):
            self.zoom_y = self.pos1_y
            self.zoom_h = self.pos2_y - self.pos1_y
        else:
            self.zoom_y = self.pos2_y
            self.zoom_h = self.pos1_y - self.pos2_y
        self.crop_image = True
        print("crop is set to true")

    def resetZoom(self):
        self.crop_image = False

    def cropImage(self,org):
        scale_factor_w = self.rect().width()/org.width()
        scale_factor_h = self.rect().height()/org.height()
        crop_rect = QRect(
            self.zoom_x / scale_factor_w,
            self.zoom_y / scale_factor_h,
            self.zoom_w / scale_factor_w,
            self.zoom_h / scale_factor_h)
        return org.copy(crop_rect)

    def paintEvent(self, event):
        if not (self.curr_frame is None):
            if self.crop_image:
                self.curr_frame = self.cropImage(self.curr_frame)

            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.curr_frame)

            if self.draw_zoom:
                self.draw(painter, self.x_anchron, self.y_anchron, self.curr_x, self.curr_y)
            
    def draw(self,painter,x_anchron, y_anchron, curr_x, curr_y):
        pen = QPen(Qt.red, 3)
        painter.setPen(pen)
        painter.drawLine(x_anchron, y_anchron, x_anchron, curr_y)
        painter.drawLine(x_anchron, y_anchron, curr_x, y_anchron)
        painter.drawLine(curr_x, curr_y, x_anchron, curr_y)
        painter.drawLine(curr_x, curr_y, curr_x, y_anchron)

    def mousePressEvent(self, event):
        self.x_anchron = event.x()
        self.y_anchron = event.y()
        self._lastpos = event.pos()
        if(self.draw_zoom):
            self.draw_zoom = False
            self.pos2_x = self.x_anchron
            self.pos2_y = self.y_anchron
            self.setZoom()
        else:
            self.pos1_x = self.x_anchron
            self.pos1_y = self.y_anchron
            self.curr_x = event.x()
            self.curr_y = event.y()
            self.draw_zoom = True

    def mouseMoveEvent(self,event):
        if(self.draw_zoom):
            self.curr_x = event.x()
            self.curr_y = event.y()
            print(f"curr_x = {self.curr_x}, curr_y = {self.curr_y}")
            self.update()
class MainWindow(QWidget):
    
    def __init__(self,display):
        super().__init__()

        
        self.setWindowTitle('PyView')
        
        self.setGeometry(QRect(530, 20, 256, 192))
        
        reset_view = QPushButton('Reset View')
        reset_view.clicked.connect(display.resetZoom)

        froze_view = QPushButton('Froze')
        froze_view.clicked.connect(display.stop)

        layout = QGridLayout()
        layout.addWidget(display, 0, 1,3, 3)
        layout.addWidget(froze_view, 0, 0)
        layout.addWidget(reset_view, 1, 0)

        # self.setStyleSheet("background-color:black;")
        # self.setAutoFillBackground(True)
        
        self.setLayout(layout)


if __name__=="__main__":
    app = QApplication(sys.argv)

    # interface = videoInterface()
    display = VideoDisplay()

    window = MainWindow(display)
    window.show()

    # vid = VidFeed(display.get_id())
    # vid.startPrev()

    sys.exit(app.exec_())

