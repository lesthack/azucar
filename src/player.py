#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject
import gtk
import re
import os
import keybinder
from cover import *
#import pygtk
#import logging

UI_FILE = "data/player.ui"

class player:
	def __init__(self, xmms):
		self.builder = gtk.Builder()
		self.builder.add_from_file(UI_FILE)
		self.window = self.builder.get_object("main")		
		self.xmms = xmms
		self.app_cover = cover()
					
		self.__properties__()
		self.__set_signals__()
		self.__set_hotkeys__()

		#self.initlogger()
		#self.logger.info('Iniciando Actividad')
		
	def __properties__(self):
		self.treeviewlist = self.builder.get_object("treeviewlist")
		self.insearch = self.builder.get_object("insearch")
		self.playerbar = self.builder.get_object("playerbar")
		self.playerbar.set_fraction(0)
		
		self.supported = ( 'mp1', 'mp2', 'mp3', 'm4a', 'm4p', 'ogg', 'flac', 'asf', 'wma', 'wav',
					'mpg', 'mpeg', 'm4v', 'mp4', 'avi', 'ogm', 'wmv',
					'mod', 'ape', 'apl', 'm4b', 'm4v', 'm4r', '3gp', 'aac', 
					'mpc', 'mp+', 'mpp', 'oga', 'sid')
			
		self.current_song = ""
		self.current_song_duration = 0
		self.status = None
		
		self.modelo = gtk.ListStore (int, str, 'gboolean')
		self.treeviewlist.set_model(self.modelo)
		
		render = gtk.CellRendererText() 
		render.set_property('cell-background', '#ddd')
		columna = gtk.TreeViewColumn ("name", render, text=1, cell_background_set=2)
		self.treeviewlist.append_column(columna)
		self.cellbackground = True

	def __set_signals__(self):
		self.insearch.connect("changed", self.search_song)
		self.treeviewlist.connect("key-press-event", self.treeviewlist_keypress)
		self.treeviewlist.connect("row-activated", self.treeviewlist_row_activated)
		self.window.connect("key-press-event", self.main_keypress)
		self.window.connect("configure-event", self.main_configure)
		self.window.connect("focus-out-event", self.main_focusout)
		self.window.connect("destroy", gtk.main_quit)
		self.xmms.playback_current_id(self.handler_playback_current_id)		
		self.xmms.playlist_list_entries('_active', self.get_tracks)				
		self.xmms.signal_playback_playtime(self.handler_set_time_track)
		self.xmms.playback_status(self.handler_playback_status)
		self.xmms.broadcast_playlist_changed(self.handler_playlist_change)
		self.xmms.broadcast_playback_current_id(self.handler_playback_current_id)
		self.xmms.broadcast_playback_status(self.handler_playback_status)

	def handler_playback_status(self, result):
		self.status = result.value()
	
	def handler_playlist_change(self, result):		
		update = result.value()

		if update['type']==0: #add			
			self.xmms.medialib_get_info(update['id'], self.add_track)
		elif update['type']==1:
			self.xmms.medialib_get_info(update['id'], self.add_track)
		elif update['type']==2: #shuffle
			self.modelo.clear()
			self.xmms.playlist_list_entries('_active', self.get_tracks)
		elif update['type']==3: #remove
			self.remove_track(update['position'])
		elif update['type']==4: #clear
			self.modelo.clear()
			self.treeviewlist.set_model(self.modelo)
		elif update['type']==5: #change positions
			self.modelo.swap(self.modelo[update['position']].iter, self.modelo[update['newposition']].iter)

	def handler_playback_current_id(self, result):						
		self.xmms.medialib_get_info(result.value(), self.set_track_player)

		# Select Row 		
		try:
			miter = self.get_iter(result.value())
			if miter and self.modelo == self.treeviewlist.get_model():
				self.treeviewlist.get_selection().select_iter(miter)
		except:
			print "Ocurrio un error al tratar de obtener la seleccion"

	def handler_set_time_track(self, result):
		total = result.value()
		min = total/(60*1000)
		sec = (total - min*1000*60)/1000

		if len(str(min))==1: min = "0%s" % min
		if len(str(sec))==1: sec = "0%s" % sec

		self.playerbar.set_text("%s:%s  %s" % (min, sec, self.current_song))

		progress = 0.0
		
		if self.current_song_duration > 0:
			progress = (int(total)*100/int(self.current_song_duration))/100.0			

		self.playerbar.set_fraction(progress)
			
	def set_track_player(self, result):
		track = self.get_taginfo(result.value())
		if track:
			self.current_song = "%s - %s" % (track[1],track[2])		
			self.current_song_duration = result.value()['duration']				
			
	def remove_track(self, position):
		try:
			self.modelo.remove(self.modelo[position].iter)
		except:
			print "Can't remove position: ", position
		
	def get_tracks(self, result):
		playlist = result.value()
		for element in playlist:
			self.xmms.medialib_get_info(element, self.add_track)

	def add_track(self, result):
		taginfo = self.get_taginfo(result.value())
		try:
			self.modelo.append([taginfo[0], "%s - %s" % (taginfo[1], taginfo[2]), self.cellbackground])		
			self.cellbackground = (True, False)[self.cellbackground==True]
		except:
			print "Can't to append: ", result.value()

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
		hdlr = logging.FileHandler('xmms2me.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)
		self.logger.setLevel(logging.INFO)

	def search_song(self, widget):
		modeltemp = gtk.ListStore (int, str, 'gboolean')

		cellbackground = True
		
		for i in self.modelo:						
			match = re.search(r'%s' % widget.get_text().lower(), self.modelo.get_value(i.iter, 1).lower())
			if match:
				modeltemp.append([self.modelo.get_value(i.iter, 0), self.modelo.get_value(i.iter, 1), cellbackground])
				cellbackground = (True, False)[cellbackground==True]

		self.treeviewlist.set_model(modeltemp)
		
	def treeviewlist_keypress(self, widget, event):
		try:
			sel = self.treeviewlist.get_selection().get_selected()
			id = widget.get_model().get_value(sel[1], 0)				

			if event.keyval	in [65363]: # Show Cover			
				try:								
					self.xmms.medialib_get_info(id, self.set_cover_information)
				except:
					print "Ocurrio un error en treeviewlist_keypress"						
			elif event.keyval == 65535: # Delete Item			
				try:								
					pos = self.get_song_position(id)
					self.xmms.playlist_remove_entry(pos,'_active')
					self.treeviewlist.set_model(self.modelo)
				except:
					print "Ocurrio un error al tratar de eliminar un item"
			else:
				self.app_cover.window.hide()
		except:
			return

	def set_cover_information(self, result):
		try:
			url_cover = "%s/.config/xmms2/bindata/%s" % (os.getenv("HOME"), result.value()['picture_front'])
		except:
			url_cover = "data/no-cover.jpg"

		taginfo = self.get_taginfo(result.value())
		self.app_cover.set_artist("Artist: %s" % taginfo[1])
		self.app_cover.set_song("%s" % taginfo[2])
		self.app_cover.set_album("Album: %s" % taginfo[3])
		self.app_cover.set_url(url_cover)
		self.app_cover.window.show()

	def treeviewlist_row_activated(self, widget, iter, path):
		modelo = widget.get_model()
		new_pos = self.get_song_position(int(modelo.get_value(modelo[iter[0]].iter, 0)))		
		self.xmms2_play(new_pos)
		
	def main_configure(self, widget, event):		
		width, height = self.window.get_size()
		x, y = self.window.get_position()
		
		self.window.get_position()
		self.app_cover.window.move(x+width+5,y+60)

	def main_focusout(self, widget, event):
		self.app_cover.window.hide()

	def main_keypress(self, widget, event):
		keyval = event.keyval
		name = gtk.gdk.keyval_name(keyval)
		mod = gtk.accelerator_get_label(keyval, event.state)
		mod = mod.replace("+Mod2","")

		#print mod, name, keyval

		if mod == "Ctrl+O":
			self.xmms2_open()
		elif mod == "Ctrl+L":
			self.xmms2_clear()

	def xmms2_open(self):
		
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
					print "Error to adding file %s" % ifile
		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, no files selected'

		dialog.destroy()
			
	def xmms2_clear(self):
		self.xmms.playlist_clear()
		
	def xmms2_next(self):
		self.xmms.playlist_set_next_rel(1)
		self.xmms.playback_tickle()

	def xmms2_prev(self):
		self.xmms.playlist_set_next_rel(-1)
		self.xmms.playback_tickle()

	#def xmms2_start(self):
	#	self.xmms.playback_start()

	#def xmms2_pause(self):
	#	self.xmms.playback_pause()		

	#def xmms2_stop(self):
	#	self.xmms.playback_stop()		
		
	def xmms2_play(self, pos):		
		self.xmms.playlist_set_next(pos)
		self.xmms.playback_tickle()		
		if self.status == 0:
			self.xmms.playback_start()
		
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
		
	def get_song_position(self, id):
		pos = 0
		if id > -1:
			for i in self.modelo:
				if i[0] == id:
					return pos
				pos+=1
		return 0

	def get_iter(self, id):
		for it in self.modelo:
			if it[0] == id:
				return it.iter
		return None
