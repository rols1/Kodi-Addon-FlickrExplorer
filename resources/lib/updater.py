# -*- coding: utf-8 -*-
################################################################################
#			updater.py - Part of Kodi-Addon-FlickrExplorer
#
#
################################################################################
#	01.12.2019 Migration Python3 Modul kodi_six + manuelle Anpassungen
# 	18.03.2020 adjust_AddonXml: Anpassung python-Version an Kodi-Version
#	13.04.2020 Aktualisierung adjust_AddonXml
# 	29.01.2023 Aktualisierung adjust_line für Kodi 20 Nexus
################################################################################
# 

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
	from urlparse import urljoin, urlparse, urlunparse , urlsplit, parse_qs 
elif PYTHON3:				
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse, urlsplit, parse_qs  
	from urllib.request import Request, urlopen, urlretrieve
	from urllib.error import URLError

# Standard:
import shutil						# Dir's löschen
import zipfile, re
import io 							# Python2+3 -> update() io.BytesIO für Zipfile

import resources.lib.util_flickr as util
PLog=util.PLog; stringextract=util.stringextract; MyDialog=util.MyDialog;
cleanhtml=util.cleanhtml; RLoad=util.RLoad; RSave=util.RSave; 
 
ADDON_ID      	= 'plugin.image.flickrexplorer'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
ADDON_PATH    	= SETTINGS.getAddonInfo('path')

FEED_URL = 'https://github.com/{0}/releases.atom'

################################################################################
TITLE = 'FlickrExplorer'
REPO_NAME		 	= 'Kodi-Addon-FlickrExplorer'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME

################################################################################

# This gets the release name
def get_latest_version():
	PLog('get_latest_version:')
	try:
		# https://github.com/rols1/Kodi-Addon-FlickrExplorer/releases.atom
		# releases.atom liefert Releases-Übersicht als xml-Datei 
		release_feed_url = ('https://github.com/{0}/releases.atom'.format(GITHUB_REPOSITORY))
		PLog(release_feed_url)
			
		r = urlopen(release_feed_url)
		page = r.read()					
		page=page.decode('utf-8')				
		PLog(len(page))
		# PLog(page[:800])

		link	= stringextract('<link rel', '"/>', page)			# ../releases/tag/0.2.9"/
		tags 	= link.split('/')
		tag = tags[-1]												# 0.2.9
		title	= stringextract('<title>', '</title>', page)		# 
		content	= stringextract('li&gt;', '</content>', page)
		summary = cleanSummary(content)
		# PLog("content: "  + content)
		# PLog(link); PLog(title); PLog(summary); PLog(tag);  
		return (title, summary, tag)
	except Exception as exception:
		PLog(str(exception))
		return ('', '', '')

################################################################################
# decode latest_version (hier bytestring) erforderlich für Pfad-Bau in 
def update_available(VERSION):
	PLog('update_available:')

	# save_restore('save')					# Test-Session save_restore
	# save_restore('restore')
	# return (False, '', '', '', '', '')
	
	try:
		title, summ, tag = get_latest_version()
		PLog(tag); 	# PLog(latest_version_str); PLog(summ);
		
		if tag:
			# wir verwenden auf Github die Versionierung nicht im Plugin-Namen
			# latest_version  = title 
			latest_version  = tag		# Format hier: '1.4.1'

			current_version = VERSION
			int_lv = tag.replace('.','')
			int_cv = current_version.replace('.','')
			PLog('Github: ' + latest_version); PLog('lokal: ' + current_version); 
			# PLog(int_lv); PLog(int_cv)
			return (int_lv, int_cv, latest_version, summ, tag)
	except Exception as exception:	
		PLog(str(exception))
	return (False, '', '', '', '', '')		# int_lv hier bool statt string
            
################################################################################
def update(url, ver):
	PLog('update: ' + ver)	
	
	if ver:		
		msg1 = 'Addon Update auf  Version {0}'.format(ver)
		msg2 = 'Update erfolgreich - weiter zum aktuellen Addon'  	# Kodi: kein Neustart notw.
		try:
			dest_path 	= xbmc.translatePath("special://home/addons/")
			r 			= urlopen(url)
			PLog('Mark1')
			zip_data	= zipfile.ZipFile(io.BytesIO(r.read()))
			PLog('Mark2')
			
			# save_restore('save')									# Cache sichern - entfällt, s.o.
			
			PLog(dest_path)
			PLog(ADDON_PATH)
			shutil.rmtree(ADDON_PATH)		# remove addon, Verzicht auf ignore_errors=True
			PLog('Mark3')
			zip_data.extractall(dest_path)
				
			# save_restore('restore')								# Cache sichern	 - entfällt, s.o.
			PLog('Mark4')
			adjust_AddonXml()										# addon.xml an Kodi-Verson anpassen
					
		except Exception as exception:
			msg1 = 'Update fehlgeschlagen'
			msg2 = 'Error: ' + str(exception)
												
		MyDialog(msg1, msg2, '')
	else:
		msg1 = 'Update fehlgeschlagen'
		msg2 =  'Version ' + ver + 'nicht gefunden!'
		MyDialog(msg1, msg2, '')

################################################################################
# adjust_AddonXml:  Anpassung der python-Version in der neu installierten 
#	addon.xml an die akt. Kodi-Version. Passende addon.xml bleibt unver-
#	ändert. Da Kodi die addon.xml erst bei Neustart od. Addon-Installation
#	prüft, muss die Änderung nicht bereits vor dem Speichern im zip erfolgen.
# 
#	Python-Versionen s. https://kodi.wiki/view/Addon.xml#Dependency_versions
#		Leia / Matrix		version="2.25.0" / version="3.0.0"
#	Addon-Version (Bsp.):	version="2.8.5" /  version="2.8.5+matrix"
# 
# Nach Beendigung des Updates wird bei jedem Laden des Moduls util
#	in check_AddonXml das Verzeichnis ADDON_DATA angepasst (s. dort)
# 
def adjust_AddonXml():
	PLog('adjust_AddonXml:')
	
	path = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/addon.xml')
	PLog(path)
	page = RLoad(path, abs_path=True)
	change = False
	new_lines = []
	lines = page.splitlines()
	
	for line in lines:
		new_line = line
		# PLog(line)		# Debug
		if 'addon="xbmc.python"' in line or 'addon id=' in line:
			new_line = adjust_line(line)
			if new_line != line:
				change = True
				PLog('adjust_AddonXml_oldline: %s' % line)
				PLog('adjust_AddonXml_newline: %s' % new_line)
				new_line = line.replace(line, new_line)
		new_lines.append(new_line)	
	
	if change == False:
		PLog(u'adjust_AddonXml: addon.xml unverändert')
	else:
		page = '\n'.join(new_lines)
		RSave(path, page)		
	return	

#------------------------------
def adjust_line(line):
	PLog('adjust_line:')
	KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')
	PLog(KODI_VERSION)
	new_line = line

	try:
		vers = re.search(u'(\d+).', KODI_VERSION).group(0)
	except Exception as exception:
		PLog(str(exception))
		vers = "19"														# Default Matrix
	vers = int(vers)
	PLog("vers: %d" % vers)
	
	if vers < 19:														# Leia, Krypton, ..
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '2.25.0')				
		if 'addon id=' in line:
			new_line = line.replace('+matrix', '')						# ev. Downgrade				
			new_line = line.replace('+nexus', '')						# ev. Downgrade
	
	if 	vers == 19:														# Matrix
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '3.0.0')
		if 'addon id=' in line:
			addon_ver = stringextract('version="', '"', line)
			if 'matrix' not in line:									
				new_line = line.replace(addon_ver, '%s+matrix' % addon_ver)	
	if 	vers == 20:														# Nexus
		if 'addon="xbmc.python"' in line:
			python_ver = stringextract('version="', '"', line)
			new_line = line.replace(python_ver, '3.0.1')
		if 'addon id=' in line:
			addon_ver = stringextract('version="', '"', line)
			if 'nexus' not in line:									
				new_line = line.replace(addon_ver, '%s+nexus' % addon_ver)	
								
	return new_line	
	
################################################################################
# save_restore:  Cache sichern / wieder herstellen
#	funktioniert nicht unter Windows im updater-Modul - daher hierher verlagert
#	Aufrufer update (vor + nach Austausch)
# Windows-Problem: ohne Dir-Wechsel aus RESSOURCES_DIR Error 32 (belegter Prozess)
# 03.05.2019 Funktion wieder entfernt - s.o.

	
################################################################################# 
# clean tag names based on your release naming convention
def cleanSummary(summary):
	
	summary = (summary.replace('&lt;','').replace('&gt;','').replace('/ul','')
		.replace('/li','').replace('\n', ' | '))
	summary =  (summary.replace('| ul |', ' | ').replace('/h3', '')
		.replace('&quot;', '"').replace('| li', '| ').replace('-&amp;gt;', '->'))
		
	return summary.lstrip()
