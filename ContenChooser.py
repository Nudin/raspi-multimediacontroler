import os, time
from gi.repository import Gtk
from settings import *

def debug(text):
    if DEBUG:
        print(time.ctime(), text)

class ContenChooser(Gtk.Window):

    stoppedmanuell = False	# Has the playback been stoped by user (or was the file finished)
    contenttype = None		# video or image
    playing_tree_iter = None

    # Trivial Constructor, don't do anything except creating a window
    def __init__(self, commandQueue, statusQueue):
        self.statusQueue = statusQueue
        self.commandQueue = commandQueue
        Gtk.Window.__init__(self, title="Auswahlmenü")
        
    # The window is build up here
    def init2(self, num):
        #Setting up the grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Read in all available Content into a ListStore
        self.liststore = Gtk.ListStore(str)
        if num == 0:
            self.dir=videodir
            self.contenttype="video"
        else:
            self.dir=photodir
            self.contenttype="image"
        self.filelist={}
        for file in os.listdir(self.dir):
            title = os.path.splitext(file)[0]
            self.filelist[title] = file
            self.liststore.append((title, ))

        #creating the treeview
        self.treeview = Gtk.TreeView(self.liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Auswahl", renderer, text=0)
        self.treeview.append_column(column)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollwindow = Gtk.ScrolledWindow()
        self.scrollwindow.set_vexpand(True)
        self.grid.attach(self.scrollwindow, 0, 0, 4, 5)

        self.scrollwindow.add(self.treeview)
        
        self.playbutton = Gtk.Button("play")
        play_image = Gtk.Image()
        play_image.set_from_file("icons/media-playback-start.png")
        self.playbutton.set_image(play_image)
        self.playbutton.set_property("always_show_image",True)
        self.playbutton.connect("clicked",self.playbuttonclicked)
        
        self.stopbutton = Gtk.Button("stop")
        stop_image = Gtk.Image()
        stop_image.set_from_file("icons/media-playback-stop.png")
        self.stopbutton.set_image(stop_image)
        self.stopbutton.set_property("always_show_image",True)
        self.stopbutton.connect("clicked",self.stopbuttonclicked)
        
        self.backbutton = Gtk.Button("back")
        back_image = Gtk.Image()
        back_image.set_from_file("icons/back.png")
        self.backbutton.set_image(back_image)
        self.backbutton.set_property("always_show_image",True)
        self.backbutton.connect("clicked",self.exit)
        self.statuslabel = Gtk.Label("Please choose")
        
        self.autoplay = Gtk.CheckButton("autoplay")
	self.autoplay.set_active(autoplay_default)
        
        self.grid.attach_next_to(self.playbutton,
                               self.scrollwindow, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.stopbutton,
                               self.playbutton,   Gtk.PositionType.RIGHT,  1, 1)
        self.grid.attach_next_to(self.autoplay,
                               self.stopbutton,   Gtk.PositionType.RIGHT,  1, 1)
        
        self.grid.attach_next_to(self.backbutton,
                               self.scrollwindow, Gtk.PositionType.TOP,    1, 1)
        self.grid.attach_next_to(self.statuslabel,
                               self.backbutton,   Gtk.PositionType.RIGHT,  3, 1)
        
        self.resize(320, 240)
        
        
    # Get the selected element
    def get_selection(self):
        (model, pathlist) =  self.treeview.get_selection().get_selected_rows()
        self.playing_tree_iter = model.get_iter(pathlist[0])
        return self.filelist[model.get_value(self.playing_tree_iter,0)]
        
    # Get the element after the selected element
    def getnext(self):
        (model, pathlist) =  self.treeview.get_selection().get_selected_rows()
        next_tree_iter = model.iter_next(self.playing_tree_iter)
        if next_tree_iter == None:
            next_tree_iter = model.get_iter_first()
        self.playing_tree_iter=next_tree_iter
        return self.filelist[model.get_value(next_tree_iter,0)]
    
    
    #### Event-handler ####
    
    # Play the selected element
    def playbuttonclicked(self, button=None):
        selection = self.get_selection()
        debug("Selection: " + selection)
        self.play(selection)
        
    # Stop playing
    # this function is called by the stop-button
    def stopbuttonclicked(self, button):
        self.stop()
        self.commandQueue.put("clear()")
        
    # exit the window
    def exit(self, button):
        self.close()


    #### Playback-handler ####

    # Play the given element
    def play(self, selection):
        # Stop old playback
        self.stop()
        # Start new playback
        self.commandQueue.put("play('"+self.contenttype+"', '"+self.dir+selection+"')")
        time.sleep(0.5)
        while not self.statusQueue.empty():
            val = self.statusQueue.get()
            debug("Outputting: " + val)
        self.statuslabel.set_label("Playing: "+selection)
    
    # Stop playing
    def stop(self):
        self.commandQueue.put("stop()")
        while not self.statusQueue.empty():
            val = self.statusQueue.get()
            debug("Outputting: " + val)
    
    # Set label back and if autoplay is enabled, start playing nex video
    # this function is called after the video/slideshow has been stoped
    def stopped(self, returncode):
        debug("stopped() " + str(self.stoppedmanuell))
        self.statuslabel.set_label("Please choose")
        if (returncode >= 0) and self.autoplay.get_active():
            self.play(self.getnext())


