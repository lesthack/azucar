#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject
import gtk
import re
import os
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
		
		#self.initlogger()
		#self.logger.info('Iniciando Actividad')
		
	def __properties__(self):
		self.treeviewlist = self.builder.get_object("treeviewlist")
		self.insearch = self.builder.get_object("insearch")
		self.playerbar = self.builder.get_object("playerbar")
		self.current_song = ""
		self.current_song_id = -1
		self.current_song_duration = 0
		
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
		self.xmms.broadcast_playlist_changed(self.handler_playlist_change)
		self.xmms.broadcast_playback_current_id(self.handler_playback_current_id)
		self.xmms.playlist_list_entries('_active', self.get_tracks)		
		self.xmms.signal_playback_playtime(self.handler_set_time_track)		
		
	def handler_playlist_change(self, result):		
		update = result.value()
		print update
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
		elif update['type']==5: #change positions
			self.modelo.swap(self.modelo[update['position']].iter, self.modelo[update['newposition']].iter)

	def handler_playback_current_id(self, result):
		self.xmms.medialib_get_info(result.value(), self.set_track_player)

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
		self.current_song_id = track[0]
		self.current_song = "%s - %s" % (track[1],track[2])		
		self.current_song_duration = result.value()['duration']				
		
	def remove_track(self, position):
		self.modelo.remove(self.modelo[position].iter)
		
	def get_tracks(self, result):
		playlist = result.value()
		for element in playlist:
			self.xmms.medialib_get_info(element, self.add_track)

	def add_track(self, result):
		taginfo = self.get_taginfo(result.value())
		self.modelo.append([taginfo[0], "%s - %s" % (taginfo[1], taginfo[2]), self.cellbackground])		
		self.cellbackground = (True, False)[self.cellbackground==True]		

	def get_taginfo(self, info):
		track = []

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
				modeltemp.append([1, self.modelo.get_value(i.iter, 1), cellbackground])
				cellbackground = (True, False)[cellbackground==True]

		self.treeviewlist.set_model(modeltemp)
		
	def treeviewlist_keypress(self, widget, event):
		sel = self.treeviewlist.get_selection().get_selected()
		print self.modelo.get_value(sel[1], 0)
		
		if event.keyval	in [65363]:			
			#set cover
			self.app_cover.set_artist("")
			self.app_cover.set_song("")
			self.app_cover.set_album("")
			self.app_cover.window.show()
		else:
		#elif event.keyval == 65307:
			self.app_cover.window.hide()

	def treeviewlist_row_activated(self, widget, iter, path):
		new_pos = self.get_song_position(int(self.modelo.get_value(self.modelo[iter[0]].iter, 0)))
		act_pos = self.get_song_position(self.current_song_id)
		self.xmms2_play(new_pos-act_pos)
		
	def main_configure(self, widget, event):		
		width, height = self.window.get_size()
		x, y = self.window.get_position()
		
		self.window.get_position()
		self.app_cover.window.move(x+width+5,y+100)

	def main_focusout(self, widget, event):
		self.app_cover.window.hide()

	def main_keypress(self, widget, event):
		keyval = event.keyval
		name = gtk.gdk.keyval_name(keyval)
		mod = gtk.accelerator_get_label(keyval, event.state)
		#print mod, keyval

		if mod == "Ctrl+F":
			self.xmms2_next()
		elif mod == "Ctrl+A":
			self.xmms2_prev()
		elif mod == "Ctrl+S":
			self.xmms2_pause()	
		elif mod == "Ctrl+D":
			self.xmms2_start()
			
	def xmms2_next(self):
		self.xmms.playlist_set_next_rel(1)
		self.xmms.playback_tickle()

	def xmms2_prev(self):
		self.xmms.playlist_set_next_rel(-1)
		self.xmms.playback_tickle()

	def xmms2_start(self):
		self.xmms.playback_start()		

	def xmms2_pause(self):
		self.xmms.playback_pause()		

	def xmms2_play(self, pos):
		self.xmms.playlist_set_next_rel(pos)
		self.xmms.playback_tickle()
		
	def get_filename(self, url):		
		n = url.split('/')

		try:
		    name = n[-1][:-4]
		except:
		    name = ""

		return name.replace('+',' ')

	def get_song_position(self, pos):
		npos = 0
		if self.current_song_id > -1:
			for i in self.modelo:
				if i[0] == pos:
					return npos
				npos+=1
		return -1