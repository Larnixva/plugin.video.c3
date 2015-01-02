import sys
import os
import xbmc
import xbmcaddon
import urllib
import urllib2
import urlparse
import xbmcplugin
import xbmcgui
import xbmcvfs
import time
import json as Json
from xml.dom import minidom
from datetime import datetime, timedelta

addon           = xbmcaddon.Addon('plugin.video.c3')
loc             = addon.getLocalizedString
jsonurl         = 'https://31c3.cc/cccsync/congress/2014/Fahrplan/schedule.json'
addondir        = xbmc.translatePath(addon.getAddonInfo('profile'))
addon_handle    = int(sys.argv[1])
resolution      = addon.getSetting('resolution') #SD - 0; HD - 1; Auto - 2
translated      = addon.getSetting('translated') #original - 0; translated - 1
parameters      = dict(urlparse.parse_qsl(sys.argv[2][1:]))

if not xbmcvfs.exists(addondir):
    xbmcvfs.mkdirs(addondir)

if sys.argv[1] == 'resetetag':
    addon.setSetting('cache-etag', '')
    if xbmcvfs.exists(os.path.join(addondir, 'schedule.json')):
        xbmcvfs.delete(os.path.join(addondir, 'schedule.json'))
    d = xbmcgui.Dialog()
    d.ok('c3 Videos Add-on', loc(30104))
    exit()

if not addon.getSetting('cache-etag') or not xbmcvfs.exists(os.path.join(addondir, 'schedule.json')):
    response = urllib2.urlopen(jsonurl)
    addon.setSetting('cache-etag', response.headers.get('ETag'))
    json = response.read()
    with open(os.path.join(addondir, 'schedule.xml'), 'w') as file:
        file.write(json)
else:
    req = urllib2.Request(jsonurl)
    req.add_header('If-None-Match', addon.getSetting('cache-etag'))
    try:
        response = urllib2.urlopen(req)
        addon.setSetting('cache-etag', response.headers.get('ETag'))
        json = response.read()
        with open(os.path.join(addondir, 'schedule.json'), 'w') as file:
            file.write(json)
    except urllib2.HTTPError:
        with open(os.path.join(addondir, 'schedule.json'), 'r') as file:
            xml = file.read()

if not xbmcvfs.exists(os.path.join(addondir, 'schedule.json')):
    response = urllib2.urlopen('http://events.ccc.de/congress/2014/Fahrplan/schedule.json')
    json = response.read()
    with open(os.path.join(addondir, 'schedule.json'), 'w') as file:
        file.write(json)
else:
    with open(os.path.join(addondir, 'schedule.json'), 'r') as file:
        json = file.read()

fahrplan = Json.loads(json)

def parse_datetime_string(timestr):
    timestr = timestr.rsplit('+', 1)
    timeo = time.strptime(timestr[0], '%Y-%m-%dT%H:%M:%S')
    timeo = datetime.fromtimestamp(time.mktime(timeo))
    timezone = timestr[1].split(':', 1)
    timezone = timedelta(hours=int(timezone[0]), minutes=int(timezone[1]))
    return timeo - timezone

def find_current(json, roomstr):
    if roomstr == 'Saal S':
        return False
    itemlist = json['schedule']['conference']['days']
    for day in itemlist:
        start = parse_datetime_string(day['day_start'])
        end = parse_datetime_string(day['day_end'])
        if start <= datetime.utcnow() < end:
            saal = day['rooms'][roomstr]
            for talk in saal:
                date = parse_datetime_string(talk['date'])
                duration = talk['duration'].split(':', 1)
                duration = timedelta(hours=int(duration[0]), minutes=int(duration[1]))
                if date <= datetime.utcnow() < date + duration:
                    return talk
    return False

#dicts and so on
    
halls = { '1' : loc(30001), '2' : loc(30002), 'G' : loc(30003), '6' : loc(30004), 'S' : loc(30009) }
trans = { '0' : loc(30005), '1' : loc(30006) }

urls = { '1' : { '0' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s1_native.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s1_native_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s1_native_sd.m3u8'},
                '1' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s1_translated.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s1_translated_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s1_translated_sd.m3u8' }
            },
        '2' : { '0' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s2_native.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s2_native_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s2_native_sd.m3u8'},
                '1' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s2_translated.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s2_translated_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s2_translated_sd.m3u8' }
            },
        'G' : { '0' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s3_native.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s3_native_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s3_native_sd.m3u8'},
                '1' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s3_translated.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s3_translated_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s3_translated_sd.m3u8' }
            },
        '6' : { '0' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s4_native.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s4_native_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s4_native_sd.m3u8'},
                '1' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s4_translated.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s4_translated_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s4_translated_sd.m3u8' }
            },
        'S' : { '0' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s5_native.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s5_native_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s5_native_sd.m3u8'},
                '1' :
                    { '2' : 'http://hls.stream.c3voc.de/hls/s5_translated.m3u8',
                    '1' : 'http://hls.stream.c3voc.de/hls/s5_translated_hd.m3u8',
                    '0' : 'http://hls.stream.c3voc.de/hls/s5_translated_sd.m3u8' }
            },
    }
    

# display streams

for key, value in halls.iteritems():
    talk = find_current(fahrplan, 'Saal ' + key)
    if key == 'S' and translated == '1':
        translated = '0'
    if talk is not False:
        #log('Aktueller Talk in Saal ' + key + ': ' +  get_tag_info(talk, 'title') + '\tURL: ' + urls[key][translated][resolution])
        li = xbmcgui.ListItem(value + ' - ' + talk['title'], talk['subtitle'], iconImage='defaultvideo.png')
        #li.setProperty('TotalTime', '3600')
        #log(str(get_tag_info(talk, 'persons')))
        namesArr = []
        for person in talk['persons']:
            namesArr.append(person['full_public_name'])
        names = ' / '.join(namesArr)

        info = {'genre'         :       talk['track'],
                'year'          :       '2014',
                'director'      :       names,
                'writer'        :       names,
                'plot'          :       talk['description'],
                'plotoutline'   :       talk['abstract'],
                'title'         :       value + ' - ' + talk['title'],
                'mpaa'          :       'FSK 0',
                'duration'      :       talk['duration'] + ':00',
                'studio'        :       'c3voc',
                'tagline'       :       talk['subtitle'],
                'aired'         :       parse_datetime_string(talk['date']).strftime('%Y-%m-%d'),
                'credits'       :       names,
                'artist'        :       names
            }

###### Not in JSON
#        if talk.optout == 'true':
#            info['tagline'] += ' - ' + loc(30008)

#        if get_tag_info(talk, 'language') == 'de':
#            info['tagline'] += ' - Deutsch'
#        else:
#            info['tagline'] += ' - English'
        
        li.setInfo('video', info)
        li.setThumbnailImage('defaultvideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)
        xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
    else:
        #log('Aktueller Talk in Saal ' + key + ': ' +  'none' + '\tURL: ' + urls[key][translated][resolution])
        if value != 'Sendezentrum':
            li = xbmcgui.ListItem(value + ' - ' + loc(30007), iconImage='defaultvideo.png')
            li.setInfo('video', {'title' : value + ' - ' + loc(30007)})
        else:
            li = xbmcgui.ListItem(value, iconImage='defaultvideo.png')
            li.setInfo('video', {'title' : value})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=urls[key][translated][resolution], listitem=li)
        xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.endOfDirectory(addon_handle)
