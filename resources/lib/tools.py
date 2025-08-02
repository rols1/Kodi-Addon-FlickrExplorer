# -*- coding: utf-8 -*-
# tools.py	Teil von Kodi-Addon-FlickrExplorer
#
# Stand: 25.07.2025

# Python3-Kompatibilität:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs
# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

# Standard:
import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:					
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve 
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse , urlsplit, parse_qs 
	LOG_MSG = xbmc.LOGNOTICE 				# s. PLog
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	LOG_MSG = xbmc.LOGINFO 					# s. PLog
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass

# Addonmodule:
from resources.lib.util_flickr import *
from flickrexplorer import *
PLog("tools.py_loaded")

# Globals
ADDON_ID      	= 'plugin.image.flickrexplorer'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')		# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]						# plugin://plugin.image.flickrexplorer/
HANDLE			= int(sys.argv[1])

################################################################################

#----------------------------------------------------------------
# Kontextmenü 
# Aufruf ShowPhotoObject -> addContextMenuItems -> RunScript
# mtitle: Kontextmenü-Title
# 
def Context1(title, thumb, owner, pid, mtitle):
	PLog('Context1:'); 
	PLog(title);  PLog(mtitle); PLog(thumb); PLog(pid); PLog(owner); 
	params = "%s###%s###%s###%s" % (title, thumb, owner, pid)
	dirID =	"Context_Info"								
	Dict("store", "Context_Params", params)			# Context_Info entpackt Dict
	
	fparams="&fparams={'mtitle': '%s'}" % mtitle	
	action="action=dirList&dirID=%s&fparams=%s"	% (dirID, fparams)
	PLog("action_Context1: " + action)
	action=quote(action)
	
	xbmc.executebuiltin('RunAddon(%s, %s)'  % (ADDON_ID, action))
	
#----------------------------------------------------------------




















