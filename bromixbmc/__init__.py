"""
Version 2.1.2 (2014.08.04)
- ADD: logDebug, logWarning, logInfo and logError

Version 2.1.1 (2014.08.03)
- ADD: plugin.getFormatTime(hour, minute, seconds)

Version 2.1.0 (2014.07.28)
- CHG: plugin.getSettingAsBool(name, default)

Version 2.0.9 (2014.07.28)
- ADD: plugin.getSettingAsFloat(name, default)
- ADD: plugin.setSettingAsFloat(name, value)
- ADD: plugin.setSettingAsString(name, value)
- ADD: plugin.getSettingAsString(name, default)

Version 2.0.8 (2014.07.26)
- ADD: plugin.getSettingAsInt(mapping={....}) for mapping values

Version 2.0.7 (2014.07.25)
- ADD: addImage(...) will also set the setInfo('pictures'...) info labels

Version 2.0.6 (2014.07.20)
- ADD: addImage(...)

Version 2.0.5 (2014.07.19)
- ADD: executebuiltin(function)
- ADD: addSortMethod(sort_method) for add sorting

Version 2.0.4 (2014.07.15)
- ADD: decodeHtmlText(text) for decoding html escaped text

Version 2.0.3 (2014.07.13)
- ADD: getSettingAsInt

Version 2.0.2 (2014.07.10)
- FIX: Android won't return a valid language so I added a default value 

Version 2.0.1 (2014.07.08)
- complete restructuring

Version 1.0.2 (2014.06.25)
- added 'getFavorites', 'addFavorite' and 'removeFavorite'
- set the encoding for the favorite routines to utf-8
- removed 'duration' and 'plot' from addVideoLink -> therefore use 'additionalInfoLabels'

Version 1.0.1 (2014.06.24)
- added support for helping with favorites
- initial release
"""

import locale
import re
import sys
import urlparse
import HTMLParser

import xbmc

from plugin import Plugin
from keyboard import Keyboard
from search_history import SeachHistory

def logDebug(text):
    xbmc.log(msg=text, level=xbmc.LOGDEBUG)
    pass

def logInfo(text):
    xbmc.log(msg=text, level=xbmc.LOGINFO)
    pass

def logWarning(text):
    xbmc.log(msg=text, level=xbmc.LOGWARNING)
    pass

def logError(text):
    xbmc.log(msg=text, level=xbmc.LOGERROR)
    pass

def getFormatDateShort(year, month, day):
    date_format = xbmc.getRegion('dateshort')
    date_format = date_format.replace('%d', day)
    date_format = date_format.replace('%m', month)
    date_format = date_format.replace('%Y', year)
    return date_format

def getFormatTime(hour, minute, seconds=None):
    time_format = xbmc.getRegion('time')
    _hour = hour
    if len(_hour)==1:
        _hour='0'+_hour
        
    _min = minute
    if len(_min)==1:
        _min='0'+_min
    
    _sec = seconds
    if _sec==None:
        _sec='00'
    if len(_sec)==1:
        _sec='0'+_sec
        
    time_format = '%H:%M'
    time_format = time_format.replace('%H', _hour)
    time_format = time_format.replace('%M', _min)
    time_format = time_format.replace('%S', _sec)
        
    return time_format

def executebuiltin(function):
    xbmc.executebuiltin(function)

def stripHtmlFromText(text):
    return re.sub('<[^<]+?>', '', text)

def decodeHtmlText(text):
    hp = HTMLParser.HTMLParser()
    return hp.unescape(text)

def getParam(name, default=None):
    args = urlparse.parse_qs(sys.argv[2][1:])
    value = args.get(name, None)
    if value and len(value)>=1:
        return value[0]
    
    return default

def getLanguageId(default='en-US'):
    result = default
    
    try:
        language = locale.getdefaultlocale()
        if language and len(language)>=1 and language[0]:
            result = language[0].replace('_', '-')
    except:
        # do nothing
        pass
    
    return result