# -*- coding: utf-8 -*-
# util_flickr.py
#	

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
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError

import glob, shutil, time, ssl, string
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
	

# Globals
NAME		= 'FlickrExplorer'
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

ADDON_ID      	= 'plugin.image.flickrexplorer'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')		# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]						# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)

DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA


###################################################################################################
#									Hilfsfunktionen Kodiversion
#	Modulnutzung: 
#					import resources.lib.util as util
#					PLog=util.PLog;  home=util.home; ...  (manuell od.. script-generiert)
#
#	convert_util_imports.py generiert aus util.py die Zuordnungen PLog=util.PLog; ...
####################################################################################################
#----------------------------------------------------------------  
def PLog(msg, loglevel=xbmc.LOGDEBUG):
	if DEBUG == 'false':
		return
		
	#if isinstance(msg, str):		# entf. mit six
	#	msg = msg.encode('utf-8')
	
	loglevel = xbmc.LOGNOTICE
	# PLog('loglevel: ' + str(loglevel))
	if loglevel >= 2:
		xbmc.log("%s --> %s" % (NAME, msg), level=loglevel)
	 
#---------------------------------------------------------------- 
#	03.04.2019 data-Verzeichnisse des Addons in
#		../.kodi/userdata/addon_data/plugin.image.flickrexplorer
#  		Check / Initialisierung 
#	Die Funktion checkt bei jedem Aufruf des Addons data-Verzeichnis einschl. 
#		Unterverzeichnisse auf Existenz und legt bei Bedarf neu an. User-Info
#		 nur noch bei Fehlern (Anzeige beschnittener Verzeichnispfade im 
#		Kodi-Dialog nur verwirend).
#	 
def check_DataStores():
	PLog('check_DataStores:')
	store_Dirs = ["Dict", "slides"]
				
	# Check 
	#	falls ein Unterverz. fehlt, erzeugt make_newDataDir alle
	#	Datenverz. oder einzelne fehlende Verz. neu.
	ok=True	
	for Dir in store_Dirs:						# Check Unterverzeichnisse
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)
		if os.path.isdir(Dir_path) == False:	
			PLog('Datenverzeichnis fehlt: %s' % Dir_path)
			ok = False
			break
	
	if ok:
		return 'OK %s '	% ADDON_DATA			# Verz. existiert - OK
	else:
		# neues leeres Verz. mit Unterverz. anlegen / einzelnes fehlendes 
		#	Unterverz. anlegen 
		ret = make_newDataDir(store_Dirs)	
		if ret == True:						# ohne Dialog
			msg1 = 'Datenverzeichnis angelegt - Details siehe Log'
			msg2=''; msg3=''
			PLog(msg1)
			# xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)  # OK ohne User-Info
			return 	'OK - %s' % msg1
		else:
			msg1 = "Fehler beim Anlegen des Datenverzeichnisses:" 
			msg2 = ret
			msg3 = 'Bitte Kontakt zum Entwickler aufnehmen'
			PLog("%s\n%s" % (msg2, msg3))	# Ausgabe msg1 als exception in make_newDataDir
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return 	'Fehler: Datenverzeichnis konnte nicht angelegt werden'
				
#---------------------------
# ab Version 1.5.6
# 	erzeugt neues leeres Datenverzeichnis oder fehlende Unterverzeichnisse
def  make_newDataDir(store_Dirs):
	PLog('make_newDataDir:')
				
	if os.path.isdir(ADDON_DATA) == False:		# erzeugen, falls noch nicht vorh.
		try:  
			PLog('erzeuge %s' % ADDON_DATA)
			os.mkdir(ADDON_DATA)
		except Exception as exception:
			ok=False
			PLog(str(exception))
			return str(exception)		
				
	ok=True
	for Dir in store_Dirs:						# Unterverz. erzeugen
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)	
		if os.path.isdir(Dir_path) == False:	
			try:  
				PLog('erzeuge %s' % Dir_path)
				os.mkdir(Dir_path)
			except Exception as exception:
				ok=False
				PLog(str(exception))
				break
	if ok:
		return True
	else:
		return str(exception)
		
#----------------------------------------------------------------  
# Die Funktion Dict speichert + lädt Python-Objekte mittels Pickle.
#	Um uns das Handling mit keys zu ersparen, erzeugt die Funktion
#	trotz des Namens keine dicts. Aufgabe ist ein einfacher
#	persistenter Speicher. Der Name Dict lehnt sich an die
#	allerdings wesentlich komfortablere Dict-Funktion in Plex an.
#
#	Den Dict-Vorteil, beliebige Strings als Kennzeichnung zu ver-
#	wenden, können wir bei Bedarf außerhalb von Dict
#	mit der vars()-Funktion ausgleichen (siehe Zuweisungen). 
#
#	Falls (außerhalb von Dict) nötig, kann mit der Zusatzfunktion 
#	name() ein Variablenname als String zurück gegeben werden.
#	
#	Um die Persistenz-Variablen von den übrigen zu unterscheiden,
#	kennzeichnen wir diese mit vorangestelltem Dict_ (ist aber
#	keine Bedingung).
#
# Zuweisungen: 
#	Dictname=value 			- z.B. Dict_sender = 'ARD-Alpha'
#	vars('Dictname')=value 	- 'Dict_name': _name ist beliebig (prg-generiert)
#	Bsp. für Speichern:
#		 Dict('store', "Dict_name", Dict_name)
#			Dateiname: 		"Dict_name"
#			Wert in:		Dict_name
#	Bsp. für Laden:
#		CurSender = Dict("load", "CurSender")
#   Bsp. für CacheTime: 5*60 (5min) - Verwendung bei "load", Prüfung mtime 
#	ev. ergänzen: OS-Verträglichkeit des Dateinamens

def Dict(mode, Dict_name='', value='', CacheTime=None):
	PLog('Dict: ' + mode)
	# PLog('Dict: ' + str(Dict_name))
	# PLog('Dict: ' + str(type(value)))
	dictfile = "%s/%s" % (DICTSTORE, Dict_name)
	# PLog("dictfile: " + dictfile)
	
	if mode == 'store':	
		with open(dictfile, 'wb') as f: pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
		f.close
		return True
	if mode == 'remove':		# einzelne Datei löschen
		try:
			 os.remove(dictfile)
			 return True
		except:	
			return False
			
	if mode == 'ClearUp':			# Files im Dictstore älter als maxdays löschen
		maxdays = int(Dict_name)
		return ClearUp(DICTSTORE, maxdays*86400) # 1 Tag=86400 sec
			
	if mode == 'load':	
		if os.path.exists(dictfile) == False:
			PLog('Dict: %s nicht gefunden' % dictfile)
			return False
		if CacheTime:
			mtime = os.path.getmtime(dictfile)	# modified-time
			now	= time.time()
			CacheLimit = now - CacheTime		# 
			# PLog("now %d, mtime %d, CacheLimit: %d" % (now, mtime, CacheLimit))
			if CacheLimit > mtime:
				PLog('Cache miss: CacheLimit > mtime')
				return False
			else:
				PLog('Cache hit: load')	
		try:			
			with open(dictfile, 'rb')  as f: data = pickle.load(f)
			f.close
			PLog('load from Cache')
			return data
		# Exception  ausführlicher: s.o.
		except Exception as e:	
			PLog('UnpicklingError' + str(e))
			return False

#-------------------------
# Zusatzfunktion für Dict - gibt Variablennamen als String zurück
# Aufruf: name(var=var) - z.Z. nicht genutzt
def name(**variables):				
	s = [x for x in variables]
	return s[0]
#----------------------------------------------------------------
# Dateien löschen älter als seconds
#		directory 	= os.path.join(path)
#		seconds		= int (1 Tag=86400, 1 Std.=3600)
# leere Ordner werden entfernt
def ClearUp(directory, seconds):	
	PLog('ClearUp: %s, sec: %s' % (directory, seconds))	
	PLog('älter als: ' + seconds_translate(seconds))
	now = time.time()
	cnt_files=0; cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 
		PLog("ClearUp: globFiles " + str(len(files)))
		# PLog(" globFiles: " + str(files))
		for f in files:
			# PLog(os.stat(f).st_mtime)
			if os.stat(f).st_mtime < (now - seconds):
				os.remove(f)
				cnt_files = cnt_files + 1
			if os.path.isdir(f):		# Leerverz. entfernen
				if not os.listdir(f):
					os.rmdir(f)
					cnt_dirs = cnt_dirs + 1
		PLog("ClearUp: entfernte Dateien %s, entfernte Ordner %s" % (str(cnt_files), str(cnt_dirs)))	
		return True
	except Exception as exception:	
		PLog(str(exception))
		return False

#----------------------------------------------------------------  
# Prüft directory auf limit-Überschreitung,
#	löscht älteste Unterverzeichnisse bzw. 
#	Einzeldateien, falls kein Unterverz. exisitiert
# limit bisher nur MBytes und GBytes, Berechn. hier
#	einfach mit 10er- statt 2er-Potenzen.
def CheckStorage(directory, limit):
	PLog('CheckStorage: %s, limit: %s' % (directory, limit))
	
	cnt=1
	lm, bez = limit.split()			# "100 MBytes", "1 GByte", ..
	if "MBytes" in bez:
		limit = int(lm) * 1000000 
	else:
		limit = int(lm) * 1000000000 
	size = 	getFolderSize(directory)			# 1. Belegung ermitteln
	PLog('Check 1, limit: %s, size: %s' % (limit, size))
	
	if limit > int(size):						# Limit nicht erreicht
		return
	
	dirs = '%s/*' % directory					# 2. Schleife: Löschen / Abgleich
	while int(size) >= limit:
		cnt = cnt  + 1
		dirlist = glob.glob(dirs)
		dir_alt =  min(dirlist, key=os.path.getctime)
		PLog(u'lösche Verz.: %s' % dir_alt)
		shutil.rmtree(dir_alt, ignore_errors=True) # kompl. Verz. löschen
		size = 	getFolderSize(directory)		
		PLog('Check %s, limit: %s, size: %s' % (str(cnt),limit, size))
	return
#--------------------------------- 
# Helper für CheckStorage, aus: 
# https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
def getFolderSize(folder):
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath):
			total_size += os.path.getsize(itempath)
		elif os.path.isdir(itempath):
			total_size += getFolderSize(itempath)
	return total_size
	
#----------------------------------------------------------------  
# Listitems verlangen encodierte Strings auch bei Umlauten. Einige Quellen liegen in unicode 
#	vor (s. json-Auswertung in get_page) und müssen rückkonvertiert  werden.
# Hinw.: Teilstrings in unicode machen str-Strings zu unicode-Strings.
def UtfToStr(line):
	if type(line) == unicode:
		line =  line.encode('utf-8')
		return line
	else:
		return line	
		
def up_low(line, mode='up'):
	try:
		if PYTHON2:	
			if isinstance(line, unicode):
				line = line.encode('utf-8')
		if mode == 'up':
			return line.upper()
		else:
			return line.lower()
	except Exception as exception:	
		PLog('up_low: ' + str(exception))
	return up_low
#----------------------------------------------------------------  
# In Kodi fehlen die summary- und tagline-Zeilen der Plexversion. Diese ersetzen wir
#	hier einfach durch infoLabels['Plot'], wobei summary und tagline durch 
#	2 Leerzeilen getrennt werden (Anzeige links unter icon).
#
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Mehr s. PlayVideo
#

def addDir(li, label, action, dirID, fanart, thumb, fparams, summary='', tagline='', mediatype='', cmenu=True):
	PLog('addDir:')
	PLog(type(label))
	label=py2_encode(label)
	PLog('addDir - label: {0}, action: {1}, dirID: {2}'.format(label, action, dirID))
	PLog(type(summary)); PLog(type(tagline));
	summary=py2_encode(summary); tagline=py2_encode(tagline); 
	fparams=py2_encode(fparams); fanart=py2_encode(fanart); thumb=py2_encode(thumb);
	PLog('addDir - summary: {0}, tagline: {1}, mediatype: {2}, cmenu: {3}'.format(summary, tagline, mediatype, cmenu))
	
	li.setLabel(label)			# Kodi Benutzeroberfläche: Arial-basiert für arabic-Font erf.
	PLog('summary, tagline: %s, %s' % (summary, tagline))
	Plot = ''
	if tagline:								
		Plot = tagline
	if summary:									
		Plot = "%s\n\n%s" % (Plot, summary)
		
	if mediatype == 'video': 	# "video", "music" setzen: List- statt Dir-Symbol
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot, "mediatype": "video"})	
		isFolder = False		# nicht bei direktem Player-Aufruf - OK mit setResolvedUrl
		li.setProperty('IsPlayable', 'true')					
	else:
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot})	
		li.setProperty('IsPlayable', 'false')
		isFolder = True	
	
	li.setArt({'thumb':thumb, 'icon':thumb, 'fanart':fanart})
	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	PLog('PLUGIN_URL: ' + PLUGIN_URL)	# plugin://plugin.video.ardundzdf/
	PLog('HANDLE: ' + str(HANDLE))
	url = PLUGIN_URL+"?action="+action+"&dirID="+dirID+"&fanart="+fanart+"&thumb="+thumb+quote_plus(fparams)
	PLog("addDir_url: " + unquote_plus(url))
		
		
	xbmcplugin.addDirectoryItem(handle=HANDLE,url=url,listitem=li,isFolder=isFolder)
	
	PLog('addDir_End')		
	return	

#---------------------------------------------------------------- 

# Ersetzt R-Funktion von Plex (Pfad zum Verz. Resources, hier zusätzl. Unterordner möglich) 
# Falls abs_path nicht gesetzt, wird der Pluginpfad zurückgegeben, sonst der absolute Pfad
# für lokale Icons üblicherweise PluginAbsPath.
def R(fname, abs_path=False):	
	PLog('R(fname): %s' % fname); # PLog(abs_path)
	# PLog("ADDON_PATH: " + ADDON_PATH)
	if abs_path:
		try:
			# fname = '%s/resources/%s' % (PluginAbsPath, fname)
			path = os.path.join(ADDON_PATH,fname)
			return path
		except Exception as exception:
			PLog(str(exception))
	else:
		if fname.endswith('png'):	# Icons im Unterordner images
			fname = '%s/resources/images/%s' % (ADDON_PATH, fname)
			fname = os.path.abspath(fname)
			# PLog("fname: " + fname)
			return os.path.join(fname)
		else:
			fname = "%s/resources/%s" % (ADDON_NAME, fname)
			fname = os.path.abspath(fname)
			return fname 
#----------------------------------------------------------------  
# ersetzt Resource.Load von Plex 
# abs_path s.o.	R()	
def RLoad(fname, abs_path=False): # ersetzt Resource.Load von Plex 
	if abs_path == False:
		fname = '%s/resources/%s' % (ADDON_PATH, fname)
	path = os.path.join(fname) # abs. Pfad
	PLog('RLoad: %s' % str(fname))
	try:
		if PYTHON2:
			with open(path,'r') as f:
				page = f.read()		
		else:
			with open(path,'r', encoding="utf8") as f:
				page = f.read()		
	except Exception as exception:
		PLog(str(exception))
		page = ''
	return page
#----------------------------------------------------------------
# Gegenstück zu RLoad - speichert Inhalt page in Datei fname im  
#	Dateisystem. PluginAbsPath muss in fname enthalten sein,
#	falls im Pluginverz. gespeichert werden soll 
#  Migration Python3: immer utf8
# 
def RSave(fname, page, withcodec=False): 
	PLog('RSave: %s' % str(fname))
	PLog(withcodec)
	path = os.path.join(fname) # abs. Pfad
	msg = ''					# Rückgabe leer falls OK
	try:
		if PYTHON2:
			if withcodec:		# 14.11.0219 Kompat.-Maßnahme
				import codecs	#	für DownloadExtern
				with codecs.open(path,'w', encoding='utf-8') as f:
					f.write(page)	
			else:
				with open(path,'w') as f:
					f.write(page)		
		else:
			with open(path,'w', encoding="utf8") as f:
				f.write(page)
		
	except Exception as exception:
		msg = str(exception)
		PLog(msg)
	return msg
#----------------------------------------------------------------  
#	doppelte utf-8-Enkodierung führt an manchen Stellen zu Sonderzeichen
#  	14.04.2019 entfernt: (':', ' ')
def repl_json_chars(line):	# für json.loads (z.B.. in router) json-Zeichen in line entfernen
	line_ret = line
	#PLog(type(line_ret))
	for r in	((u'"', u''), (u'\\', u''), (u'\'', u'')
		, (u'&', u'und'), ('(u', u'<'), (u')', u'>'),  (u'∙', u'|')
		, (u'„', u'>'), (u'“', u'<'), (u'”', u'>'),(u'°', u' Grad')
		, (u'\r', u'')):			
		line_ret = line_ret.replace(*r)
	
	return line_ret
#---------------------------------------------------------------- 
# strip-Funktion, die auch Zeilenumbrüche innerhalb des Strings entfernt
#	\s [ \t\n\r\f\v - s. https://docs.python.org/3/library/re.html
def mystrip(line):	
	line_ret = line	
	line_ret = re.sub(r"\s+", " ", line)	# Alternative für strip + replace
	# PLog(line_ret)		# bei Bedarf
	return line_ret
#----------------------------------------------------------------  	
# DirectoryNavigator - Nutzung des Kodi-builtin, der Code der PMS-Version kann entfallen
# S. http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmcgui.html
# mytype: 	0 : ShowAndGetDirectory, 1 : ShowAndGetFile, 2
# mask: 	nicht brauchbar bei endungslosen Dateien, Bsp. curl
def DirectoryNavigator(settingKey, mytype, heading, shares='files', useThumbs=False, \
	treatAsFolder=False, path=''):
	PLog('DirectoryNavigator:')
	PLog(settingKey); PLog(mytype); PLog(heading); PLog(path);
	
	dialog = xbmcgui.Dialog()
	d_ret = dialog.browseSingle(int(mytype), heading, 'files', '', False, False, path)	
	PLog('d_ret: ' + d_ret)
	
	SETTINGS.setSetting(settingKey, d_ret)	
	return 
#----------------------------------------------------------------  
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	#pos2 = mString.find(mSecondChar, pos1 + ind+1)		
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
		
	#PLog(mString); PLog(mFirstChar); PLog(mSecondChar); 	# bei Bedarf
	#PLog(pos1); PLog(ind); PLog(pos2);  PLog(rString); 
	return rString
#---------------------------------------------------------------- 
def blockextract(blockmark, blockendmark, mString):  # extrahiert Blöcke begrenzt durch blockmark aus mString
	#   Block wird durch blockendmark begrenzt, falls belegt 
	#	blockmark bleibt Bestandteil der Rückgabe
	#	Verwendung, wenn xpath nicht funktioniert (Bsp. Tabelle EPG-Daten www.dw.com/de/media-center/live-tv/s-100817)
	rlist = []				
	if 	blockmark == '' or 	mString == '':
		PLog('blockextract: blockmark or mString leer')
		return rlist
	
	pos = mString.find(blockmark)
	if 	mString.find(blockmark) == -1:
		PLog('blockextract: blockmark <%s> nicht in mString enthalten' % blockmark)
		# PLog(pos) PLog(blockmark);PLog(len(mString));PLog(len(blockmark));
		return rlist
		
	pos2 = 1
	while pos2 > 0:
		pos1 = mString.find(blockmark)						
		ind = len(blockmark)
		pos2 = mString.find(blockmark, pos1 + ind)		
		
		if blockendmark:
			pos3 = mString.find(blockendmark, pos1 + ind)
			ind_end = len(blockendmark)
			block = mString[pos1:pos3+ind_end]	# extrahieren einschl.  blockmark + blockendmark
			# PLog(block)			
		else:
			block = mString[pos1:pos2]			# extrahieren einschl.  blockmark
			# PLog(block)		
		mString = mString[pos2:]	# Rest von mString, Block entfernt
		rlist.append(block)
		# PLog(rlist)
	# PLog(rlist)		
	return rlist  
#----------------------------------------------------------------  
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	cleantext = line
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#----------------------------------------------------------------  	
def decode_url(line):	# in URL kodierte Umlaute und & wandeln, Bsp. f%C3%BCr -> für, 	&amp; -> &
	line = py2_decode(line)
	unquote(line)
	line = line.replace(u'&amp;', u'&')
	return line
#----------------------------------------------------------------  
# Migration PY2/PY3: py2_decode aus kodi-six
def make_filenames(title):
	PLog('make_filenames:')
	# erzeugt - hoffentlich - sichere Dateinamen (ohne Extension)
	# zugeschnitten auf Titelerzeugung in meinen Plugins 
	
	title = py2_decode(title)
	fname = transl_umlaute(title)		# Umlaute	
	
	valid_chars = "-_ %s%s" % (string.ascii_letters, string.digits)
	fname = ''.join(c for c in fname if c in valid_chars)
	fname = fname.replace(u' ', u'_')

	return fname
#----------------------------------------------------------------  
def transl_umlaute(line):	# Umlaute übersetzen, wenn decode nicht funktioniert
	PLog('transl_umlaute:')
	# line= py2_decode(line)	
	# line= str(line)	
	line_ret = line
	line_ret = line_ret.replace(u"Ä", u"Ae", len(line_ret))
	line_ret = line_ret.replace(u"ä", u"ae", len(line_ret))
	line_ret = line_ret.replace(u"Ü", u"Ue", len(line_ret))
	line_ret = line_ret.replace(u'ü', u'ue', len(line_ret))
	line_ret = line_ret.replace(u"Ö", u"Oe", len(line_ret))
	line_ret = line_ret.replace(u"ö", u"oe", len(line_ret))
	line_ret = line_ret.replace(u"ß", u"ss", len(line_ret))	
	return line_ret

#---------------------------------------------------------------- 
# Migration PY2/PY3: py2_decode aus kodi-six
def unescape(line):
# HTML-Escapezeichen in Text entfernen, bei Bedarf erweitern. ARD auch &#039; statt richtig &#39;	
#					# s.a.  ../Framework/api/utilkit.py
#					# Ev. erforderliches Encoding vorher durchführen - Achtung in Kodis 
#					#	Python-Version v2.26.0 'ascii'-codec-Error bei mehrfachem decode
#
	# PLog(type(line))
	if line == None or line == '':
		return ''	
	line = py2_decode(line)
	for r in	((u"&amp;", u"&"), (u"&lt;", u"<"), (u"&gt;", u">")
		, (u"&#39;", u"'"), (u"&#039;", u"'"), (u"&quot;", u'"'), (u"&#x27;", u"'")
		, (u"&ouml;", u"ö"), (u"&auml;", u"ä"), (u"&uuml;", u"ü"), (u"&szlig;", u"ß")
		, (u"&Ouml;", u"Ö"), (u"&Auml;", u"Ä"), (u"&Uuml;", u"Ü"), (u"&apos;", u"'")
		, (u"&nbsp;|&nbsp;", u""), (u"&nbsp;", u""), 
		# Spezialfälle:
		#	https://stackoverflow.com/questions/20329896/python-2-7-character-u2013
		#	"sächsischer Genetiv", Bsp. Scott's
		#	Carriage Return (Cr)
		(u"–", u"-"), (u"&#x27;", u"'"), (u"&#xD;", u""), (u"\xc2\xb7", u"-"),
		(u'undoacute;', u'o'), (u'&eacute;', u'e'), (u'&egrave;', u'e'),
		(u'&atilde;', u'a')):
		line = line.replace(*r)
	return line
#----------------------------------------------------------------  
# Migration PY2/PY3: py2_decode aus kodi-six
def transl_json(line):	# json-Umlaute übersetzen
	# Vorkommen: Loader-Beiträge ZDF/3Sat (ausgewertet als Strings)
	# Recherche Bsp.: https://www.compart.com/de/unicode/U+00BA
	# 
	line= py2_decode(line)	
	#PLog(line)
	for r in ((u'\\u00E4', u"ä"), (u'\\u00C4', u"Ä"), (u'\\u00F6', u"ö")		
		, (u'\\u00C6', u"Ö"), (u'\\u00D6', u"Ö"),(u'\\u00FC', u"ü"), (u'\\u00DC', u'Ü')
		, (u'\\u00DF', u'ß'), (u'\\u0026', u'&'), (u'\\u00AB', u'"')
		, (u'\\u00BB', u'"')
		, (u'\xc3\xa2', u'*')			# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2
		, (u'u00B0', u' Grad')		# u00BA -> Grad (3Sat, 37 Grad)	
		, (u'u00EA', u'e')			# 3Sat: Fête 
		, (u'u00E9', u'e')			# 3Sat: Fabergé
		, (u'u00E6', u'ae')):			# 3Sat: Kjaerstad

		line = line.replace(*r)
	#PLog(line)
	return line	
#---------------------------------------------------------------- 
# Format seconds	86400	(String, Int, Float)
# Rückgabe:  		1d, 0h, 0m, 0s	(days=True)
#		oder:		0h, 0d				
def seconds_translate(seconds, days=False):
	#PLog('seconds_translate:')
	#PLog(seconds)
	if seconds == '' or seconds == 0  or seconds == 'null':
		return ''
	if int(seconds) < 60:
		return "%s sec" % seconds
	seconds = float(seconds)
	day = seconds / (24 * 3600)	
	time = seconds % (24 * 3600)
	hour = time / 3600
	time %= 3600
	minutes = time / 60
	time %= 60
	seconds = time
	if days:
		#PLog("%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds))
		return "%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds)
	else:
		#PLog("%d:%02d" % (hour, minutes))
		return  "%d:%02d" % (hour, minutes)		
#---------------------------------------------------------------- 	
# Holt User-Eingabe für Suche ab
#	s.a. get_query (für Search , ZDF_Search)
def get_keyboard_input():
	kb = xbmc.Keyboard('', 'Bitte Suchwort(e) eingeben')
	kb.doModal() # Onscreen keyboard
	if kb.isConfirmed() == False:
		return ""
	inp = kb.getText() # User Eingabe
	return inp		
#----------------------------------------------------------------
# Locale.LocalString( steht in Kodi nicht zur Verfügung. Um
#	die vorh. Sprachdateien (json-Format) unverändert nutzen zu
#	können, suchen wir hier den zum Addon-internen String 
#	passenden locale-String durch einfachen Textvergleich im 
#	passenden locale-Verzeichnis ( Dict('load', 'loc_file')).
# Die Plex-Lösung von czukowski entfällt damit.

def L(string):	
	PLog('L: ' + string)
	loc_file = Dict('load', 'loc_file')
	if loc_file == False or os.path.exists(loc_file) == False:	
		return 	string
	
	lines = RLoad(loc_file, abs_path=True)
	lines = lines.splitlines()
	lstring = ''	
	for line in lines:
		term1 = line.split('":')[0].strip()
		term1 = term1.strip()
		term1 = term1.replace('"', '')			# Hochkommata entfernen
		# PLog(term1)
		if term1 == string:						# string stimmt mit Basis-String überein?
			lstring = line.split(':')[1]		# 	dann Ziel-String zurückgeben
			lstring = lstring.strip()
			lstring = lstring.replace('"', '') 	# Hochkommata + Komma entfernen
			lstring = lstring.replace(',', '')
			break
			
	PLog(string); PLog(lstring)		
	if lstring:
		return lstring
	else:
		return string						# Rückgabe Basis-String, falls kein Paar gefunden
#----------------------------------------------------------------
####################################################################################################
# Für Flickr verzichten wir auf die 2. Stufe mit Zertifikaten wie bei tunein2017 und ardundzdf - wg.
#	api-Nutzung nicht benötigt.
#
def RequestUrl(CallerName, url):
	PLog('RequestUrl: ' + url)
	UrlopenTimeout = 3			# Timeout sec
	
	msg=''
	loc = Dict('load', 'loc')						# Bsp. fr, 	loc_browser nicht benötigt
	PLog('loc: ' + loc)	
	url = py2_encode(url)

	msg=''
	PLog('page1:')			
	try:																# Step 1: urllib2.Request
		PLog("RequestUrl, step 1, called from %s" % CallerName)
		req = Request(url)	
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3')
		req.add_header('Accept-Language',  '%s, en;q=0.9, %s;q=0.7'	% (loc, loc))
			
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
		gcontext.check_hostname = False
		gcontext.verify_mode = ssl.CERT_NONE
		ret = urlopen(req, context=gcontext, timeout=UrlopenTimeout)
		
		compressed = ret.info().get('Content-Encoding') == 'gzip'
		PLog("compressed: " + str(compressed))
		page = ret.read()
		PLog(len(page))
		if compressed:
			buf = StringIO(page)
			f = gzip.GzipFile(fileobj=buf)
			page = f.read()
			PLog(len(page))
		ret.close()
		# PLog(page[:160])
	except Exception as exception:
		error_txt = "RequestUrl: %s-1: %s" % (CallerName, str(exception)) 
		error_txt = error_txt + ' | ' + url				 			 	 
		msg =  error_txt
		PLog(msg)
		page=''
				
	if '/video_download.gne' in url:		# Videodaten unverändert weiter 
		return page, msg
	else:
		PLog(page[:100])
		page = page.decode('utf-8')
		return page, msg		
		
####################################################################################################
# PlayVideo aus Kodi-Addon-ARDundZDF, Modul util  
#	Details s. dort
#	Behandl.- Untertitel entfällt hier, dto. Header-Checks
#
def PlayVideo(url, title, thumb, Plot, sub_path=None, Merk='false'):	
	PLog('PlayVideo:'); PLog(url); PLog(title);	 PLog(Plot); 
	PLog(sub_path);
	
	# Header-Check: Flickr gibt bei Fehlern HTML-Seite zurück 
	#	Bsp.:  <h1>This page is private.</h1>
	#	OK: content-type': 'video/mp4'

	# Fehlervideo nicht benötigt (Zugriff nur auf öffentl. Inhalte)
	# 01.12.2019 Header-Check gelöscht, dto. in RequestUrl,
	#if 'text/html' in str(page):				# ffmpeg-erzeugtes Fehlerbild-mp4-Video (10 sec)
	#	PLog('Error: Textpage ' + url)
	#	url =  os.path.join("%s", 'PrivatePage720x640.mp4') % (RESOURCES_PATH)			
	#	return PlayVideo(url, title, thumb, Plot)			
				
	li = xbmcgui.ListItem(path=url)		
	li.setArt({'thumb': thumb, 'icon': thumb})
	
	Plot=Plot.replace('||', '\n')				# || Code für LF (\n scheitert in router)
	infoLabels = {}
	infoLabels['title'] = title
	infoLabels['sorttitle'] = title
	#infoLabels['genre'] = genre
	#infoLabels['plot'] = Plot
	#infoLabels['plotoutline'] = Plot
	infoLabels['tvshowtitle'] = Plot
	infoLabels['tagline'] = Plot
	infoLabels['mediatype'] = 'video'
	li.setInfo(type="Video", infoLabels=infoLabels)
			
	# Abfrage: ist gewählter Eintrag als Video deklariert? - Falls ja,	# IsPlayable-Test
	#	erfolgt der Aufruf indirekt (setResolvedUrl). Falls nein,
	#	wird der Player direkt aufgerufen. Direkter Aufruf ohne IsPlayable-Eigenschaft 
	#	verhindert Resume-Funktion.
	# Mit xbmc.Player() ist  die Unterscheidung Kodi V18/V17 nicht mehr erforderlich,
	#	xbmc.Player().updateInfoTag bei Kodi V18 entfällt. 
	# Die Player-Varianten PlayMedia + XBMC.PlayMedia scheitern bei Kommas in Url.	
	# 
	IsPlayable = xbmc.getInfoLabel('ListItem.Property(IsPlayable)') # 'true' / 'false'
	PLog("IsPlayable: %s, Merk: %s" % (IsPlayable, Merk))
	PLog("kodi_version: " + KODI_VERSION)							# Debug
	# kodi_version = re.search('(\d+)', KODI_VERSION).group(0) # Major-Version reicht hier - entfällt
			
	#if Merk == 'true':										# entfällt bisher - erfordert
	#	xbmc.Player().play(url, li, windowed=False) 		# eigene Resumeverwaltung
	#	return
	
	if IsPlayable == 'true':								# true
		xbmcplugin.setResolvedUrl(HANDLE, True, li)			# indirekt
	else:													# false, None od. Blank
		xbmc.Player().play(url, li, windowed=False) 		# direkter Start
	return				
			

####################################################################################################


