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
from player import *

try:
    import gtk
except ImportError:
    sys.exit("pygtk not found.")

try:
	import xmmsclient
	import xmmsclient.glib
except ImportError:
	sys.exit("xmmsclient not found.")

ml = gobject.MainLoop(None, False)
xmms = xmmsclient.XMMS("azucar")

try:
	xmms.connect(os.getenv("XMMS_PATH"))
except IOError, detail:
	md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, "Connection failed: %s" % detail)
	md.run()
	md.destroy()
	sys.exit(1)
	
def main():
	conn = xmmsclient.glib.GLibConnector(xmms)
	app = player(xmms)
	app.window.show()	
	gtk.main()

if __name__ == "__main__":
    sys.exit(main())