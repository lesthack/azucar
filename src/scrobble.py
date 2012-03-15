#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import os
from xml.dom.minidom import parse, parseString

class scrobble:
    def __init__(self, path_temp, path_default):
        self.__api_key__ = "b25b959554ed76058ac220b7b2e0a026"        
        self.ws = "http://ws.audioscrobbler.com/2.0/"
        self.path = path_temp
        self.path_default = path_default
        
    def get_apikey(self):
        return self.__api_key__
    
    def __read_url_data__(self, params):
        data = urllib.urlencode(params)
        try:
            request = urllib2.urlopen(self.ws, data)
            return request.read().encode('utf-8')
        except Exception as error:
            print "ocurrio un error:", error
    
    def __get_text__(self, nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)
        
    def get_album_info(self, artist, album):
        method = "album.getinfo"
        params = {"method": method,
                  "api_key": self.get_apikey(),
                  "artist": artist,
                  "album": album }
                
        xml_pure = self.__read_url_data__(params)
        
        dom = parseString(xml_pure)        
        images = dom.getElementsByTagName("image")
                
        for image in images:
            if image.attributes.getNamedItem("size").value == "large":
                try:
                    url_image = self.__get_text__(image.childNodes)                
                    path_image = "%s/currentcover.%s" % (self.path, url_image[-3:])
                    request = urllib.urlretrieve(url_image, path_image )
                    print path_image
                    return path_image
                except:
                    return self.path_default
                
