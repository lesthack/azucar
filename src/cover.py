#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
#from mutagen import File

UI_FILE = "data/cover.ui"

class cover:
	def __init__(self):
		self.builder = gtk.Builder()
		self.builder.add_from_file(UI_FILE)
		self.window = self.builder.get_object("properties")
		self.album = self.builder.get_object("lb_album")
		self.artist = self.builder.get_object("lb_artist")
		self.song = self.builder.get_object("lb_song")
		self.image = self.builder.get_object("cover_image")

	def set_album(self, _album):
		self.album.set_text(_album)

	def set_artist(self, _artist):
		self.artist.set_text(_artist)

	def set_song(self, _song):
		self.song.set_text(_song)

	def set_url(self, url):
		pixbuf = gtk.gdk.pixbuf_new_from_file(url)
		scaled_buf = pixbuf.scale_simple(100,100,gtk.gdk.INTERP_BILINEAR)
		self.image.set_from_pixbuf(scaled_buf)
