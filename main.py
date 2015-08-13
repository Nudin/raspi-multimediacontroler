#!/usr/bin/env python3
import sys
import os
import time
import threading
from queue import Queue
import subprocess
import signal

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GObject

from gi.repository import Gdk

from ContenChooser import *
from settings import *

GObject.threads_init()

Gtk.Settings.get_default().set_property("gtk-touchscreen-mode", True)
Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", False)
Gtk.Settings.get_default().set_property("gtk-theme-name", gtktheme)
Gtk.Settings.get_default().set_property('gtk-font-name', font)
Gtk.Settings.get_default().set_property('gtk-button-images', True)

if show_exit:
    icons = ["video", "image", "system"]
else:
    icons = ["video", "image"]

run = True
statusQueue = Queue()
commandQueue = Queue()
win2 = ContenChooser(commandQueue, statusQueue)

def debug(text):
    if DEBUG:
        print(time.ctime(), text)

class waitforexit(threading.Thread):
    def __init__(self, pro, statusQueue):
        self.statusQueue = statusQueue
        self.pro = pro
        threading.Thread.__init__ (self,name="waitforexit")
    
    def run(self):
        self.pro.wait()
        print(self.pro.returncode)
        if self.pro.returncode >= 0:
            clear_pro = subprocess.Popen("./clear.sh", stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid)
        debug("Playback finished")
        self.statusQueue.put("stoped")
        win2.stopped(self.pro.returncode)


class video(threading.Thread):
    """
        Play a video
    """
    pro = None
    
    def __init__(self, commandQueue, statusQueue):
        self.commandQueue = commandQueue
        self.statusQueue = statusQueue
        threading.Thread.__init__ (self,name="videoThread")
    
    def run(self):
        while True:
            if not self.commandQueue.empty():
                command = self.commandQueue.get()
                debug("command: " + command)
                if command == "exit":
                    break
                else:
                    exec("self."+command)
            time.sleep(0.2)
    
    def play(self, contenttype, filename):
        if contenttype == "video":
            player=videoplayer
            clear_pro = subprocess.Popen("./blackscreen", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        else:
            player=imageplayer
        self.pro = subprocess.Popen("trap 'exit -15' EXIT;"+ player+" '"+filename+"'", stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
        self.statusQueue.put("started")
        waiter = waitforexit(self.pro, self.statusQueue)
        waiter.start()
    
    def stop(self):
        if self.pro:
          if self.pro.poll() != 0:
            try:
              os.killpg(self.pro.pid, signal.SIGTERM)	# Why not pro.kill()?
            except:
              True
    
    def clear(self):
        clear_pro = subprocess.Popen("./clear.sh", stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid)


class MainWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self)

    liststore = Gtk.ListStore(Pixbuf, str)

    iconview = Gtk.IconView.new()
    iconview.set_property("columns",len(icons))
    
    iconview.set_model(liststore)
    iconview.set_pixbuf_column(0)
    iconview.set_text_column(-1)
    self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(65535,65535,65535))
    iconview.set_property("expand",True)
    iconview.set_property("valign",3)
    iconview.set_property("halign",3)
    iconview.set_property("spacing",0)
    iconview.set_property("row-spacing",0)
    iconview.set_property("column-spacing",0)

    icon_scale = touch_resolution_w/len(icons)*0.9

    for icon in icons:
        pixbuf =  Pixbuf.new_from_file("icons/"+icon+".png")
        pixbuf =  pixbuf.scale_simple(icon_scale,icon_scale,2)
        liststore.append([pixbuf, icon])

    box = Gtk.Box.new(1,20)
    innerbox = Gtk.Box.new(1,0)
    #innerbox.add(Gtk.Label("Choose:"))
    #innerbox.pack_end(iconview, True, True, 0)
    #innerbox.set_baseline_position(2)
    box.set_baseline_position(2)
    #box.pack_end(innerbox, True, True, 0)
    box.add(iconview)
    self.add(box)
    iconview.connect("selection-changed",self.react)
    self.resize(touch_resolution_w,touch_resolution_h)
    

  def react(self, data):
      global run
      if len(data.get_selected_items()) != 0:
         buttonnr = int(data.get_selected_items()[0].to_string())
         
         if buttonnr == 2:
             # exit-button pressed, leave program
             run = False
             self.close()
             Gtk.main_quit()
             win2.stop(True)
             return
         else:
             # Show contentchooser-window
             self.close()
             win2.init2(buttonnr)
             win2.connect("delete-event", Gtk.main_quit)
             win2.show_all()


videoThread = video(commandQueue, statusQueue)
videoThread.start()

subprocess.Popen("./clear.sh", stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid)

if play_on_start_type:
    commandQueue.put("play('" + play_on_start_type + "', '" + play_on_start_file + "')")

while run:
 win = MainWindow()
 win.show_all()
 Gtk.main()

commandQueue.put("exit")

