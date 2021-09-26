# -*- coding: utf-8 -*-

# Python3-Kompatibilität:
from __future__ import absolute_import		# sucht erst top-level statt im akt. Verz. 
from __future__ import division				# // -> int, / -> float
from __future__ import print_function		# PYTHON2-Statement -> Funktion
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

# o. Auswirkung auf die unicode-Strings in PYTHON3:
from kodi_six.utils import py2_encode, py2_decode

import os, sys
PYTHON2 = sys.version_info.major == 2
PYTHON3 = sys.version_info.major == 3
if PYTHON2:
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode, urlretrieve
	from urllib2 import Request, urlopen, URLError 
	from urlparse import urljoin, urlparse, urlunparse, urlsplit, parse_qs
elif PYTHON3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError
	try:									# https://github.com/xbmc/xbmc/pull/18345 (Matrix 19.0-alpha 2)
		xbmc.translatePath = xbmcvfs.translatePath
	except:
		pass


# Python
import ssl				# HTTPS-Handshake
from io import BytesIO	# Python2+3 -> get_page (compressed Content), Ersatz für StringIO
import gzip, zipfile

from threading import Thread	# thread_getpic
import shutil					# thread_getpic

import json				# json -> Textstrings
import re				# u.a. Reguläre Ausdrücke
import math				# für math.ceil (aufrunden)

import resources.lib.updater 			as updater		

# Addonmodule + Funktionsziele (util_imports.py)
import resources.lib.util_flickr as util

PLog=util.PLog; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
UtfToStr=util.UtfToStr; addDir=util.addDir; R=util.R; RLoad=util.RLoad; RSave=util.RSave; 
repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; DirectoryNavigator=util.DirectoryNavigator; 
stringextract=util.stringextract; blockextract=util.blockextract; 
cleanhtml=util.cleanhtml; decode_url=util.decode_url; unescape=util.unescape; 
transl_json=util.transl_json; repl_json_chars=util.repl_json_chars; seconds_translate=util.seconds_translate; 
get_keyboard_input=util.get_keyboard_input; L=util.L; RequestUrl=util.RequestUrl; PlayVideo=util.PlayVideo;
make_filenames=util.make_filenames; CheckStorage=util.CheckStorage; MyDialog=util.MyDialog;
del_slides=util.del_slides;

# +++++ FlickrExplorer  - Addon Kodi-Version, migriert von der Plexmediaserver-Version +++++

VERSION =  '0.7.3'	
VDATE = '15.10.2020'
 
# 
#	
#
# (c) 2019 by Roland Scholz, rols1@gmx.de
# 
# 	Licensed under MIT License (MIT)
# 	(previously licensed under GPL 3.0)
# 	A copy of the License you find here:
#		https://github.com/rols1/Kodi-Addon-FlickrExplorer/blob/master/LICENSE.md
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# Flickr:		https://www.flickr.com/
# Wikipedia:	https://de.wikipedia.org/wiki/Flickr


FANART 				= 'art-flickr.png'		# Hintergrund			
ICON_FLICKR 		= 'icon-flickr.png'						
ICON_SEARCH 		= 'icon-search.png'						
ICON_FOLDER			= 'Dir-folder.png'

ICON_OK 			= "icon-ok.png"
ICON_WARNING 		= "icon-warning.png"
ICON_NEXT 			= "icon-next.png"
ICON_CANCEL 		= "icon-error.png"
ICON_MEHR 			= "icon-mehr.png"
ICON_MEHR_1 		= "icon-mehr_1.png"
ICON_MEHR_10 		= "icon-mehr_10.png"
ICON_MEHR_100 		= "icon-mehr_100.png"
ICON_MEHR_500 		= "icon-mehr_500.png"
ICON_WENIGER_1		= "icon-weniger_1.png"
ICON_WENIGER_10  	= "icon-weniger_10.png"
ICON_WENIGER_100 	= "icon-weniger_100.png"
ICON_WENIGER_500 	= "icon-weniger_500.png"

ICON_WORK 			= "icon-work.png"

ICON_GALLERY 		= "icon-gallery.png"

ICON_MAIN_UPDATER	= 'plugin-update.png'		
ICON_UPDATER_NEW 	= 'plugin-update-new.png'
ICON_INFO 			= "icon-info.png"

NAME		= 'FlickrExplorer'

BASE 				= "https://www.flickr.com"
GALLERY_PATH 		= "https://www.flickr.com/photos/flickr/galleries/"
PHOTO_PATH 			= "https://www.flickr.com/photos/"

REPO_NAME		 	= 'Kodi-Addon-FlickrExplorer'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME
REPO_URL 			= 'https://github.com/{0}/releases/latest'.format(GITHUB_REPOSITORY)


PLog('Addon: lade Code')
PluginAbsPath 	= os.path.dirname(os.path.abspath(__file__))			# abs. Pfad für Dateioperationen
RESOURCES_PATH	=  os.path.join("%s", 'resources') % PluginAbsPath
ADDON_ID      	= 'plugin.image.flickrexplorer'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]
HANDLE			= int(sys.argv[1])

PLog("ICON: " + R(ICON_FLICKR))
TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLog("ADDON_DATA: " + ADDON_DATA)

DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
SLIDESTORE 		= os.path.join("%s/slides") % ADDON_DATA
PLog(DICTSTORE); 

check 			= check_DataStores()	# Check /Initialisierung / Migration 
PLog('check: ' + str(check))
										
try:	# 28.11.2019 exceptions.IOError möglich, Bsp. iOS ARM (Thumb) 32-bit
	from platform import system, architecture, machine, release, version	# Debug
	OS_SYSTEM = system()
	OS_ARCH_BIT = architecture()[0]
	OS_ARCH_LINK = architecture()[1]
	OS_MACHINE = machine()
	OS_RELEASE = release()
	OS_VERSION = version()
	OS_DETECT = OS_SYSTEM + '-' + OS_ARCH_BIT + '-' + OS_ARCH_LINK
	OS_DETECT += ' | host: [%s][%s][%s]' %(OS_MACHINE, OS_RELEASE, OS_VERSION)
except:
	OS_DETECT =''
	
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')
	
PLog('Addon: ClearUp')
ARDStartCacheTime = 300						# 5 Min.	
 
# Dict: Simpler Ersatz für Dict-Modul aus Plex-Framework
days = SETTINGS.getSetting('DICT_store_days')
if days == 'delete':						# slides-Ordner löschen 
	del_slides(SLIDESTORE)
	SETTINGS.setSetting('DICT_store_days','100')
	xbmc.sleep(100)
	days = 100
else:
	days = int(days)
Dict('ClearUp', days)				# Dict bereinigen 
	
																		
####################################################################################################		
# Auswahl Sprachdatei / Browser-locale-setting	
# Locale-Probleme unter Plex s. Plex-Version
# 	hier Ersatz der Plex-Funktion Locale.LocalString durch einfachen Textvergleich - 
#	s. util.L
# Kodi aktualisiert nicht autom., daher Aktualsierung jeweils in home.

def ValidatePrefs():	
	PLog('ValidatePrefs:')
			
	try:
		lang =  SETTINGS.getSetting('language').split('/') # Format Bsp.: "English/en/en_GB"
		loc  = str(lang[1])				# en
		if len(lang) >= 2:
			loc_browser = str(lang[2])	# en_GB
		else:
			loc_browser = loc			# Kennungen identisch
	except Exception as exception:
		PLog(repr(exception))
		loc 		= 'en'				# Fallback (Problem Setting)
		loc_browser = 'en-US'
				
	loc_file =  os.path.join("%s", "%s", "%s") % (RESOURCES_PATH, "Strings", '%s.json' % loc)
	PLog(loc_file)	
	
	if os.path.exists(loc_file) == False:	# Fallback Sprachdatei: englisch
		loc_file =  os.path.join("%s", "%s", "%s") % (RESOURCES_PATH, "Strings", 'en.json')
		
	Dict('store', 'loc', loc) 	
	Dict('store', 'loc_file', loc_file) 		
	Dict('store', 'loc_browser', loc_browser)
	
	PLog('loc: %s' % loc)
	PLog('loc_file: %s' % loc_file)
	PLog('loc_browser: %s' % loc_browser)
	
####################################################################################################
def Main():
	PLog('Main:'); 
	PLog('Addon-Version: ' + VERSION); PLog('Addon-Datum: ' + VDATE)	
	PLog(OS_DETECT)	
	PLog('Addon-Python-Version: %s'  % sys.version)
	PLog('Kodi-Version: %s'  % KODI_VERSION)
			
	PLog(PluginAbsPath)	
											
	ValidatePrefs()
	li = xbmcgui.ListItem()
						
	title=L('Suche') + ': ' +  L('im oeffentlichen Inhalt')

	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_SEARCH), thumb=R(ICON_SEARCH), 
		fparams=fparams, summary=L('Suchbegriff im Suchfeld eingeben und Return druecken'))
		
	if SETTINGS.getSetting('username'):							# Menü MyFlickr für angemeldete User
		summ = 'User: ' + SETTINGS.getSetting('username')
		fparams="&fparams={}"
		addDir(li=li, label='MyFlickr', action="dirList", dirID="MyMenu", fanart=R('icon-my.png'), thumb=R('icon-my.png'), 
			fparams=fparams, summary=summ)
			
	title=L('Photostream')	
	summ = L('Fotos') + ' ' + L('im oeffentlichen Inhalt') 							
	fparams="&fparams={'query': 'None', 'user_id': 'None'}" 
	addDir(li=li, label=title, action="dirList", dirID="Search_Work", fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), 
		fparams=fparams, summary=summ)
		
	title = L('Web Galleries')
	fparams="&fparams={'pagenr': '1'}"
	addDir(li=li, label=title, action="dirList", dirID="WebGalleries", fanart=R(ICON_GALLERY), thumb=R(ICON_GALLERY), 
		fparams=fparams)

	title = L('Flickr Nutzer')
	summ = L("Suche Nutzer und ihre Inhalte") + ': '  + str(SETTINGS.getSetting('FlickrPeople'))	
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="FlickrPeople", fanart=R('icon-user.png'), thumb=R('icon-user.png'), 
		fparams=fparams, summary=summ)
	
	# Updater-Modul einbinden:		
	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if SETTINGS.getSetting('pref_info_update') == 'true': # Updatehinweis beim Start des Addons 
		ret = updater.update_available(VERSION)
		if ret[0] == False:		
			msg1 = L("Github ist nicht errreichbar")
			msg2 = 'update_available: False'
			PLog("%s | %s" % (msg1, msg2))
			MyDialog(msg1, msg2, '')
		else:
			int_lv = ret[0]			# Version Github
			int_lc = ret[1]			# Version aktuell
			latest_version = ret[2]	# Version Github, Format 1.4.1
			
			if int_lv > int_lc:								# Update-Button "installieren" zeigen
				call_update = True
				title = 'neues Update vorhanden - jetzt installieren'
				summary = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
				# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
				url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
				url=py2_encode(url);
				fparams="&fparams={'url': '%s', 'ver': '%s'}" % (quote_plus(url), latest_version) 
				addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(FANART), 
					thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
			
	if call_update == False:							# Update-Button "Suche" zeigen	
		title = 'Addon-Update | akt. Version: ' + VERSION + ' vom ' + VDATE	
		summary='Suche nach neuen Updates starten'
		tagline='Bezugsquelle: ' + repo_url			
		fparams="&fparams={'title': 'Addon-Update'}"
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(FANART), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams, summary=summary, tagline=tagline)
	
	# Info-Button
	summary = L('Stoerungsmeldungen an Forum oder rols1@gmx.de')
	tagline = u'für weitere Infos (changelog.txt) klicken'
	path = os.path.join(ADDON_PATH, "changelog.txt") 
	title = u"Änderungsliste (changelog.txt)"
	path=py2_encode(path); title=py2_encode(title); 
	fparams="&fparams={'path': '%s', 'title': '%s'}" % (quote(path), quote(title))
	addDir(li=li, label='Info', action="dirList", dirID="ShowText", fanart=R(FANART), thumb=R(ICON_INFO), 
		fparams=fparams, summary=summary, tagline=tagline)
	

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
#----------------------------------------------------------------
def ShowText(path, title):
	PLog('ShowText:'); 
	page = RLoad(path, abs_path=True)
	page = page.replace('\t', ' ')		# ersetze Tab's durch Blanks
	dialog = xbmcgui.Dialog()
	dialog.textviewer(title, page)
	return
#----------------------------------------------------------------

# sender neu belegt in Senderwahl (Classic: deaktiviert) 
####################################################################################################
# Doppelnutzung MyMenu:  SETTINGS.getSetting('username') + FlickrPeople 
#
# Rücksprung aus MyMenu/User				-> Main
# Rücksprung aus MyMenu/SETTINGS.getSetting('username')	-> FlickrPeople
# Rücksprung aus Untermenüs	ohne user_id	-> Main
# Rücksprung aus Untermenüs	mit user_id		-> MyMenu 
#
def home(li,user_id,username='', returnto=''):		 
	PLog('home:')					# eingetragener User (Einstellungen)
	PLog('user_id: %s, username: %s, returnto: %s' % (str(user_id), str(username), str(returnto)))	
	
	li = xbmcgui.ListItem()
	
	if returnto == 'FlickrPeople':				# MyMenu -> FlickrPeople 
		title = py2_decode(L('Zurueck zu')) + ' ' + py2_decode(L('Flickr Nutzer'))
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="FlickrPeople", fanart=R('homePeople.png'), 
			thumb=R('homePeople.png'), fparams=fparams)
		return li
		
	if returnto == 'Main':
		title = L('Zurueck zum Hauptmenue')		# MyMenu -> Hauptmenue
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R('home.png'), 
		thumb=R('home.png'), fparams=fparams)
		return li

	if user_id:									# Untermenüs: User (SETTINGS.getSetting('username') oder Flickr People)
		if username == '':
			user_id,nsid,username,realname = GetUserID(user_id) 					
		title = py2_decode(L('Zurueck zu')) + ' ' + username
		username=py2_encode(username); user_id=py2_encode(user_id); 
		fparams="&fparams={'username': '%s', 'user_id': '%s'}"  % (quote(username), quote(user_id))
		addDir(li=li, label=title, action="dirList", dirID="MyMenu", fanart=R('homePeople.png'), 
			thumb=R('homePeople.png'), fparams=fparams)
		return li
		
	title = L('Zurueck zum Hauptmenue')			# Untermenüs:  ohne user_id
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R('home.png'), thumb=R('home.png'), fparams=fparams)

	return li
	
####################################################################################################
# Userabhängige Menüs 
# 2-fache Verwendung:
#	1. Aufrufer Main 			- für den User aus Einstellungen SETTINGS.getSetting('username')
#	2. Aufrufer FlickrPeople 	- für einen ausgewählten User aus FlickrPeople 
#
def MyMenu(username='',user_id=''):
	PLog('MyMenu:')
	PLog('user_id: %s, username: %s' % (str(user_id), str(username)))	
		
	if username=='' and user_id=='':								# aus Main, User aus Einstellungen
		if SETTINGS.getSetting('username'):								
			user = SETTINGS.getSetting('username').strip()
			user_id,nsid,username,realname = GetUserID(user) 
			# Ergebnis zusätzl. in Dicts (nicht bei ausgewählten usern (FlickrPeople):
			Dict('store', 'user', user); Dict('store', 'nsid', nsid); Dict('store', 'username', username);  
			Dict('store', 'realname', realname); 
			PLog('user_id: %s, nsid: %s, username: %s, realname: %s' % (user_id,nsid,username,realname))
			
			if 'User not found'	in user_id:							# err code aus GetUserID
				msg1 = L("User not found") + ': %s' % user	
				MyDialog(msg1, '', '')
				return 
				
	PLog(Dict('load','nsid'))
	nsid = user_id				
	if nsid == Dict('load','nsid'):	
		returnto ='Main' 
	else:
		returnto ='FlickrPeople' 	

	li = xbmcgui.ListItem()
	li = home(li, user_id=user_id, returnto=returnto)				# Home-Button
	
	title = 'Search: content owned by %s' % (username)
	summ = L('Suche') + ' ' + L('Fotos')
	title=py2_encode(title);
	fparams="&fparams={'user_id': '%s', 'title': '%s'}"  % (nsid, quote(title))
	addDir(li=li, label=title, action="dirList", dirID="Search", fanart=R(ICON_SEARCH), thumb=R(ICON_SEARCH), 
		fparams=fparams, summary=summ)
	
	title='%s: Photostream'	% username							
	fparams="&fparams={'query': '%s', 'user_id': '%s'}" % (quote('&Photostream&'), nsid)
	addDir(li=li, label=title, action="dirList", dirID="Search_Work", fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), 
		fparams=fparams, summary=title)
				
	title='%s: Albums'	% username
	title=py2_encode(title);		
	fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '1'}" % ( quote(title), nsid)
	addDir(li=li, label=title, action="dirList", dirID="MyAlbums", fanart=R('icon-album.png'), thumb=R('icon-album.png'), 
		fparams=fparams, summary=title)
				
	title='%s: Galleries'	% username	
	title=py2_encode(title);	
	fparams="&fparams={'title': '%s', 'user_id': '%s'}" % (quote(title), nsid)
	addDir(li=li, label=title, action="dirList", dirID="MyGalleries", fanart=R('icon-gallery.png'), 
		thumb=R('icon-gallery.png'), fparams=fparams, summary=title)
				
	title='%s: Faves'	% username		
	fparams="&fparams={'query': '%s', 'user_id': '%s'}" % (quote('&Faves&'), nsid)
	addDir(li=li, label=title, action="dirList", dirID="Search_Work", fanart=R('icon-fav.png'), thumb=R('icon-fav.png'), 
		fparams=fparams, summary=title)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
			
#------------------------------------------------------------------------------------------
# Begrenzung der Anzahl auf 100 festgelegt. Keine Vorgabe in Einstellungen, da Flickr unterschiedlich mit
#	den Mengen umgeht (seitenweise, einzeln, ohne). Z.B. in galleries.getList nur 1 Seite - Mehr-Sprünge daher
#	mit max_count=100.
#	Flickr-Ausgabe im xml-Format.
def MyGalleries(title, user_id, offset=0):
	PLog('MyGalleries:'); PLog('offset: ' + str(offset))
	offset = int(offset)
	title_org = title
	max_count = 100									# Begrenzung fest wie Flickr Default
	

	path = BuildPath(method='flickr.galleries.getList', query_flickr='', user_id=user_id, pagenr=1)
				
	page, msg = RequestUrl(CallerName='MyGalleries', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return 
	PLog(page[:100])
		
	cnt = stringextract('total="', '"', page)					# im  Header
	pages = stringextract('pages="', '"', page)
	PLog('Galleries: %s, Seiten: %s' % (cnt, pages))
	if cnt == '0' or pages == '':
		msg1 = L('Keine Gallerien gefunden')
		MyDialog(msg1, '', '')
		return 
		
	li = xbmcgui.ListItem()
	li = home(li, user_id=user_id)		# Home-Button
		
	records = blockextract('<gallery id', '', page)
	pagemax = int(len(records))
	PLog('total: ' + str(pagemax))
	
	i=0 + offset
	loop_i = 0		# Schleifenzähler
	# PLog(records[i])
	for r in records:
		title 		= stringextract('<title>', '</title>', records[i])
		title		= unescape(title)
		url 		= stringextract('url="', '"', records[i])
		username 	= stringextract('username="', '"', records[i])
		count_photos = stringextract('count_photos="', '"', records[i])
		summ = '%s: %s %s' % (username, count_photos, L('Fotos'))
		img_src = R(ICON_FLICKR)
		i=i+1; loop_i=loop_i+1
		if i >= pagemax:
			break
		if loop_i > max_count:
			break
		
		gallery_id = url.split('/')[-1]		# Bsp. 72157697209149355
		if url.endswith('/'):
			gallery_id = url.split('/')[-2]	# Url-Ende bei FlickrPeople ohne / 	
				
		PLog(i); PLog(url);PLog(title);PLog(img_src); PLog(gallery_id);
		title=py2_encode(title);
		fparams="&fparams={'title': '%s', 'gallery_id': '%s', 'user_id': '%s'}" % (quote(title), gallery_id, user_id)
		addDir(li=li, label=title, action="dirList", dirID="Gallery_single", fanart=R(img_src), thumb=R(img_src), 
			fparams=fparams, summary=summ)
				
	PLog(offset); PLog(pagemax); 					# pagemax hier Anzahl Galleries
	tag = 'total: %s ' % pagemax + L('Galerien')
	name = title_org
	if (int(offset)+100) < int(pagemax):
		offset = min(int(offset) +100, pagemax)
		PLog(offset)
		title_org=py2_encode(title_org);
		fparams="&fparams={'title': '%s', 'offset': '%s'}" % (quote(title_org), offset)
		addDir(li=li, label=title_org, action="dirList", dirID="MyGalleries", fanart=R(ICON_MEHR_100), 
			thumb=R(ICON_MEHR_100), fparams=fparams, summary=L('Mehr (+ 100)'), tagline=tag)
	# weniger
	if int(offset) > 100:
		offset = max(int(offset)-100-max_count, 0)
		PLog(offset)
		title_org=py2_encode(title_org);
		fparams="&fparams={'title': '%s', 'offset': '%s'}" % (quote(title_org), offset)
		addDir(li=li, label=title_org, action="dirList", dirID="MyGalleries", fanart=R(ICON_WENIGER_100), 
			thumb=R(ICON_WENIGER_100), fparams=fparams, summary=L('Weniger (- 100)'), tagline=tag)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#------------------------------------------------------------------------------------------
# Bezeichnung in Flickr-API: Photosets
#	Mehrere Seiten - anders als MyGalleries
#	Flickr-Ausgabe im xml-Format.
# Workflow:
# 	MyAlbums -> MyAlbumsSingle -> BuildPath -> BuildPages -> SeparateVideos -> ShowPhotoObject
#
def MyAlbums(title, user_id, pagenr):
	PLog('MyAlbums:'); PLog('page: ' + str(pagenr))
	title_org = title							# title_org: Username
	
	path = BuildPath(method='flickr.photosets.getList', query_flickr='', user_id=user_id, pagenr=pagenr)
				
	page, msg = RequestUrl(CallerName='MyAlbums', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return 		
	PLog(page[:100])
		
	pages = stringextract('pages="', '"', page)		# im  Header, Anz. Seiten
	
	alben_max = stringextract('total="', '"', page)		# im  Header
	perpage = stringextract('perpage="', '"', page)		# im  Header
	thispagenr = stringextract('page="', '"', page)		# im  Header, sollte pagenr entsprechen
	PLog('Alben: %s, Seite: %s von %s, perpage: %s' % (alben_max, thispagenr, pages, perpage))
	
	name = '%s %s/%s' % (L('Seite'), pagenr, pages)	
	li = xbmcgui.ListItem()
	li = home(li, user_id=user_id)		# Home-Button
			
	if alben_max == '0':			
		msg1 = L('Keine Alben gefunden')
		MyDialog(msg1, '', '')
		return 
		
	records = blockextract('<photoset id', '', page)
	PLog('records: ' + str(len(records)))
	
	for rec in records:
		title 		= stringextract('<title>', '</title>', rec)
		photoset_id	= stringextract('id="', '"', rec)
		description = stringextract('description="', '"', rec)
		count_photos = stringextract('photos="', '"', rec)
		secret =  stringextract('secret=\"', '\"', rec) 
		serverid =  stringextract('server=\"', '\"', rec) 
		farmid =  stringextract('farm=\"', '\"', rec) 
		
		title=unescape(title); title=repl_json_chars(title)
					
		# Url-Format: https://www.flickr.com/services/api/misc.urls.html
		# thumb_src = 'https://farm%s.staticflickr.com/%s/%s_%s_z.jpg' % (farmid, serverid, photoset_id, secret)  # m=small (240)
		# Anforderung Url-Set in BuildPath -> BuildExtras
		thumb_src = stringextract('url_z="', '"', rec)	# z=640
		
		summ = "%s %s (%s)" % (count_photos, L('Fotos'), title_org)	# Anzahl stimmt nicht
		if description:
			summ = '%s | %s' % (summ, description)
		img_src = R(ICON_FLICKR)
		
		PLog('1Satz:')
		PLog(title);PLog(photoset_id);PLog(thumb_src);
		title=py2_encode(title); 
		fparams="&fparams={'title': '%s', 'photoset_id': '%s', 'user_id': '%s'}" % (quote(title), photoset_id, 
			user_id)
		addDir(li=li, label=title, action="dirList", dirID="MyAlbumsSingle", fanart=thumb_src, thumb=thumb_src, 
			fparams=fparams, summary=summ)
				
	# auf mehr prüfen:
	PLog(pagenr); PLog(pages);
	page_next = int(pagenr) + 1
	tag = 'total: %s %s, %s %s ' % (alben_max, L('Alben'), pages, L('Seiten'))
	title_org=py2_encode(title_org); 
	if page_next <= int(pages):
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_MEHR_1), thumb=R(ICON_MEHR_1), 
			fparams=fparams, summary=L('Mehr (+ 1)'), tagline=tag)
	if (page_next+10) < int(pages):
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_MEHR_10), thumb=R(ICON_MEHR_10), 
			fparams=fparams, summary=L('Mehr (+ 10)'), tagline=tag)
	if (page_next+100) < int(pages):
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_MEHR_100), thumb=R(ICON_MEHR_100), 
			fparams=fparams, summary=L('Mehr (+ 100)'), tagline=tag)
	# weniger
	page_next = int(pagenr) - 1
	if  page_next >= 1:
		page_next = page_next - 1
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_WENIGER_1), thumb=R(ICON_WENIGER_1), 
			fparams=fparams, summary=L('Weniger (- 1)'), tagline=tag)
	if page_next > 10:
		page_next = page_next - 10
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_WENIGER_10), thumb=R(ICON_WENIGER_10), 
			fparams=fparams, summary=L('Weniger (- 10)'), tagline=tag)
	if page_next > 100:
		page_next = page_next - 100
		fparams="&fparams={'title': '%s', 'user_id': '%s', 'pagenr': '%s'}" % (quote(title_org), user_id, int(page_next))
		addDir(li=li, label=title_org, action="dirList", dirID="MyAlbums", fanart=R(ICON_WENIGER_100), thumb=R(ICON_WENIGER_100), 
			fparams=fparams, summary=L('Weniger (- 100)'), tagline=tag)
							
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
#------------------------------------------------------------------------------------------
# Bezeichnung in Flickr-API: Photosets
#	Mehrere Seiten - anders als MyGalleries
#	Flickr-Ausgabe im xml-Format.
# Seitensteuerung durch BuildPages (-> SeparateVideos -> ShowPhotoObject, ShowVideos)
#
def MyAlbumsSingle(title, photoset_id, user_id, pagenr=1):
	PLog('MyAlbumsSingle:')
	
	mymethod = 'flickr.photosets.getPhotos'
	path = BuildPath(method=mymethod, query_flickr=mymethod, user_id=user_id, pagenr=1, 
		photoset_id=photoset_id) 

	page, msg = RequestUrl(CallerName='MyAlbumsSingle', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return	
	PLog(page[:100])
	pagemax		= stringextract('pages="', '"', page)
	perpage 	=  stringextract('perpage="', '"', page)	
	PLog(pagemax); PLog(perpage)					# flickr-Angabe stimmt nicht mit?
	
	records = blockextract('<photo id', '', page)	# ShowPhotoObject:  nur '<photo id'-Blöcke zulässig 	
	maxPageContent = SETTINGS.getSetting('maxPageContent')
	mypagemax = len(records) / int(maxPageContent)
	
	PLog('2Satz:')
	PLog('records: %s, maxPageContent: %s, mypagemax: %s' % (str(len(records)), maxPageContent, str(mypagemax)))
	# mypagemax = int(round(mypagemax + 0.49))		# zwangsw. aufrunden - entfällt
	# PLog('mypagemax: %s' % str(mypagemax))
	
	searchname = '#MyAlbumsSingle#'
	li = BuildPages(title=title, searchname=searchname, SEARCHPATH=path, pagemax=pagemax, perpage=perpage, 
		pagenr=1)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
	
####################################################################################################
# --------------------------
#  	FlickrPeople:  gesucht wird auf der Webseite mit dem Suchbegriff fuer Menue Flickr Nutzer.
#	Flickr liefert bei Fehlschlag den angemeldeten Nutzer zurück
# 	Exaktheit der Websuche nicht beeinflussbar.	
#
def FlickrPeople(pagenr=1):
	PLog('FlickrPeople: ' + str(SETTINGS.getSetting('FlickrPeople')))
	PLog('pagenr: ' + str(pagenr))
	pagenr = int(pagenr)
	
	if SETTINGS.getSetting('FlickrPeople'):
		username = SETTINGS.getSetting('FlickrPeople').replace(' ', '%20')		# Leerz. -> url-konform 
		path = 'https://www.flickr.com/search/people/?username=%s&page=%s' % (username, pagenr)
	else:
		msg1 = L('Einstellungen: Suchbegriff für Flickr Nutzer fehlt')
		MyDialog(msg1, '', '')
		return 			
	
	title2 = 'Flickr People ' + L('Seite') + ' ' +  str(pagenr)
	li = xbmcgui.ListItem()
	li = home(li, user_id='')				# Home-Button
				
	page, msg = RequestUrl(CallerName='FlickrPeople', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return 			
	PLog(page[:100])
	page = page.replace('\\', '')					# Pfadbehandl. im json-Bereich
	
	total = 0
	#  totalItems[2]  enthält die Anzahl. Falls page zu groß (keine weiteren 
	#	Ergebnisse), enthalten sie 0.
	try:
		totalItems =  re.findall(r'totalItems":(\d+)\}\]', page)  # Bsp. "totalItems":7}]
		PLog(totalItems)
		total = int(totalItems[0])
	except Exception as exception:
		PLog(str(exception))
	PLog("total: " + str(total))
	
	records = blockextract('_flickrModelRegistry":"search-contact-models"', 'flickrModelRegistry', page)
	PLog(len(records))
	
	thumb=R('icon-my.png')	
	i = 0					# loop count
	for rec in records:
		# PLog(rec)
		nsid =  stringextract('id":"', '"', rec) 
		if '@N' not in nsid:
				continue			
		username =  stringextract('username":"', '"', rec) 
		username=unescape(username);  username=unquote(username)
		realname =  stringextract('realname":"', '"', rec) 
		alias =  stringextract('pathAlias":"', '"', rec) 		# kann fehlen
		alias = unescape(alias);  alias = unquote(alias)
		
		if alias == '':
			alias = username
		iconfarm =  stringextract('iconfarm":"', '"', rec) 
		iconserver =  stringextract('iconserver":"', '"', rec) 
		followersCount =  stringextract('followersCount":', ',', rec) 
		if followersCount == '':
			followersCount  = '0'
		photosCount =  stringextract('photosCount":', ',', rec) 
		if photosCount == '':									# # photosCount kann fehlen
			photosCount  = '0'
		iconserver =  stringextract('iconserver":"', '"', rec) 
		title = "%s | %s" % (username, realname)
		PLog(title)
		title=unescape(title); title=unquote(title)
		summ = "%s: %s" % (L('Fotos'), photosCount)
		summ = summ + " | %s: %s | Alias: %s" % (L('Followers'), followersCount, alias)
		
		PLog('5Satz')
		PLog("username: %s, nsid: %s"	% (username, nsid)); PLog(title)
		if realname:
			label=realname
		else:
			label=username
		label=unescape(label); label=unquote(label)
		
		username=py2_encode(username);
		fparams="&fparams={'username': '%s', 'user_id': '%s'}" % (quote(username), nsid)
		addDir(li=li, label=label, action="dirList", dirID="MyMenu", fanart=thumb, thumb=thumb, 
		fparams=fparams, summary=summ)
		i = i + 1
			
	if i == 0: 
		msg = SETTINGS.getSetting('FlickrPeople') + ': ' + L('kein Treffer')
		PLog(msg)
		msg1=msg	
		MyDialog(msg1, '', '')
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		
	# plus/minus 1 Seite:
	PLog(pagenr * len(records)); PLog(total)
	if (pagenr * len(records)) < total:
		title =  'FlickrPeople ' + L('Seite') + ' ' +  str(pagenr+1)
		fparams="&fparams={'pagenr': '%s'}" % (pagenr+1)
		addDir(li=li, label=title, action="dirList", dirID="FlickrPeople", fanart=R(ICON_MEHR_1), 
			thumb=R(ICON_MEHR_1), fparams=fparams, summary=L('Mehr (+ 1)'))
	if 	pagenr > 1:	
		title =  'FlickrPeople ' + L('Seite') + ' ' +  str(pagenr-1)
		fparams="&fparams={'pagenr': '%s'}" % (pagenr-1)
		addDir(li=li, label=title, action="dirList", dirID="FlickrPeople", fanart=R(ICON_WENIGER_1), 
			thumb=R(ICON_WENIGER_1), fparams=fparams, summary=L('Weniger (- 1)'))
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

####################################################################################################
# für Gallerie-Liste ohne user_id kein API-Call verfügbar - Auswertung der Webseite (komb. html/json) 
# Keine Sortierung durch Flickr möglich - i.G. zu MyGalleries (sort_groups)
# 08.09.2019 Blockmerkmal geändert ('gallery-hunk clearfix -> 'class="tile-container">'
# Scrollmechnismus - nur ein Teil der Webinhalte verfügbar.
# 
def WebGalleries(pagenr):
	PLog('WebGalleries: pagenr=' + pagenr)
	if int(pagenr) < 1:
		pagenr = "1"
	path = GALLERY_PATH + 'page%s/' % (pagenr)		# Zusatz '?rb=1' nur in Watchdog erforderlich (302 Found)
	
	page, msg = RequestUrl(CallerName='WebGalleries: page %s' % pagenr, url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return			
	PLog(page[:50])
	
	# die enthaltenen Parameter page + perPage wirken sich verm. nicht auf die
	#	Seitenberechnung aus. Das Web zeigt jeweils 3 Vorschaubilder zu jeder Gallerie,
	#	nach 24 Galerien  erscheinen beim Scrolldown jeweils neue 24 Galerien.
	# 
	# Alternative ohne Bilder: Bereich "class="view pagination-view" enthält die 
	#	Links zu den einzelnen Seiten.
	totalItems 	= stringextract('totalItems":', '}', page) 		# Anzahl Galerien json-Bereich
	PageSize	= stringextract('viewPageSize":', ',', page)
	PLog(totalItems); PLog(PageSize);
	try:
		pages = float(totalItems) / float(PageSize)
		pagemax = int(math.ceil(pages))							# max. Seitenzahl, aufrunden für Seitenrest
	except Exception as exception:
		PLog(str(exception))
		pagemax  = 1
		msg1 = "WebGalleries: " + L('Ermittlung der Seitenzahl gescheitert')
		msg2 = "Gezeigt wird nur die erste Seite"
		MyDialog(msg1, '', '')
	
	PLog('pagemax: ' + str(pagemax)); 
	name = L('Seite') + ' ' + pagenr + L('von') + ' ' + str(pagemax)	
	li = xbmcgui.ListItem()
	li = home(li, user_id='')				# Home-Button
	
	records = blockextract('class="tile-container">', '', page)  # oder gallery-case gallery-case-user	
	if len(records) == 0: 
		msg1 = L("Keine Gallerien gefunden")
		MyDialog(msg1, '', '')
		return			
	PLog(len(records))
	for rec in records:					# Elemente pro Seite: 12
		# PLog(rec)   		# bei Bedarf
		href = BASE + stringextract('href="', '"', rec) 		# Bsp. https://www.flickr.com/photos/flickr/galleries/..
		try:
			href_id = href.split('/')[-2]
		except:
			href_id = ''
		img_src = img_via_id(href_id, page)
		gallery_id = href_id

		title = stringextract('gallery-title">', '</h4>', rec)  # in href
		title=py2_encode(title); 
		title=cleanhtml(title); title=mystrip(title);  
		title=unescape(title); title=repl_json_chars(title)
		
		nr_shown = stringextract('stat item-count">', '</span>', rec)		# Anzahl, Bsp.: 15 photos
		nr_shown = mystrip(nr_shown) 
		views 	= stringextract('stat view-count">', '</span>', rec)		# Views,  Bsp.: 3.3K views
		views = views.strip() 
		
		comments 	= stringextract('stat comment-count">', '</span>', rec)	# Views,  Bsp.: 17 comments
		comments = mystrip(comments) 
		summ = "%s | %s | %s" % (nr_shown, views, comments )
			
		PLog('6Satz:')	
		PLog(href);PLog(img_src);PLog(title);PLog(summ);PLog(gallery_id);
		title=py2_encode(title);
		fparams="&fparams={'title': '%s', 'gallery_id': '%s', 'user_id': '%s'}" % (quote(title), gallery_id, '')
		addDir(li=li, label=title, action="dirList", dirID="Gallery_single", fanart=img_src, thumb=img_src, 
			fparams=fparams, summary=summ)
				
	# auf mehr prüfen:
	PLog("pagenr: %s, pagemax: %s" % (pagenr, pagemax))
	pagenr = int(pagenr)
	if pagenr < pagemax:
		page_next = pagenr + 1			# Pfad-Offset + 1
		path = GALLERY_PATH + 'page%s/' % str(page_next)	
		PLog(path); 
		title = "%s, %s %s %s %s" % (L('Galerien'), L('Seite'), str(page_next), L('von'),  str(pagemax))
		fparams="&fparams={'pagenr': '%s'}" % str(page_next)
		addDir(li=li, label=title, action="dirList", dirID="WebGalleries", fanart=R(ICON_MEHR_1), 
			thumb=R(ICON_MEHR_1), fparams=fparams)
		
	# weniger
	if pagenr > 1:
		page_next = pagenr - 1			# Pfad-Offset - 1
		title = "%s, %s %s %s %s" % (L('Galerien'), L('Seite'), str(page_next), L('von'),  str(pagemax))
		fparams="&fparams={'pagenr': '%s'}" % str(page_next)
		addDir(li=li, label=title, action="dirList", dirID="WebGalleries", fanart=R(ICON_WENIGER_1), 
			thumb=R(ICON_WENIGER_1), fparams=fparams)
			
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
#---------------------------------------
# img_via_id: ermittelt im json-Teil (ARD-Neu) via href_id
def img_via_id(href_id, page):
	PLog("img_via_id: " + href_id)
	if href_id == '':
		img_src = R(ICON_FOLDER)
		return img_src								# Fallback bei fehlender href_id
	
	records = blockextract('"compoundId":', '', page)
	for rec in records:
		if href_id in rec:
			img_src = stringextract('"displayUrl":"', '"', rec)
			img_src = img_src.replace('\\', '')
			img_src = img_src.replace('_s', '')	# ..475efd8f73_s.jpg
			if img_src.startswith('https') == False:
				img_src = 'https:' + img_src
	if len(img_src) > 10:
		return 	img_src
	else:
		return R(ICON_FOLDER)		
      
#------------------------------------------------------------------------------------------
# Erzeugt Foto-Objekte für WebGalleries + MyGalleries (Pfade -> Rückgabe im xml-Format).
# Die Thumbnails von Flickr werden nicht gebraucht - erzeugt Plex selbst aus den Originalen
# max. Anzahl Fotos in Galerie: 50 (https://www.flickr.com/help/forum/en-us/72157646468539299/)
#	z.Z. keine Steuerung mehr / weniger nötig
def Gallery_single(title, gallery_id, user_id):		
	PLog('Gallery_single: ' + gallery_id)
		
	searchname = '#Gallery#'
	# pagenr hier weglassen - neu in BuildPages
	href = BuildPath(method='flickr.galleries.getPhotos', query_flickr='', user_id=user_id, pagenr='') 
	href = href + "&gallery_id=%s"  % (gallery_id)
	li = BuildPages(title=title, searchname=searchname, SEARCHPATH=href, pagemax='?', perpage=1, 
		pagenr='?')

	return li
		
####################################################################################################
# API-Format: https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=
#	24df437b03dd7bf070ba220aa717027e&text=Suchbegriff&page=3&format=rest
#	Rückgabeformat XML
# 
# Verwendet wird die freie Textsuche (s. API): Treffer möglich in Titel, Beschreibung + Tags
# Mehrere Suchbegriffe, getrennt durch Blanks, bewirken UND-Verknüpfung.
#
# 23.09.2020 Liste für letzte Suchbegriffe - hier ohne Rücksicht auf
#	das Suchergebnis
#
def Search(query='', user_id='', pagenr=1, title=''):
	PLog('Search: ' + query); 
	# wir springen direkt - Ablauf:
	#	Search -> Search_Work -> BuildPages (-> SeparateVideos -> ShowPhotoObject, ShowVideos)
	
	query_file 	= os.path.join("%s/search_terms") % ADDON_DATA
	
	if query == '':													# Liste letzte Sucheingaben
		query_recent = RLoad(query_file, abs_path=True)
		if query_recent.strip():
			head = L('Suche')
			search_list = [head]
			query_recent= query_recent.strip().splitlines()
			query_recent=sorted(query_recent, key=str.lower)
			search_list = search_list + query_recent
			title = L('Suche') + ': ' +  L('im oeffentlichen Inhalt')
			ret = xbmcgui.Dialog().select(title, search_list, preselect=0)	
			PLog(ret)
			if ret == -1:
				PLog("Liste Sucheingabe abgebrochen")
				return Main()
			elif ret == 0:
				query = ''
			else:
				query = search_list[ret]

	if  query == '':
		query = get_keyboard_input()	# Modul util
		if  query == None or query.strip() == '':
			return ""	
	query = query.strip(); query_org = query
	
	# wg. fehlender Rückgabewerte speichern wir ohne Rücksicht
	#	auf das Suchergebnis: 
	if query:															# leere Eingabe vermeiden
		query_recent= RLoad(query_file, abs_path=True)					# Sucheingabe speichern
		query_recent= query_recent.strip().splitlines()
		if len(query_recent) >= 24:										# 1. Eintrag löschen (ältester)
			del query_recent[0]
		query_org=py2_encode(query_org)										# unquoted speichern
		if query_org not in query_recent:
			query_recent.append(query_org)
			query_recent = "\n".join(query_recent)
			query_recent = py2_encode(query_recent)
			RSave(query_file, query_recent)								# withcodec: code-error	

	Search_Work(query=py2_encode(query), user_id=user_id)
			 
	return
	
# --------------------------	
# Search_Work: ermöglicht die Flickr-Suchfunktion außerhalb der normalen Suchfunktion, z.B.
#	Photostream + Faves. Die normale Suchfunktion startet in Search, alle anderen hier.
# Ablauf: 
#	Search_Work -> Seitensteuerung durch BuildPages (-> SeparateVideos -> ShowPhotoObject, ShowVideos)
#
# query='#Suchbegriff#' möglich (MyMenu: MyPhotostream, MyFaves) - Behandl. in BuildPath
#	10.04.2020 wg. coding-Problemen geändert in '&Suchbegriff&'
#  query='None' möglich (Photostream)
#
# URL's: viele Foto-Sets enthalten unterschiedliche Größen - erster Ansatz, Anforderung mit b=groß, 
#	schlug häufig fehl. Daher Anforderung mit einer Suffix-Liste (extras), siehe 
#	https://www.flickr.com/services/api/misc.urls.html, und Entnahme der "größten" URL. 
# 
def Search_Work(query, user_id, SEARCHPATH=''):		
	PLog('Search_Work: ' + query); 		
	
	query_flickr = quote(query)
	if query == '&Faves&':							# MyFaves
		SEARCHPATH = BuildPath(method='flickr.favorites.getList', query_flickr=query_flickr, user_id=user_id, pagenr='')
	else:
		# BuildPath liefert zusätzlich Dict['extras_list'] für Fotoauswahl (s.u.)
		SEARCHPATH = BuildPath(method='flickr.photos.search', query_flickr=query_flickr, user_id=user_id, pagenr='')
	PLog(SEARCHPATH)
				  	
	if query == 'None':								# von Photostream
		searchname = L('Seite')
		title='Photostream'		
	else:
		searchname = L('Suche') + ': ' + query + ' ' + L('Seite')
		title=query
	if query.startswith('&') and query.endswith('&'):# von MyPhotostream / MyFaves
		title = query.replace('&', '')
		searchname =  L('Seite')					# Ergänzung in BuildPages
	PLog(title)					
	BuildPages(title=title, searchname=searchname, SEARCHPATH=SEARCHPATH, pagemax=1, perpage=1, pagenr='?')
		
	return
	
#---------------------------------------------------------------- 
# Ausgabesteuerung für Fotoseiten: Buttons für die einzelnen Seiten, einschl. Mehr/Weniger.
#	Falls nur 1 Seite vorliegt, wird SeparateVideos direkt angesteuert.
# Auslagerung ShowPhotoObject für PHT erforderlich (verträgt keine Steuer-Buttons) 
# searchname steuert Belegung von title2 des ObjectContainers - Einfassung
#	 durch ## kennzeichnet: keine Suche
# perpage setzen wir wg. des PHT-Problems nicht bei der Fotoausgabe einer einzelnen 
#	Seite um - Flickr-Default hier 100 (dto. bei Suche).
# Bei Überschreitung der Seitenzahl (page) zeigt Flickr die letzte verfügbare Seite.
# Die Seitenberechnung stimmt bei Flickr nur dann, wenn bei max. Bildgröße 
#	"Originalbild" gewählt ist. Bei kleineren Größen rechnet Flickr die weggefallenen
#	Seiten nicht heraus - dann zeigt das Addon wieder die erste Seite, obwohl laut
#	noch weitere Seiten existieren. 
def BuildPages(title, searchname, SEARCHPATH, pagemax=1, perpage=1, pagenr=1,  photototal=1):
	PLog('BuildPages:')
	PLog('SEARCHPATH: %s' % (SEARCHPATH))
	PLog(pagenr); PLog(title)
	title_org = title
	
	if pagenr == '?' or pagenr == '':							# Inhalt noch unbekannt
		page, msg = RequestUrl(CallerName='BuildPages', url=SEARCHPATH)
		if page == '': 
			msg1=msg			
			MyDialog(msg1, '', '')
			return
		PLog(page[:100])
		if  '<rsp stat="ok">' not in page or 'pages="0"' in page:			
			msg1 = L('kein Treffer')
			MyDialog(msg1, '', '')
			return

		pagemax		= stringextract('pages="', '"', page)
		photototal 	=  stringextract('total="', '"', page)		# z.Z. n.b.
		perpage 	=  stringextract('perpage="', '"', page)	# Flickr default: 100 pro Seite
		pagenr 		= 1											# Start mit Seite 
		
	PLog('Flickr: pagemax %s, total %s, perpage %s' % (pagemax, photototal, perpage))
	
	pagenr = int(pagenr); pagemax = int(pagemax); 			
	maxPageContent = 500										# Maximum Flickr	
	if SETTINGS.getSetting('maxPageContent'):					# Objekte pro Seite (Einstellungen)
		maxPageContent = int(SETTINGS.getSetting('maxPageContent'))
	if pagenr < 1:
		pagenr = 1
	pagenr = min(pagenr, pagemax)
	PLog("Plugin: pagenr %d, maxPageContent %d, pagemax %d" % (pagenr, maxPageContent, pagemax))

	# user_id ermitteln für home (PHT-Problem)
	# Pfade ohne user_id möglich (z.B. Suche + Photostream  aus Main)
	try:
		user_id = re.search(u'user_id=(\d+)@N0(\d+)', SEARCHPATH).group(0)		#user_id=66956608@N06
		user_id = user_id.split('=')[1]
	except Exception as exception:
		PLog(str(exception))
		user_id = ''
		
	# keine Suche - Bsp.  = '#Gallery#'	
	if searchname.startswith('#') and searchname.endswith('#'):	
		searchname = searchname.replace('#', '')
		title_org = searchname		# Titel für ShowPhotoObject
		searchname =  L('Seite')
	
	name = '%s %s/%s' % (searchname, pagenr, pagemax)	

	
	pagemax = int(pagemax)
	if pagemax == 1:						# nur 1 Seite -> SeparateVideos direkt
		title = title + ' %s'  % 1			# Bsp. "scott wilson Seite 1"
		PLog('pagemax=1, jump to SeparateVideos')
		li = SeparateVideos(title=title, path=SEARCHPATH, title_org=title_org)
		return li 
			
	li = xbmcgui.ListItem()
	li = home(li, user_id=user_id)			# Home-Button
	
	for i in range(pagemax):
		title = L('Seite') + ': ' + str(pagenr)	
		# Anpassung SEARCHPATH an pagenr 
		path1 = SEARCHPATH.split('&page=')[0]	# vor + nach page trennen	
		path2 = SEARCHPATH.split('&page=')[1]
		pos = path2.find('&')					# akt. pagenr abschneiden
		path2 = path2[pos:]
		path = path1 + '&page=%s' %  str(pagenr) + path2 # Teil1 + Teil2 wieder verbinden
		path = path + '&per_page=%s' %  str(maxPageContent)
		
		PLog('3Satz:')
		PLog("i %d, pagenr %d" % (i, pagenr))
		PLog(path);  # PLog(path1); PLog(path2);
		# SeparateVideos -> ShowPhotoObject, ShowVideos:
		
		title=py2_encode(title); path=py2_encode(path);
		title_org=py2_encode(title_org); 		
		fparams="&fparams={'title': '%s', 'path': '%s', 'title_org': '%s'}" % (quote(title), 
			quote(path), quote(title_org))
		addDir(li=li, label=title, action="dirList", dirID="SeparateVideos", fanart=R('icon-next.png'), 
			thumb=R('icon-next.png'), fparams=fparams)
			
		pagenr = pagenr + 1 
		if i >= maxPageContent-1:				# Limit Objekte pro Seite
			break			
		if pagenr >= pagemax+1:					# Limit Plugin-Seiten gesamt
			break	
			
	# auf mehr prüfen:	
	# Begrenzung max/min s.o.
	PLog('Mehr:')
	PLog(pagenr); PLog(pagemax); PLog(maxPageContent);
	tag = 'total: %s ' % pagemax + L('Seiten')
	title_org=py2_encode(title_org); searchname=py2_encode(searchname); SEARCHPATH=py2_encode(SEARCHPATH)		
	if pagenr  <= pagemax:
		pagenr_next = pagenr
		title = L('Mehr (+ 1)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_MEHR_1), thumb=R(ICON_MEHR_1), 
			fparams=fparams)
	if pagenr + (9 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (10 * maxPageContent)
		title = L('Mehr (+ 10)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_MEHR_10), thumb=R(ICON_MEHR_10), 
			fparams=fparams)
	if pagenr + (99 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (100 * maxPageContent)
		title = L('Mehr (+ 100)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_MEHR_100), thumb=R(ICON_MEHR_100), 
			fparams=fparams)
	if pagenr + (499 * maxPageContent) <= pagemax:
		pagenr_next = pagenr + (500 * maxPageContent)
		title = L('Mehr (+ 500)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_MEHR_500), thumb=R(ICON_MEHR_500), 
			fparams=fparams)
	# weniger
	if  pagenr-1 > maxPageContent:			# maxPageContent = 1 Seite
		pagenr_next = pagenr - ( 2* maxPageContent)
		title = L('Weniger (- 1)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_WENIGER_1), thumb=R(ICON_WENIGER_1), 
			fparams=fparams)
	if  pagenr-1 > (10 * maxPageContent):
		pagenr_next = pagenr - (10 * maxPageContent)
		title = L('Weniger (- 10)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_WENIGER_10), thumb=R(ICON_WENIGER_10), 
			fparams=fparams)
	if  pagenr-1 > 100:
		pagenr_next =  pagenr - (100 * maxPageContent)
		title = L('Weniger (- 100)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_WENIGER_100), thumb=R(ICON_WENIGER_100), 
			fparams=fparams)
	if  pagenr-1 > 500:
		pagenr_next =  pagenr - (500 * maxPageContent)
		title = L('Weniger (- 500)')
		fparams="&fparams={'title': '%s', 'searchname': '%s', 'SEARCHPATH': '%s', 'pagemax': '%s', 'pagenr': '%s'}" %\
			(quote(title_org), quote(searchname), quote(SEARCHPATH), pagemax, pagenr_next)
		addDir(li=li, label=title_org, action="dirList", dirID="BuildPages", fanart=R(ICON_WENIGER_500), thumb=R(ICON_WENIGER_500), 
			fparams=fparams)
				
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------- 
#	SeparateVideos: Aufruf durch BuildPages falls SETTINGS.getSetting('showVideos') gewählt
#	- 2 Buttons,  falls die Seite  (path)  sowohl Videos als auch Fotos enthält.
#		andernfalls wird direkt zu ShowPhotoObject oder ShowVideos verzweigt
#		(Seite wird aus dem Cache erneut geladen)
#	- user_id,username,realname werden hier ermittelt + übergeben
def SeparateVideos(title, path, title_org):
	PLog('SeparateVideos: ' + path)

	li = xbmcgui.ListItem()
	page, msg = RequestUrl(CallerName='SeparateVideos', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
	PLog(page[:100])								# Ergebnis im XML-Format, hier in strings verarbeitet

	# Rückwärtssuche: user_id -> username + realname 
	#	1. user_id aus path ermitteln, 2.  Aufruf flickr.people.getInfo
	#	nur falls user_id bekannt - nicht bei den Publics (müsste via nsid bei
	#		jedem Satz ermittelt werden - zu zeitaufwendig bei 100 Sätzen)
	# 	Pfade ohne user_id möglich (z.B. Suche + Photostream  aus Main)
	try:
		user_id = re.search(u'user_id=(\d+)@N0(\d+)', path).group(0)		#user_id=66956608@N06
		user_id = user_id.split('=')[1]
	except Exception as exception:
		PLog(str(exception))							
		user_id = ''

	username=''; realname=''; 
	if user_id and ('None' not in user_id):	 # 'None' = PHT-Dummy
		user_id,nsid,username,realname = GetUserID(user_id)		# User-Profil laden
	PLog('user_id %s, username %s, realname %s'	% (user_id,username,realname))
	
	if SETTINGS.getSetting('showVideos') == 'false':						#	keine Videos zeigen
		ShowPhotoObject(title,path,user_id,username,realname,title_org)	#	direkt
		return 


	if 'media="video"' in page and 'media="photo"' in page:	# Auswahlbuttons für Fotos + Videos zeigen
		# title von BuildPages
		title=py2_encode(title); path=py2_encode(path); username=py2_encode(username); 
		realname=py2_encode(realname); title_org=py2_encode(title_org); 
		fparams="&fparams={'title': '%s', 'path': '%s', 'user_id': '%s', 'username': '%s', 'realname': '%s', 'title_org': '%s'}" %\
			(quote(title), quote(path), user_id, quote(username), quote(realname), quote(title_org))
		addDir(li=li, label=title, action="dirList", dirID="ShowPhotoObject", fanart=R('icon-photo.png'), 
			thumb=R('icon-photo.png'), fparams=fparams)
			
		title = L("zeige Videos")
		fparams="&fparams={'title': '%s', 'path': '%s', 'user_id': '%s', 'username': '%s', 'realname': '%s'}" %\
			(quote(title), quote(path), user_id, quote(username), quote(realname))
		addDir(li=li, label=title, action="dirList", dirID="ShowVideos", fanart=R('icon-video.png'), 
			thumb=R('icon-video.png'), fparams=fparams)
	else:
		if 'media="video"' in page:				# nur Videos
			ShowVideos(title,path,user_id,username,realname)  	# 	direkt			
		else:									# nur Fotos
			ShowPhotoObject(title,path,user_id,username,realname,title_org)  # 	direkt
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------- 
#	Aufrufer: BuildPages -> SeparateVideos
#	path muss die passende pagenr enthalten
#	
#	Anders als beim Photo-Objekt in Plex werden die Bilder hier 
#		in SLIDESTORE gespeichert und als Listitem gelistet
#		(Button -> Einzelbild). 
#		Ein abschließender Button ruft die Slideshow auf (Kodi-
#		Player).
#
# Überwachung Speicherplatz: 	CheckStorage - s.u.
# eindeutiger Verz.-Namen: 		path2dirname - s.u.
#
# Hinw.: bei wiederholten Aufrufen einer Quelle sammeln sich im Slide-Verz.
#	mehr Bilder als bei Flickr (insbes. Photostream wird häufig aktualisiert) -
#	es erfolgt kein Abgleich durch das Addon. Alle Bilder in einem Verz.
#	verbleiben bis zum Löschen durch CheckStorage oder CleanUp.
#
def ShowPhotoObject(title,path,user_id,username,realname,title_org):
	PLog('ShowPhotoObject:')
	PLog(title); PLog(title_org)
		
	page, msg = RequestUrl(CallerName='ShowPhotoObject', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
	PLog(page[:100])								# Ergebnis im XML-Format, hier in strings verarbeitet
	pagenr		= stringextract('page="', '"', page)	
		
	li = xbmcgui.ListItem()
	li = home(li,  user_id=user_id, username=username)			# Home-Button

	records = blockextract('<photo id', '', page)	# ShowPhotoObject:  nur '<photo id'-Blöcke zulässig 	
	PLog('records: %s' % str(len(records)))
	extras_list = Dict('load', 'extras_list')
	try:									# Back in Browser: ValueError: list.remove(x)
		extras_list.remove('media')			# 1. Eintrag media enthält keinen URL
	except:
		pass
	PLog("extras_list: " + str(extras_list));  	# Größen s. BuildExtras
		
	CheckStorage(SLIDESTORE, SETTINGS.getSetting('max_slide_store'))	# Limit checken
		
	title = path2dirname(title, path, title_org)	# Verz.-Namen erzeugen
	fname = make_filenames(py2_decode(title))		# os-konforme Behandl. 
	PLog(fname);
	fpath = '%s/%s' % (SLIDESTORE, fname)
	PLog(fpath)
	if os.path.isdir(fpath) == False:
		try:  
			os.mkdir(fpath)
		except OSError:  
			msg1 = L('Bildverzeichnis im SLIDESTORE konnte nicht erzeugt werden:')
			msg2 = fname
			msg3 = "SLIDESTORE: %s" % (SLIDESTORE)
			PLog(msg1); PLog(msg2); PLog(msg3)
			MyDialog(msg1, msg2, msg3)
			return li	
		
	image = 0
	for s in records:
		if 'media="video"' in s:
			continue								
		pid =  stringextract('photo id=\"', '\"', s) 	# photo id auch bei Videos
		owner =  stringextract('owner=\"', '\"', s) 	
		secret =  stringextract('secret=\"', '\"', s) 
		serverid =  stringextract('server=\"', '\"', s) 
		farmid =  stringextract('farm=\"', '\"', s) 		
		descr =  stringextract('title=\"', '\"', s)		# Zusatz zu Bild 001 
		descr = unescape(descr)							
		
		if 	username:						# Ersatz owner durch username + realname	
			owner = username
			if realname:
				owner = "%s | %s" % (owner, realname)
		
		# Url-Format: https://www.flickr.com/services/api/misc.urls.html
		thumb_src = 'https://farm%s.staticflickr.com/%s/%s_%s_m.jpg' % (farmid, serverid, pid, secret)  # m=small (240)
		# Foto-Auswahl - jeweils das größte, je nach Voreinstellung (falls verfügbar):
		Imagesize = L('Bildgroesse') 
		Imagesize = py2_decode(Imagesize)
		if 'url_' in s:							# Favs ohne Url
			for i in range (len(extras_list)):			
				url_extra = extras_list[i]
				img_src = stringextract('%s=\"' % (url_extra), '\"', s) 
				suffix = url_extra[-2:] 		# z.B. _o von url_o, zusätzlich height + width ermitteln
				width = stringextract('width%s=\"' % (suffix), '\"', s)	  	# z.B. width_o
				height = stringextract('height%s=\"' % (suffix), '\"', s)  	# z.B. height_o
				# PLog(url_extra); PLog(img_src);PLog(suffix);PLog(width);PLog(height);	# bei Bedarf
				if len(img_src) > 0:		# falls Format nicht vorhanden, weiter mit den kleineren Formaten
					PLog("url_extra: " + url_extra)
					break
			summ = owner + ' | ' + '%s: %s x %s' % (Imagesize, width, height)
		else:									# Favs-Url wie thumb_src ohne extra (m)
			img_src = 'https://farm%s.staticflickr.com/%s/%s_%s.jpg' % (farmid, serverid, pid, secret)
			summ = owner 						# falls ohne Größenangabe
		
		# für Originalbilder in Alben zusätzl. getSizes-Call erforderlich:	
		PLog('Mark0')
		if "photosets.getPhotos" in path:		# Output ohne Url-Liste für Größen
			if SETTINGS.getSetting('max_width') == "Originalbild":
				PLog('try_info_call:')
				API_KEY = GetKey()	
				p1 = "https://www.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=%s" % API_KEY
				p2 = "&photo_id=%s&format=rest" % (pid)
				info_url = p1 + p2
				page, msg = RequestUrl(CallerName='ShowPhotoObject2', url=info_url)
				if page:
					sizes = blockextract('<size label', '', page)
					source=''
					for size in sizes:
						if '"Original"' in size:
							width = stringextract('width="', '"', s)	  	# z.B. "1600"
							height = stringextract('height="', '"', s)	  	# z.B. "1200"
							source = stringextract('source="', '"', s)
							break
						else:	# Original kann fehlen, letzte Zeile auswerten (aufsteigend sort.)
							width = stringextract('width="', '"', sizes[-1])	  	# z.B. "3968"
							height = stringextract('height="', '"', sizes[-1])	  	# z.B. "2907"
							source = stringextract('source="', '"', sizes[-1])
							
					if source:
						img_src = source
						summ = owner + ' | ' + '%s: %s x %s' % (Imagesize, width, height)							
			
		PLog(descr); PLog(img_src); # PLog(thumb_src);	PLog(pid);PLog(owner);	# bei Bedarf
		
		if img_src == '':									# Sicherung			
			msg1 = 'Problem in Bildgalerie: Bild nicht gefunden'
			PLog(msg1)
	
		if img_src:
			#  Kodi braucht Endung für SildeShow; akzeptiert auch Endungen, die 
			#	nicht zum Imageformat passen
			pic_name 	= 'Bild_%04d_%s.jpg' % (image+1, pid)		# Name: Bild + Nr + pid
			local_path 	= "%s/%s" % (fpath, pic_name)
			PLog("local_path: " + local_path)
			title = "Bild %03d | %s" % (image+1, descr)
			PLog("Bildtitel: " + title)
			
			thumb = img_src									# Default: Bild = Url 
			local_path = os.path.abspath(local_path)
			if os.path.isfile(local_path) == False:			# nicht lokal vorhanden - get & store
				# 03.10.2019 urlretrieve in Schleife bremst sehr stark - daher Ausführung im Hintergrund
				#try:
					#urllib.urlretrieve(img_src, local_path)
				background_thread = Thread(target=thread_getpic, args=(img_src, local_path))
				background_thread.start()
				thumb = local_path
				#except Exception as exception:
				#	PLog(str(exception))	
			else:											
				thumb = local_path							# lokal vorhanden - load
				thumb_src = thumb							# Verzicht auf thumbnail von Farm			
			
			tagline = unescape(title_org); tagline = cleanhtml(tagline)
			summ = unescape(summ)
			PLog('neu:');PLog(title);PLog(thumb);PLog(thumb_src);PLog(summ); PLog(local_path);
			
			if thumb:
				# via addDir ist keine Steuerung mittels Cursortasten im Listing möglich.
				#	Daher verwenden wir für jedes Bild ein eigenes Listitem. 
				#fparams="&fparams={'path': '%s', 'single': 'True'}" % urllib2.quote(local_path)
				#addDir(li=li, label=title, action="dirList", dirID="SlideShow", 
				#	fanart=thumb, thumb=thumb, fparams=fparams, summary=summ, tagline=tagline)

				image += 1
				PLog("thumb_src: " + thumb_src)

				li = xbmcgui.ListItem()
				li.setLabel(title)			
				# 11.04.2020 setThumbnailImage ersetzt durch setArt
				li.setArt({'thumb':thumb_src, 'icon':thumb_src})		# lokal oder Farm
				
				li.setInfo(type='image', infoLabels={'Title': title}) 	# plot bei image nicht möglich
				xbmcplugin.addDirectoryItem(
					handle=HANDLE,
					url=thumb,								# lokal oder Farm
					listitem=li,
					isFolder=False
				)
			
	# Button SlideShow - auch via Kontextmenü am Bild	
	if image > 0:
		fpath=py2_encode(fpath);
		fparams="&fparams={'path': '%s'}" % quote(fpath) 	# fpath: SLIDESTORE/fname
		addDir(li=li, label="SlideShow", action="dirList", dirID="SlideShow", 
			fanart=R('icon-stream.png'), thumb=R('icon-stream.png'), fparams=fparams)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)  # ohne Cache, um Neuladen zu verhindern

#----------------------------------------------------------------
def thread_getpic(img_src, local_path):
	PLog("thread_getpic:")
	PLog(img_src); PLog(local_path);

	try:
		urlretrieve(img_src, local_path)
	except Exception as exception:
		PLog("thread_getpic:" + str(exception))

	return
#----------------------------------------------------------------
# Aufruf  ShowPhotoObject
#	erzeugt eindeutigen Verz.-Namen aus title_org, Titel + Pfad, Bsp.:
# 	  	show_photos_158655533 			Photostream 1-seitig, vorgewählter User
#		show_photos_72157708806994797	Photostream 1-seitig, anderer User
#		Photostream_Page-_1				Photostream allgmein, Seite 1
#		Photostream_show_photos_158655 	Photostream mehrseitig, vorgewählter User
#		Photostream_show_photos_1		Photostream mehrseitig, Seite mit Video(s),
#											Aufruf durch SeparateVideos

def path2dirname(title, path, title_org):
	PLog('path2dirname: ' + path)
	PLog(title); PLog(title_org); 
	
	dirname=''; dir_id=''
	if 'id=' in path:						#  photoset_id, gallery_id
		try:
			dir_id = re.search('id=(\d+)',path).group(1)
		except Exception as exception:
			PLog(str(exception))	
			dir_id=''
	
	pagenr=''
	if title.startswith('Page') == False:			# Zusatz pagenr, falls nicht im Titel
		if '&page=' in path:
			try:
				pagenr = re.search('&page=(\d+)', path).group(1)
			except Exception as exception:			# nr kann fehlen (..&text=&..)
				PLog(str(exception))	
				pagenr=''		
	
	dirname = "%s_%s" % (title_org, title)			# title_org: Photostream o.ä.
	if dir_id:
		dirname = "%s_%s" % (dirname, dir_id)
	if pagenr:
		dirname = "%s_%s" % (dirname, pagenr)
	PLog(dirname)	
	
	return dirname
#---------------------------------------------------------------- 
#  Darstellung der in SLIDESTORE gespeicherten Bilder.
#		single=None -> Einzelbild
#		single=True -> SlideShow
#
#  ClearUp in SLIDESTORE s. Modulkopf
#  
def SlideShow(path, single=None):
	PLog('SlideShow: ' + path)
	local_path = os.path.abspath(path)
	if single:							# Einzelbild	
		return xbmc.executebuiltin('ShowPicture(%s)' % local_path)
	else:
		PLog(local_path)
		return xbmc.executebuiltin('SlideShow(%s, %s)' % (local_path, 'notrandom'))
#---------------------------------------------------------------- 
# Rückgabe path: xml-Format
def ShowVideos(title,path,user_id,username,realname):
	PLog('ShowVideos:')
	# PLog(path)
	
	page, msg = RequestUrl(CallerName='ShowVideos', url=path)
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return 			
	PLog(page[:100])								# Ergebnis im XML-Format, hier in strings verarbeitet
	
	li = xbmcgui.ListItem()
	li = home(li, user_id=user_id, username=username)		# Home-Button
	
	records = blockextract('<photo id', '', page)	 	
	PLog('records: %s' % str(len(records)))
	i=0
	for s in records:						
		if 'media="video"' not in s:			# Sicherung (sollte hier nicht vorkommen)
			continue
		i=i+1		
		pid 	=	stringextract('id=\"', '\"', s) 
		owner 	=  	stringextract('owner=\"', '\"', s) 	
		secret	=  	stringextract('secret=\"', '\"', s) 
		serverid =  stringextract('server=\"', '\"', s) 
		farmid 	=  	stringextract('farm=\"', '\"', s) 		
		title 	=  	stringextract('title=\"', '\"', s)	
		url 	= 	'https://www.flickr.com/video_download.gne?id=%s' % pid
		
		# gewünschte Bildgröße hier nicht relevant, z=kleinste reicht für Video-Thumb
		img_src 	=  	stringextract('url_z="', '"', s)	
		
		title = unescape(title)					# Web Client hat Probleme mit ausländ. Zeichen
		if title == '':
			title = "Video %s" % str(i)
		else:
			"Video %s| %s" % (str(i), title)
		summ  = owner
			
		PLog('4Satz:')
		PLog(title); PLog(pid); PLog(img_src); PLog(url);
		url=py2_encode(url); title=py2_encode(title); img_src=py2_encode(img_src); summ=py2_encode(summ); 	
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sub_path': '', 'Merk': ''}" %\
			(quote(url), quote(title), quote(img_src), quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="PlayVideo", fanart=img_src, thumb=img_src, fparams=fparams, 
			summary=summ) 		

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)

#---------------------------------------------------------------- 
#  method: Flickr-API-Methode
#  pagenr muss Aufrufer beisteuern
def BuildPath(method, query_flickr, user_id, pagenr, photoset_id=''):
	PLog('BuildPath: %s' % method)
	PLog(user_id); 
	query_flickr = unquote(query_flickr)
	PLog(query_flickr);
	
	API_KEY = GetKey()							# flickr_keys.txt
	PATH = "https://api.flickr.com/services/rest/?method=%s&api_key=%s"  % (method, API_KEY)	

	if user_id:									# None bei allg. Suche
		if 'None' not in user_id:				# PHT-Dummy
			# user_id = Dict('load', 'nsid')	# beliebige user_id aus FlickrPeople
			PATH =  PATH + "&user_id=%s" % (user_id)
		
	# Suchstring + Extras anfügen für Fotoabgleich - 
	#	s. https://www.flickr.com/services/api/flickr.photos.search.html
	if 'photos.search' in method or 'favorites.getList' in method or 'photosets' in method or 'galleries.getPhotos'  in method:
		extras  = BuildExtras()					# einschl. Dict['extras_list'] für Fotoabgleich 
		if query_flickr.startswith('&') and query_flickr.endswith('&'):		# von MyPhotostream / MyFaves
			query_flickr = ''												# alle listen
		if 'photosets.getList' in method:									# primary_photo_extras statt extras
			PATH =  PATH + "&text=%s&page=%s&primary_photo_extras=%s&format=rest" % (query_flickr, pagenr, extras)
		if 'photosets.getPhotos' in method:									# primary_photo_extras statt extras
			PATH =  PATH + "&photoset_id=%s&page=%s&primary_photo_extras=%s&format=rest" % (photoset_id, pagenr, extras)
		else:
			query_flickr = quote(query_flickr)
			PATH =  PATH + "&text=%s&page=%s&extras=%s&format=rest" % (query_flickr, pagenr, extras)
			
	if SETTINGS.getSetting('sort_order'):					# Bsp. 1 / date-posted-desc
		val = SETTINGS.getSetting('sort_order')
		nr = val.split('/')[0].strip	
		sortorder = val.split('/')[1].strip()
		PLog(type(PATH));PLog(type(sortorder));
		PATH = '%s&sort=%s' % (PATH, py2_encode(sortorder))	
				
	if pagenr:
		PATH =  PATH + "&page=%s" % pagenr
	
	# per_page muss an letzter Stelle stehen (Änderung in BuildPages möglich)
	if SETTINGS.getSetting('maxPageContent'):					# Objekte pro Seite
		mPC = py2_encode(SETTINGS.getSetting('maxPageContent'))
		PATH =  PATH + "&per_page=%s" % mPC
	else:
		PATH =  PATH + "&per_page=%s" % 500		# API: Maximum
	PLog(PATH) 
	return PATH    
#----------------------------------------------------------------  
def GetKey():
	API_KEY 	= RLoad('flickr_keys.txt')
	API_KEY		= API_KEY.strip()
	PLog('flickr_keys.txt geladen')	
	return API_KEY
#----------------------------------------------------------------  
# Aufruf: MyMenu
# 3 Methoden: Suche nach user_id, Email, Username
def GetUserID(user):
	PLog('GetUserID:'); PLog(str(user))
	
	API_KEY = GetKey()	
	if '@' in user:
		if '@N' in user:	# user_id (nsid)
			nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.getInfo'
			nsid_url = nsid_url + '&user_id=%s' % user
		else:				# Email
			nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.findByEmail'
			nsid_url = nsid_url + '&find_email=%s' % user
		url = nsid_url + '&api_key=%s' 	% API_KEY
	else:
		nsid_url = 'https://api.flickr.com/services/rest/?method=flickr.people.findByUsername'
		url = nsid_url + '&api_key=%s&username=%s' 	% (API_KEY, user)		
	page, msg = RequestUrl(CallerName='MyMenu: get nsid', url=url)
	PLog(page[:100])
	if page == '': 
		msg1 = msg
		MyDialog(msg1, '', '')
		return
		
	if 'User not found'	in page:								# Flickr err code
		user_id = 'User not found'
	else:
		user_id		= stringextract('id="', '"', page)			# user_id / nsid i.d.R. identisch
	nsid 		= stringextract('nsid="', '"', page)
	username 	= stringextract('<username>', '</username>', page)
	realname 	= stringextract('<realname>', '</realname>', page)
	#	Dict['user_id'] = user_id								# Dicts nur für Flickr user (s. Mymenu)
	return user_id,nsid,username,realname
	
#----------------------------------------------------------------  
def BuildExtras():		# Url-Parameter für Bildgrößen - abh. von Einstellungen
	# URL-Anforderung, sortiert von groß nach klein - Default
	# media: Ausgabe photo oder video
	extras = "media,url_o,url_k,url_h,url_l,url_c,url_z"	
	# Breiten: o = Original, k=2048, h=1600, l=1024, c=800, z=640
	pref_max_width = SETTINGS.getSetting('max_width')
	# pref_max_width = 1600		# Test
	if pref_max_width == "Originalbild":
		extras = "media,url_o,url_k,url_h,url_l,url_c,url_z"
	if pref_max_width == "2048":
		extras = "media,url_k,url_h,url_l,url_c,url_z"
	if pref_max_width == "1600":
		extras = "media,url_h,url_l,url_c,url_z"
	if pref_max_width == "1024":
		extras = "media,url_l,url_c,url_z"	
	if pref_max_width == "800":
		extras = "media,url_c,url_z"
	if pref_max_width == "640":
		extras = "media,url_z"
	
	PLog(pref_max_width); PLog(extras)
	extras_list = extras.split(",")						# Für Foto-Auswahl in Suchergebnis
	Dict('store', 'extras_list', extras_list)
	
	return extras
	
####################################################################################################
def SearchUpdate(title):		
	PLog('SearchUpdate:')
	li = xbmcgui.ListItem()

	ret = updater.update_available(VERSION)	
	#PLog(ret)
	if ret[0] == False:		
		msg1 = 'Updater: Github-Problem'
		msg2 = 'update_available: False'
		PLog("%s | %s" % (msg1, msg2))
		MyDialog(msg1, msg2, '')
		return li			

	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1
	summ = ret[3]			# Changes
	tag = ret[4]			# tag, Bsp. 029
	
	# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-FlickrExplorer.zip
	url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)

	PLog(int_lv); PLog(int_lc); PLog(latest_version); PLog(summ);  PLog(url);
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Addon vorher sichern!)			
		title = 'Update vorhanden - jetzt installieren'
		summary = 'Addon aktuell: ' + VERSION + ', neu auf Github: ' + latest_version
		tagline = cleanhtml(summ)
		thumb = R(ICON_UPDATER_NEW)
		url=py2_encode(url); 
		fparams="&fparams={'url': '%s', 'ver': '%s'}" % (quote_plus(url), latest_version) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary, 
			tagline=cleanhtml(summ))
			
		title = 'Update abbrechen'
		summary = 'weiter im aktuellen Addon'
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_UPDATER_NEW), 
			thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
	else:	
		title = 'Addon ist aktuell | weiter zum aktuellen Addon'
		summary = 'Addon Version ' + VERSION + ' ist aktuell (kein Update vorhanden)'
		summ = summ.splitlines()[0]		# nur 1. Zeile changelog
		tagline = "%s | Mehr in changelog.txt" % summ
		thumb = R(ICON_OK)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_OK), 
			thumb=R(ICON_OK), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
	
####################################################################################################
#	Hilfsfunktonen - für Kodiversion augelagert in Modul util_flickr.py
#----------------------------------------------------------------  

def router(paramstring):
	# paramstring: Dictionary mit
	# {<parameter>: <value>} Elementen
	paramstring = unquote_plus(paramstring)
	PLog(' router_params1: ' + paramstring)
	PLog(type(paramstring));
		
	if paramstring:	
		params = dict(parse_qs(paramstring[1:]))
		PLog(' router_params_dict: ' + str(params))
		try:
			if 'content_type' in params:
				if params['content_type'] == 'video':	# Auswahl im Addon-Menü
					Main()
			PLog('router action: ' + params['action'][0]) # hier immer action="dirList"
			PLog('router dirID: ' + params['dirID'][0])
			PLog('router fparams: ' + params['fparams'][0])
		except Exception as exception:
			PLog(str(exception))

		if params['action'][0] == 'dirList':			# Aufruf Directory-Listing
			newfunc = params['dirID'][0]
			func_pars = params['fparams'][0]

			# Funktionsaufrufe + Parameterübergabe via Var's 
			#	s. 00_Migration_PLEXtoKodi.txt
			# Modulpfad immer ab resources - nicht verkürzen.
			if '.' in newfunc:						# Funktion im Modul, Bsp.:
				l = newfunc.split('.')				# Bsp. resources.lib.updater.update
				PLog(l)
				newfunc =  l[-1:][0]				# Bsp. updater
				dest_modul = '.'.join(l[:-1])
				PLog(' router dest_modul: ' + str(dest_modul))
				PLog(' router newfunc: ' + str(newfunc))
				try:
					func = getattr(sys.modules[dest_modul], newfunc)
				except Exception as exception:
					PLog(str(exception))
					func = ''
				if func == '':						# Modul nicht geladen - sollte nicht
					li = xbmcgui.ListItem()			# 	vorkommen - s. Addon-Start
					msg1 = "Modul %s ist nicht geladen" % dest_modul
					msg2 = "Ursache unbekannt."
					PLog(msg1)
					MyDialog(msg1, msg2, '')
					xbmcplugin.endOfDirectory(HANDLE)

			else:
				func = getattr(sys.modules[__name__], newfunc)	# Funktion im Haupt-PRG OK		
			
			PLog(' router func_getattr: ' + str(func))		
			if func_pars != '""':		# leer, ohne Parameter?	
				# PLog(' router func_pars: Ruf mit func_pars')
				# func_pars = unquote_plus(func_pars)		# quotierte url auspacken - entf.
				PLog(' router func_pars unquote_plus: ' + str(func_pars))
				try:
					# Problem (spez. Windows): Parameter mit Escapezeichen (Windows-Pfade) müssen mit \\
					#	behandelt werden und werden dadurch zu unicode-Strings. Diese benötigen in den
					#	Funktionen eine UtfToStr-Behandlung.
					# Keine /n verwenden (json.loads: need more than 1 value to unpack)
					func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
					func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
					
					PLog("json.loads func_pars: " + func_pars)
					PLog('json.loads func_pars type: ' + str(type(func_pars)))
					mydict = json.loads(func_pars)
					PLog("mydict: " + str(mydict)); PLog(type(mydict))
				except Exception as exception:
					PLog('router_exception: {0}'.format(str(exception)))
					mydict = ''
				
				# PLog(' router func_pars: ' + str(type(mydict)))
				if 'dict' in str(type(mydict)):				# Url-Parameter liegen bereits als dict vor
					mydict = mydict
				else:
					mydict = dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in func_pars.split(',')))			
				PLog(' router func_pars: mydict: %s' % str(mydict))
				func(**mydict)
			else:
				func()
		else:
			PLog('router action-params: ?')
	else:
		# Plugin-Aufruf ohne Parameter
		Main()

#---------------------------------------------------------------- 
PLog('Addon_URL: ' + PLUGIN_URL)		# sys.argv[0], plugin://plugin.image.flickrexplorer/
PLog('ADDON_ID: ' + ADDON_ID); PLog(SETTINGS); PLog(ADDON_NAME);PLog(SETTINGS_LOC);
PLog(ADDON_PATH);PLog(ADDON_VERSION);
PLog('HANDLE: ' + str(HANDLE))

PluginAbsPath = os.path.dirname(os.path.abspath(__file__))
PLog('PluginAbsPath: ' + PluginAbsPath)

PLog('Addon: Start')
if __name__ == '__main__':
	try:
		router(sys.argv[2])
	except Exception as e: 
		msg = str(e)
		PLog('network_error: ' + msg)





		
