#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# main.py
# Copyright (C) Jorge Luis Hernandez 2011 <lesthack@gmail.com>
# 
# xmms2me is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# xmms2me is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import gobject

try:
    __file__
except NameError:
    pass
else:
    libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    sys.path.insert(0, libdir)

from player import player

try:
    import gtk
except ImportError:
    sys.exit("pygtk not found.")

try:
	import keybinder
except:
	sys.exit("python-keybinder not found.")
	
try:
	import xmmsclient
	import xmmsclient.glib
except ImportError:
	sys.exit("xmmsclient not found.")

ml = gobject.MainLoop(None, False)
xmms = xmmsclient.XMMS("azucar")

try:
	xmms.connect(os.getenv("XMMS_PATH"))
	status = True 
except IOError, detail:
	status = False

if not status:
	try:
		os.system("xmms2-launcher")
		xmms.connect(os.getenv("XMMS_PATH"))
	except:
		sys.exit("xmms2 server not found")
try:
	import logging
except ImportError:
	sys.exit("loggin not found")
	
def main():
	conn = xmmsclient.glib.GLibConnector(xmms)
	app = player(xmms)
	app.window.show()	
	gtk.main()

if __name__ == "__main__":
    sys.exit(main())