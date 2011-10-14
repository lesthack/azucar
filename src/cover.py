#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk

UI_FILE = "data/cover.ui"

class cover:
	def __init__(self):
		self.builder = gtk.Builder()
		self.builder.add_from_file(UI_FILE)
		self.window = self.builder.get_object("properties")
		self.album = self.builder.get_object("lb_album")
		self.artist = self.builder.get_object("lb_artist")
		self.song = self.builder.get_object("lb_song")

	def set_album(self, _album):
		self.album.set_text(_album)

	def set_artist(self, _artist):
		self.artist.set_text(_artist)

	def set_song(self, _song):
		self.song.set_text(_song)
