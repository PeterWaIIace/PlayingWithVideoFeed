#!/usr/bin/env python
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore    import QRect
import numpy as np
import time 
import sys 

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gtk
from gi.repository import GdkX11, GstVideo

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:

class VidFeed:

    def __init__(self,windowId):
        Gst.init(None)
        # gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! xvimagesink
        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make("v4l2src", "vsource")
        self.conv   = Gst.ElementFactory.make("videoconvert", "colorspace")
        self.scaler = Gst.ElementFactory.make("videoscale", "fvidscale")
        self.crop   = Gst.ElementFactory.make('videocrop', 'VideoCrop')

        # self.sink   = Gst.ElementFactory.make("ximagesink","video-output")
        self.appsink = Gst.ElementFactory.make("appsink","video-output")
        
        self.appsink.set_property("emit-signals", True)

        caps = Gst.caps_from_string("video/x-raw, format=(string){RGB, GRAY8}; video/x-bayer,format=(string){rggb,bggr,grbg,gbrg}")
        self.appsink.set_property("caps", caps)

        self.appsink.connect("new-sample", self.__new_frame, self.appsink)

        self.crop.set_property('top', 0)
        self.crop.set_property('bottom', 0)
        self.crop.set_property('left', 0)
        self.crop.set_property('right', 0)
        
        self.source.set_property("device","/dev/video0")
        
        self.__add_many([self.source,self.conv,self.scaler,self.crop,self.appsink])
        self.__link_many([self.source,self.conv,self.scaler,self.crop,self.appsink])

        self.__set_window_id(windowId)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)
        
        self.curr_frame = None
        # self.startPrev()

    def __gst_to_np(self,sample):
        buf = sample.get_buffer()
        caps = sample.get_caps()
        arr = np.ndarray(
            (caps.get_structure(0).get_value('height'),
            caps.get_structure(0).get_value('width'),
            3),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8)
        return arr

    def __set_window_id(self,windowId):
        self.windowId = windowId

    def __add_many(self,pipeline_list):
        for node in pipeline_list:
            self.player.add(node)

    def __new_frame(self,sink,data):
        frame = sink.emit("pull-sample")

        arr = self.__gst_to_np(frame)
        self.curr_frame = arr
        return Gst.FlowReturn.OK

    def __link_many(self,pipeline_list):
        for n in range(len(pipeline_list)-1):
            pipeline_list[n].link(pipeline_list[n+1])

    def __on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err} ", debug)
            self.player.set_state(Gst.State.NULL)

    def __on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            win_id = self.windowId
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            # if not window id then create new window
            if win_id == None:
                win_id = self.movie_window.get_property('window').get_xid()   
            imagesink.set_window_handle(win_id)

    def is_frame_ready(self):
        return not (self.curr_frame is None)

    def get_frame(self):
        ret_frame = self.curr_frame
        self.curr_frame = None
        return ret_frame

    def startPrev(self):
        self.player.set_state(Gst.State.PLAYING)
    
    def zoom(self,top,bottom,left,right):
        self.player.set_state(Gst.State.PAUSED)
        self.crop.set_property('top', top)
        self.crop.set_property('bottom', bottom)
        self.crop.set_property('left', left)
        self.crop.set_property('right', right)
        self.player.set_state(Gst.State.PLAYING)

# main for internal tests
if __name__=="__main__":

    app = QApplication(sys.argv)
    cameraWindow = QWidget()
    cameraWindow.setGeometry(QRect(530, 20, 256, 192))
    cameraWindow.setObjectName("cameraWindow")
    cameraWindow.setAttribute(0, 1); # AA_ImmediateWidgetCreation == 0
    cameraWindow.setAttribute(3, 1); # AA_NativeWindow == 3
    cameraWindow.show()

    wId = cameraWindow.winId()

    vid = VidFeed(wId)
    vid.startPrev()
    time.sleep(2)
    vid.zoom(0,150,40,60)
    sys.exit(app.exec_())
