#!/usr/bin/env python

import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo
import sys 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore    import QRect

class VidFeed:

    def __init__(self,windowId):
        Gst.init(None)
        # gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! xvimagesink
        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make("v4l2src", "vsource")
        self.conv   = Gst.ElementFactory.make("videoconvert", "colorspace")
        self.scaler = Gst.ElementFactory.make("videoscale", "fvidscale")
        self.sink   = Gst.ElementFactory.make("ximagesink","video-output")
        
        self.source.set_property("device","/dev/video0")
        
        self.__add_many([self.source,self.conv,self.scaler,self.sink])
        self.__link_many([self.source,self.conv,self.scaler,self.sink])

        self.__set_window_id(windowId)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.__on_message)
        bus.connect("sync-message::element", self.__on_sync_message)
        

        # self.startPrev()

    def __set_window_id(self,windowId):
        self.windowId = windowId

    def __add_many(self,pipeline_list):
        for node in pipeline_list:
            self.player.add(node)

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

    def startPrev(self):
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

    VidFeed(wId)
    sys.exit(app.exec_())
