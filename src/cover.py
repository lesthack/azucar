#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject
import gtk

class cover(gtk.Table):
    def __init__(self, rows, columns, homo):
        gtk.Table.__init__(self, rows, columns, homo)
        self.total_rows = 5        
        self.row = 0
        self.column = 0
        
    def addCover(self):    
        gtkimage = gtk.Image()                
        gtkimage.set_from_file("data/no-cover.jpg")                
        gtkimage.show()
        gtkbutton = gtk.Button()
        gtkbutton.add(gtkimage)
        gtkbutton.set_size_request(106, 106)
        gtkbutton.show()
        
        self.attach(gtkbutton, 
            self.row, self.row+1, 
            self.column, self.column+1, 
            gtk.FILL, gtk.FILL, 
            0, 0)
        
        if self.row < (self.total_rows-1):
            self.row += 1
        else:
            self.row = 0
            self.column += 1
            self.resize(self.total_rows, self.column + 1)
