# Azucar
### A xmms2 Frontend

[![Azucar](http://lesthack.com.mx/wp-content/uploads/2011/12/azucar-xmms2-2.png)](http://lesthack.com.mx/wp-content/uploads/2011/12/azucar-xmms2-2.png)

You might have heard of XMMS (legacy.xmms2.org), the hugely popular Winamp clone for Linux and UNIX-like operating systems. XMMS2 is a project started (in late 2002) by one of XMMS's original authors - Peter Alm - to produce a "kick-ass music player" (much like the world's 347349739921 other music player projects). In short, XMMS2 is the next generation XMMS.

So, XMMS2 is definitely an audio player. But it is not a general multimedia player - it will not play videos. It has a modular framework and plugin architecture for audio processing, visualisation and output, but this framework has not been designed to support video. Also the client-server design of XMMS2 (and the daemon being independent of any graphics output) practically prevents direct video output being implemented.

Azucar is a xmms2 frontend worked in python.

Librarys:

* xmmsclient
* xmmsclient.glib  
* gtk
* gobject
* pango
* keybinder
* logging
* pynotify

You can try now:
 
  Debian/Ubuntu
    
    $ git clone git://github.com/lesthack/azucar.git
    $ sudo apt-get install python-gtk2 python-keybinder python-notify xmms2 python-xmmsclient
    $ cd azucar
    $ python azucar.py