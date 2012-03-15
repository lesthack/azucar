#!/usr/bin/python
# -*- coding: utf-8 -*-

class album:    
    def __init__(self, album, artist, url_cover):
        self.album = album
        self.artist = artist
        self.url_cover = url_cover
        
class albums:
    def __init__(self):
        self.list = []
        self._list = []
        pass
    
    def add_album(self, album, artist, url_cover):
        if album not in self.list:
            self.list.append(album)
            self._list.append( album(album, artist, url_cover) )    
    
    def get_album(self, album):
        if album in self.list:
            pass
    
    
    
    
    
    
    
    
