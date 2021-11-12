#!/usr/bin/env python

import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

class VidFeed:

    def __init__(self):
        # gst-launch-1.0 v4l2src do-timestamp=TRUE device=/dev/video0 ! videoconvert ! xvimagesink
        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make("v4l2src", "vsource")
        self.sink = Gst.ElementFactory.make("ximagesink","video-output")
        self.source.set_property("device","/dev/video0")
        self.colorspace = Gst.ElementFactory.make("videoconvert", "colorspace")

        self.player.add(self.source)
        self.player.add(self.colorspace)
        self.player.add(self.sink)

        self.source.link(self.colorspace)
        self.colorspace.link(self.sink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        self.startPrev()
    # def start_stop(self, w):
    #     if self.button.get_label() == "Start":
    #         

    def on_message(self, bus, message):
        t = message.type
        print(f"on_message: {message} type: {t}")
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err} ", debug)
            self.player.set_state(Gst.State.NULL)

    def on_sync_message(self, bus, message):
        print("on_sync_message")
        if message.get_structure().get_name() == 'prepare-window-handle':
            print("here i am")
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            xid = self.movie_window.get_property('window').get_xid()
            imagesink.set_window_handle(xid)

    def startPrev(self):
        self.player.set_state(Gst.State.PLAYING)
        print("should be playing")

GObject.threads_init()
Gst.init(None)        
VidFeed()
Gtk.main()