#!/usr/bin/python
# -*- coding: utf-8 -*-

import gobject
import gtk
import pango
import os

class config:
    
    def __init__(self, xmms):
        self.builder = gtk.Builder()
        self.builder.add_from_file("data/config.ui")
        self.window = self.builder.get_object("window_config")
        
        self.xmms = xmms
        self.path_xmms2_config = "%s/.config/xmms2" % os.getenv("HOME")
        
        # audioscrobbler
        self.path_scrobbler_bin = "/usr/bin/xmms2-scrobbler"
        self.path_scrobbler_config = "%s/clients/xmms2-scrobbler" % self.path_xmms2_config 
        
        # lastfm
        self.path_scrobbler_lastfm = "%s/lastfm" % self.path_scrobbler_config        
        self.lastfm_handshake = "http://post.audioscrobbler.com" 
        
        self.__properties__()
        self.__set_signals__()
        self.__checks__()
        
    def __properties__(self):        
        # Generals
        self.bt_close = self.builder.get_object("bt_close")
        
        # Scrobbling
        # self.xmms.plugin_list(1, self.xmms2_list_plugins)
        self.ch_sc_status = self.builder.get_object("ch_scrobbler_status")
        self.lb_sc_info = self.builder.get_object("lb_scrobbler_info")        
        self.bt_sc_auto = self.builder.get_object("bt_scrobbler_auto")
        self.tx_sc_status = self.builder.get_object("tx_scrobbler_status")
        self.fx_login = self.builder.get_object("fx_login")
        self.in_sc_username = self.builder.get_object("in_scrobbler_username")
        self.in_sc_password = self.builder.get_object("in_scrobbler_password")
        self.bt_sc_save = self.builder.get_object("bt_scrobbler_save")
        
    def __set_signals__(self):
        self.bt_close.connect("clicked", self.close_window)
        self.bt_sc_save.connect("clicked", self.scrobbling_save_config)

    def __checks__(self):
        self.scrobbling_check_config()
            
    def close_window(self, widget=None):
        self.window.destroy()
    
    def show(self):
        self.window.show()
    
    def scrobbling_check_config(self):
        textbuffer = self.tx_sc_status.get_buffer()
        
        if self.xmms2_has_scrobbler():
            text_temp = " Xmms2-scrobbler installed: YES\n"
            self.ch_sc_status.set_active(True)
            
            text_configure_directory = ("NO","YES")[os.path.isdir(self.path_scrobbler_config)]
            text_configure_lastfm = ("NO","YES")[os.path.isdir(self.path_scrobbler_lastfm)]
            text_configure_lastfm_config = ("NO","YES")[os.path.isfile("%s/config" % self.path_scrobbler_lastfm)]
            
            text_temp += " Exist Xmms2 Configure Directory: %s\n" % text_configure_directory
            text_temp += " Exist Scrobbler Config Directory: %s\n" % text_configure_lastfm
            text_temp += " Exist LastFm Config File: %s\n" % text_configure_lastfm_config
            
            textbuffer.set_text(text_temp)
            
            if text_configure_directory == "YES" and text_configure_lastfm == "YES" and text_configure_lastfm_config == "YES": 
                self.bt_sc_auto.set_label("OK")
                self.bt_sc_auto.set_sensitive(False)
                
                config_file = open("%s/config" % self.path_scrobbler_lastfm, "r")
                lines = [i for i in config_file.readlines()] 
                
                if len(lines) > 2:
                    username = lines[0].split(": ")[1][:-1]
                    password = lines[1].split(": ")[1][:-1]                    
                    
                    self.in_sc_username.set_text(username)
                    self.in_sc_password.set_text(password)
                
                config_file.close()
                
                self.fx_login.set_visible(True)
        else:
            textbuffer.set_text(" Xmms2-scrobbler installed: NO")
            self.ch_sc_status.set_active(False)
            self.lb_sc_info.set_visible(False)
            self.bt_sc_auto.set_visible(False)        
    
    def scrobbling_save_config(self, widget=None):            
        config_file = open("%s/config" % self.path_scrobbler_lastfm, "w")
        config_file.write("user: %s\n" % self.in_sc_username.get_text())
        config_file.write("password: %s\n" % self.in_sc_password.get_text())
        config_file.write("handshake_url: %s\n" % self.lastfm_handshake)
        config_file.close()
        
    def xmms2_list_plugins(self, result):
        print result.value()
    
    def xmms2_has_scrobbler(self):
        if os.path.isfile(self.path_scrobbler_bin):
            return True
        return False
