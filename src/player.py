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
		
		#self.load_music()
		
		#self.initlogger()
		#self.logger.info('Iniciando Actividad')
		
	def __properties__(self):
		self.treeviewlist = self.builder.get_object("treeviewlist")
		self.insearch = self.builder.get_object("insearch")		

		self.modelo = gtk.ListStore (int, str)
		self.treeviewlist.set_model(self.modelo)
		
		render = gtk.CellRendererText() 
		columna = gtk.TreeViewColumn ("name", render, text=1)
		self.treeviewlist.append_column(columna)

	def __set_signals__(self):
		self.insearch.connect("changed", self.search_song)
		self.treeviewlist.connect("key-press-event", self.treeviewlist_keypress)
		self.window.connect("configure-event", self.main_configure)
		self.window.connect("focus-out-event", self.main_focusout)
		self.window.connect("destroy", gtk.main_quit)
		self.xmms.broadcast_playlist_changed(self.handler_playlist_change)
		self.xmms.playlist_list_entries('_active', self.get_tracks)

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
			print "Cambiar posición", update

	def remove_track(self, position):
		self.modelo.remove(self.modelo[position].iter)
		
	def get_tracks(self, result):
		playlist = result.value()
		for element in playlist:
			print element
			self.xmms.medialib_get_info(element, self.add_track)

	def add_track(self, result):
		taginfo = self.get_taginfo(result.value())
		self.modelo.append([taginfo[0], "%s - %s" % (taginfo[1], taginfo[2])])

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
	
	def load_music(self):
		music = open("data/music.lst","r")
		
		for i in music.readlines():
			self.modelo.append([1, i[:-1]])
			
	def initlogger(self):
		self.logger = logging.getLogger('xmms2me')
		hdlr = logging.FileHandler('xmms2me.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)
		self.logger.setLevel(logging.INFO)

	def search_song(self, widget):
		modeltemp = gtk.ListStore (int, str)

		for i in self.modelo:						
			match = re.search(r'%s' % widget.get_text().lower(), self.modelo.get_value(i.iter, 1).lower())
			if match:
				modeltemp.append([1, self.modelo.get_value(i.iter, 1)])

		self.treeviewlist.set_model(modeltemp)

	def treeviewlist_keypress(self, widget, event):				
		if event.keyval	in [65293, 65364, 65362]:
			self.app_cover.set_song("Esta es una canción mona: %s" % event.keyval)
			self.app_cover.window.show()

		elif event.keyval == 65307:
			self.app_cover.window.hide()

	def main_configure(self, widget, event):		
		width, height = self.window.get_size()
		x, y = self.window.get_position()
		
		self.window.get_position()
		self.app_cover.window.move(x+width+5,y+100)

	def main_focusout(self, widget, event):
		self.app_cover.window.hide()

	def get_filename(self, url):		
		n = url.split('/')

		try:
		    name = n[-1][:-4]
		except:
		    name = ""

		return name.replace('+',' ')
    