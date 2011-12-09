#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject
import gtk
import pango
import re
import os
import keybinder
import logging
import time
import pynotify

UI_FILE = "data/player.ui"

class player:
    
    TARGETS = [
        ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
        ('text/plain', 0, 1),
        ('TEXT', 0, 2),
        ('STRING', 0, 3),
        ]
    
    def __init__(self, xmms):
        self.initlogger()

        self.xmms = xmms
        self.logger.info('azucar init')
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.window = self.builder.get_object("main")        

        pynotify.init('Azucar')
        
        self.__properties__()
        self.__set_signals__()
        self.__set_hotkeys__()
        
    def __properties__(self):        
        self.panel_active = self.builder.get_object("panel_active")
        self.scrollplaylist = self.builder.get_object("scrollplaylist")
        self.scrollalbums = self.builder.get_object("scrollalbums")
        self.list_active = self.builder.get_object("list_active")
        self.insearch = self.builder.get_object("insearch")
        self.playerbar = self.builder.get_object("playerbar")                

        self.panel_artists = self.builder.get_object("panel_artists")

        self.album = self.builder.get_object("lb_album")
        self.artist = self.builder.get_object("lb_artist")
        self.song = self.builder.get_object("lb_song")        
        self.image_cover = self.builder.get_object("cover_image")
        self.timer = self.builder.get_object("lb_timer")

        attr_timer = pango.AttrList()
        attr_timer.insert(pango.AttrSize(24000, 0, -1)) #font size
        attr_timer.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, -1)) #font weight        
        self.timer.set_attributes(attr_timer)

        attr_song = pango.AttrList()
        attr_song.insert(pango.AttrSize(14000, 0, -1)) #font size
        attr_song.insert(pango.AttrWeight(pango.WEIGHT_BOLD, 0, -1)) #font weight        
        self.song.set_attributes(attr_song)

        # buttons
        self.bt_next = self.builder.get_object("bt_next")
        self.bt_prev = self.builder.get_object("bt_prev")
        self.bt_play = self.builder.get_object("bt_play")
        self.bt_pause = self.builder.get_object("bt_pause")
        self.bt_stop = self.builder.get_object("bt_stop")
        self.bt_albums = self.builder.get_object("bt_albums")
        self.bt_options = self.builder.get_object("bt_options")
        
        self.playerbar.set_fraction(0)
        
        self.supported = ( 'mp1', 'mp2', 'mp3', 'm4a', 'm4p', 'ogg', 'flac', 'asf', 'wma', 'wav',
                    'mpg', 'mpeg', 'm4v', 'mp4', 'avi', 'ogm', 'wmv',
                    'mod', 'ape', 'apl', 'm4b', 'm4v', 'm4r', '3gp', 'aac', 
                    'mpc', 'mp+', 'mpp', 'oga', 'sid')
            
        self.current_song = ""
        self.current_song_duration = 0
        self.status = None

        self.volume = 100
        self.pos_move = -1
        
        self.model_songs = gtk.ListStore (int, str, 'gboolean')
        self.list_active.set_model(self.model_songs)
        self.list_active.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT|gtk.gdk.ACTION_MOVE)
        self.list_active.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)
        
        render = gtk.CellRendererText() 
        render.set_property('cell-background', '#eee')
        columna = gtk.TreeViewColumn ("name", render, text=1, cell_background_set=2)
        self.list_active.append_column(columna)
        self.cellbackground = True

    def __set_signals__(self):
        self.insearch.connect("changed", self.search_song)
        self.list_active.connect("key-press-event", self.list_active_keypress)
        self.list_active.connect("row-activated", self.list_active_row_activated)
        self.list_active.connect("drag_data_get", self.list_active_drag_data_get)
        self.list_active.connect("drag_data_received", self.list_active_drag_data_received)
        self.window.connect("key-press-event", self.main_keypress)
        self.window.connect("destroy", gtk.main_quit)
        self.bt_next.connect("clicked", self.xmms2_next)
        self.bt_prev.connect("clicked", self.xmms2_prev)
        self.bt_play.connect("clicked", self.xmms2_start)
        self.bt_stop.connect("clicked", self.xmms2_stop)
        self.bt_pause.connect("clicked", self.xmms2_pause)
        
        try:
            self.xmms.playback_current_id(self.handler_playback_current_id)
            self.xmms.playlist_list_entries('_active', self.get_tracks)                
            self.xmms.signal_playback_playtime(self.handler_set_time_track)
            self.xmms.playback_status(self.handler_playback_status)
            self.xmms.broadcast_playlist_changed(self.handler_playlist_change)
            self.xmms.broadcast_playback_current_id(self.handler_playback_current_id)
            self.xmms.broadcast_playback_status(self.handler_playback_status)
            self.xmms.playback_volume_get(self.xmms2_volume)
        except:
            self.logger.critical("Error in hanlder's to xmms2")

    def handler_playback_status(self, result):
        self.status = result.value()
    
    def handler_playlist_change(self, result):        
        update = result.value()
        
        if update['type']==0: #add            
            self.xmms.medialib_get_info(update['id'], self.add_track)
        elif update['type']==1: #add in position
            self.pos_move = update['position']
            self.xmms.medialib_get_info(update['id'], self.add_track_pos)                            
        elif update['type']==2: #shuffle
            self.model_songs.clear()
            self.xmms.playlist_list_entries('_active', self.get_tracks)
        elif update['type']==3: #remove
            self.remove_track(update['position'])
        elif update['type']==4: #clear
            self.model_songs.clear()
            self.list_active.set_model(self.model_songs)
        elif update['type']==5: #change positions            
            self.model_songs.swap(self.model_songs[update['position']].iter, self.model_songs[update['newposition']].iter)

    def handler_playback_current_id(self, result):                        
        self.xmms.medialib_get_info(result.value(), self.set_track_player)
        self.__select_row__(result.value())

    def __select_row__(self, id):
        try:
            miter = self.get_iter(id)
            if miter and self.model_songs == self.list_active.get_model():
                self.list_active.get_selection().select_iter(miter)
        except:
            self.logger.error('to get selection: __select_row__')
        
    def handler_set_time_track(self, result):
        total = result.value()
        min = total/(60*1000)
        sec = (total - min*1000*60)/1000

        if len(str(min))==1: min = "0%s" % min
        if len(str(sec))==1: sec = "0%s" % sec

        self.timer.set_text("%s:%s" % (min, sec) )
        
        progress = 0.0
        
        if self.current_song_duration > 0:
            progress = (int(total)*100/int(self.current_song_duration))/100.0            
        try:
            self.playerbar.set_fraction(progress)
        except Exception:
            self.logger.error("%s" % Exception)
            
    def set_track_player(self, result):
        track = self.get_taginfo(result.value())
        if track:
            self.current_song = "%s - %s" % (track[1],track[2])        
            self.current_song_duration = result.value()['duration']

            self.artist.set_text("Artist: %s" % track[1])
            self.song.set_text("%s" % track[2])
            self.album.set_text("Album: %s" % track[3])
            
            try:
                url_cover = "%s/.config/xmms2/bindata/%s" % (os.getenv("HOME"), result.value()['picture_front'])
            except:
                url_cover = "data/no-cover.jpg"

            self.set_cover_information(url_cover)

            notify = pynotify.Notification(track[2], "Album: %s \nArtis: %s" % (track[3], track[1]) )
            notify.set_icon_from_pixbuf(self.image_cover.get_pixbuf())
            notify.set_timeout(1000)
            notify.show()
            
    def remove_track(self, position):
        try:
            self.model_songs.remove(self.model_songs[position].iter)
        except:
            self.logger.error("Can't remove position: %s" % position)
        
    def get_tracks(self, result):
        playlist = result.value()
        for element in playlist:
            self.xmms.medialib_get_info(element, self.add_track)

    def add_track(self, result):
        taginfo = self.get_taginfo(result.value())
        try:
            self.model_songs.append([taginfo[0], "%s - %s" % (taginfo[1], taginfo[2]), self.cellbackground])        
            self.cellbackground = (True, False)[self.cellbackground==True]
        except:
            self.logger.error("Can't to append: %s" % result.value())    
        
    
    def add_track_pos(self, result):
        if self.pos_move == -1:
            return        
        else:
            taginfo = self.get_taginfo(result.value())
                        
            iter = self.model_songs.get_iter(self.pos_move)            
            self.model_songs.insert_before(iter, [taginfo[0], "%s - %s" % (taginfo[1], taginfo[2]), self.cellbackground])            
            
            cellbackground = True
            modeltemp = gtk.ListStore (int, str, 'gboolean')
            
            for i in self.model_songs:                                        
                modeltemp.append([self.model_songs.get_value(i.iter, 0), self.model_songs.get_value(i.iter, 1), cellbackground])
                cellbackground = (True, False)[cellbackground==True]
    
            self.model_songs = modeltemp            
            self.list_active.set_model(self.model_songs)
            
            self.pos_move = -1
        
    
    def get_taginfo(self, info):
        track = []

        try:
            track.append(info['id'])

            if info.has_key('artist'):
                track.append(info["artist"])
            else:
                track.append("No artist")
        
            if info.has_key('title'):
                track.append(info["title"])
            else:
                track.append(self.get_filename(info['url']))

            if info.has_key('album'):
                track.append(info["album"])
            else:
                track.append("")
            
        except:            
            pass

        return track
        
    def initlogger(self):
        self.logger = logging.getLogger('xmms2me')
        hdlr = logging.FileHandler('%s/.config/xmms2/azucar.log' % os.getenv("HOME"))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def search_song(self, widget):
        modeltemp = gtk.ListStore (int, str, 'gboolean')

        cellbackground = True
        
        for i in self.model_songs:                        
            match = re.search(r'%s' % widget.get_text().lower(), self.model_songs.get_value(i.iter, 1).lower())
            if match:
                modeltemp.append([self.model_songs.get_value(i.iter, 0), self.model_songs.get_value(i.iter, 1), cellbackground])
                cellbackground = (True, False)[cellbackground==True]

        self.list_active.set_model(modeltemp)
        
    def list_active_keypress(self, widget, event):
        try:
            sel = self.list_active.get_selection().get_selected()
            id = widget.get_model().get_value(sel[1], 0)                

            if event.keyval == 65535: # Delete Item            
                try:                                
                    pos = self.get_song_position(id)
                    self.xmms.playlist_remove_entry(pos,'_active')
                    self.list_active.set_model(self.model_songs)
                except:
                    self.logger.error("in remove item to playlist")                    
            else:
                self.app_cover.window.hide()
        except:
            return

    def set_cover_information(self, url_cover):            
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(url_cover)
            scaled_buf = pixbuf.scale_simple(100,100,gtk.gdk.INTERP_BILINEAR)
            self.image_cover.set_from_pixbuf(scaled_buf)
        except:
            pixbuf = gtk.gdk.pixbuf_new_from_file("data/no-cover.jpg")
            scaled_buf = pixbuf.scale_simple(100,100,gtk.gdk.INTERP_BILINEAR)
            self.image_cover.set_from_pixbuf(scaled_buf)
        
    def list_active_row_activated(self, widget, iter, path):
        modelo = widget.get_model()
        new_pos = self.get_song_position(int(modelo.get_value(modelo[iter[0]].iter, 0)))        
        self.xmms2_play(new_pos)

    def list_active_drag_data_get(self, treeview, context, selection, target_id, etime):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, 0)        
        #print data, target_id

    def list_active_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        treeselection = treeview.get_selection()
        model, iter_sel = treeselection.get_selected()
        data = selection.data
        drop_info = treeview.get_dest_row_at_pos(x, y)        
        
        if drop_info:
            path, position = drop_info
            iter_des = model.get_iter(path)
            pos_des = path[0]
            id_sel = model.get_value(iter_sel, 0)
            pos_sel = model.get_path(iter_sel)[0]
                        
            self.xmms.playlist_remove_entry(pos_sel,'_active')
            self.xmms.playlist_insert_id(path[0], id_sel)            
        
        return        
    
    def main_keypress(self, widget, event):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)

        mod = gtk.accelerator_get_label(keyval, event.state)
        mod = mod.replace("+Mod2","")

        #print mod, name, keyval

        if mod == "Ctrl+O":
            self.xmms2_open_files()
        elif mod == "Ctrl+P":
            self.xmms2_open_directory()
        elif mod == "Ctrl+L":
            self.xmms2_clear()
        elif mod == "Ctrl+I":
            self.xmms.playback_current_id(self.handler_playback_current_id)
        elif mod == "Ctrl+J":
            if not self.insearch.get_visible():
                self.insearch.set_visible(True)                
                self.insearch.grab_focus()
            else:
                self.insearch.set_visible(False)
        elif mod == "Ctrl++":
            self.volume_up()
        elif mod == "Ctrl+-":            
            self.volume_down()

    def volume_up(self):
        self.volume = (self.volume+10, 100)[self.volume+10>100]
        self.xmms.playback_volume_set('master', self.volume)

        notify = pynotify.Notification("Volume", "%d%s" % (self.volume,'%') )
        notify.set_timeout(500)
        notify.show()
        
    def volume_down(self):
        self.volume = (self.volume-10, 0)[self.volume-10<=0]
        self.xmms.playback_volume_set('master', self.volume)            

        notify = pynotify.Notification("Volume", "%d%s" % (self.volume,'%') )
        notify.set_timeout(500)
        notify.show()
        
    def xmms2_volume(self, result):
        try:
            self.volume = result.value()['master']
        except:
            self.logger.info("No volume master access")
            
    def xmms2_open_files(self):
        
        dialog = gtk.FileChooserDialog("Add Music Files..",
            None,
            gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_select_multiple(True)
        dialog.set_current_folder(os.getenv("HOME"))
        
        filter = gtk.FileFilter()
        filter.set_name("Music files")

        for format in self.supported:
            filter.add_pattern("*.%s" % format)

        dialog.add_filter(filter)
        
        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            for ifile in dialog.get_filenames():
                try:
                    self.xmms.playlist_add_url('file://%s' % ifile)
                except:
                    self.logger.error("Error to adding file %s" % ifile)
        elif response == gtk.RESPONSE_CANCEL:
            self.logger.info("Closed, no files selected")

        dialog.destroy()

    def xmms2_open_directory(self):
        
        dialog = gtk.FileChooserDialog("Add Music Directory..",
            None,
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_select_multiple(True)
        dialog.set_current_folder(os.getenv("HOME"))

        filter = gtk.FileFilter()
        filter.set_name("Music files")

        for format in self.supported:
            filter.add_pattern("*.%s" % format)

        dialog.add_filter(filter)
        
        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            for idir in dialog.get_filenames():
                try:
                    self.xmms.playlist_radd('file://%s' % idir)
                except:
                    self.logger.error("Error to adding file %s" % ifile)
        elif response == gtk.RESPONSE_CANCEL:
            self.logger.info("Closed, no files selected")

        dialog.destroy()
        
    def xmms2_clear(self):
        self.xmms.playlist_clear()
        
    def xmms2_next(self, widget=None):
        self.xmms.playlist_set_next_rel(1)
        self.xmms.playback_tickle()

    def xmms2_prev(self, widget=None):
        self.xmms.playlist_set_next_rel(-1)
        self.xmms.playback_tickle()
        
    def xmms2_play(self, pos):
        self.xmms.playlist_set_next(pos)
        self.xmms.playback_tickle()        
        if self.status == 0:
            self.xmms.playback_start()

    def xmms2_start(self, widget=None):
        self.xmms.playback_start()

    def xmms2_stop(self, widget=None):
        self.xmms.playback_stop()

    def xmms2_pause(self, widget=None):
        self.xmms.playback_pause()
        
    def get_filename(self, url):        
        n = url.split('/')
        
        try:
            name = n[-1][:-4]
        except:
            name = ""
        
        return name.replace('+',' ')

    def __set_hotkeys__(self):

        key_next = "<Ctrl><Alt>V"        
        keybinder.bind(key_next, self.xmms2_next)
        key_prev = "<Ctrl><Alt>Z"        
        keybinder.bind(key_prev, self.xmms2_prev)
        key_start = "<Ctrl><Alt>C"        
        keybinder.bind(key_start, self.xmms.playback_start)
        key_pause = "<Ctrl><Alt>X"        
        keybinder.bind(key_pause, self.xmms.playback_pause)
        key_clear = "<Ctrl><Alt>B"
        keybinder.bind(key_clear, self.xmms.playback_stop)
        key_focus = "<Ctrl><Alt>M"
        keybinder.bind(key_focus, self.get_focus)

    def get_focus(self):
        print self.window.props.is_active
        
    def get_song_position(self, id):
        pos = 0
        if id > -1:
            for i in self.model_songs:
                if i[0] == id:
                    return pos
                pos+=1
        return 0

    def get_iter(self, id):
        for it in self.model_songs:
            if it[0] == id:
                return it.iter
        return None
    