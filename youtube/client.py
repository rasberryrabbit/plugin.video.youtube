# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import re
import time
import requests

__YOUTUBE_API_KEY__ = 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w'

class YouTubeClient(object):
    def __init__(self, username=None, password=None, language='en-US', maxResult=5, cachedToken=None, accessTokenExpiresAt=-1):
        self._opener = urllib2.build_opener()
        #opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)')]
        
        self._Username = username
        self._Password = password
        
        self.AccessToken = cachedToken
        self.AccessTokenExpiresAt = accessTokenExpiresAt
        
        self._HL = language
        _language = language.split('-')
        self._RegionCode = _language[1]
        
        self._API_Key = __YOUTUBE_API_KEY__
        self._MaxResult = maxResult
        pass
    
    def hasLogin(self):
        if not self._hasValidToken():
            self._updateToken()
            
        return self.AccessToken!=None
    
    def getUserToken(self):
        if self._Username==None or len(self._Username)==0:
            return {}
        
        if self._Password==None or len(self._Password)==0:
            return {}
        
        params = {'device_country': self._RegionCode.lower(),
                  'operatorCountry': self._RegionCode.lower(),
                  'lang': self._HL.replace('-', '_'),
                  'sdk_version': '19',
                  #'google_play_services_version': '5084034',
                  #'accountType' : 'HOSTED_OR_GOOGLE',
                  'Email': self._Username,
                  #'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie https://www.googleapis.com/auth/plus.stream.read https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/plus.pages.manage',
                  'service': 'oauth2:https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload',
                  'source': 'android',
                  #'androidId': '3b7ee32203b0465cb586551ee989b5ae',
                  'app': 'com.google.android.youtube',
                  #'callerPkg' : 'com.google.android.youtube',
                  'Passwd' : self._Password
                  }
    
        params = urllib.urlencode(params)
        
        result = {}
        
        try:
            url = 'https://android.clients.google.com/auth'
            request = urllib2.Request(url, data=params) 
            #request.add_header('device', '3b7ee32203b0465cb586551ee989b5ae')
            request.add_header('app', 'com.google.android.youtube')
            request.add_header('User-Agent', 'GoogleAuth/1.4 (GT-I9100 KTU84P) (GT-I9100 KTU84P)')
            request.add_header('content-type', 'application/x-www-form-urlencoded')
            request.add_header('Host', 'android.clients.google.com')
            request.add_header('Connection', 'Keep-Alive')
            #request.add_header('Accept-Encoding', 'gzip') 
            
            content = urllib2.urlopen(request)
            data = content.read()
            lines = data.split('\n')
            for line in lines:
                _property = line.split('=')
                if len(_property)>=2:
                    result[_property[0]] = _property[1]
        except:
            # do nothing
            pass
        
        self.AccessToken = result.get('Auth', None)
        
        return result
    
    def _createUrl(self, command, params={}):
        url = 'https://www.googleapis.com/youtube/v3/%s' % (command)
        
        _params = {}
        _params.update(params)
        _params['key'] = self._API_Key
        
        if _params!=None and len(_params)>0:
            return url + '?' + urllib.urlencode(_params)
        
        return url
    
    def _updateToken(self):
        authData = self.getUserToken()
        self.AccessToken = authData.get('Auth', None)
        self.AccessTokenExpiresAt = authData.get('Expiry', None)
        
    def _hasValidToken(self):
        isExpired = self.AccessTokenExpiresAt < time.time()
        if (self.AccessToken==None or len(self.AccessToken)==0 or isExpired):
            return False
        
        # and (self._Username!=None and self._Password!=None and len(self._Username)>0 and len(self._Password)>0):
        
        return True
    
    def _executeApi(self, command, params={}, jsonData=None, tries=1, method='GET'):
        if 'access_token' in params:
            if not self._hasValidToken():
                self._updateToken()
                params['access_token'] = self.AccessToken
        
        url = self._createUrl(command=command, params=params)
        
        try:
            if method=='GET':
                content = requests.get(url, verify=False)
                return json.loads(content.text)
            elif method=='POST':
                headers = {'content-type': 'application/json',
                           'Authorization': 'Bearer %s' % (self.AccessToken)}
                content = requests.post(url, data=json.dumps(jsonData), headers=headers, verify=False)
                pass
        except:
            if tries>=1:
                tries = tries-1
                return self._executeApi(command, params, tries, method)
        
            return {}
        pass
    
    def _makeCommaSeparatedList(self, values=[]):
        result = ''
        
        for value in values:
            result = result+value
            result = result+','
        if len(result)>0:
            result = result[:-1]
        
        return result;
    
    def getVideosInfo(self, videoIds=[]):
        result = {}
        
        if len(videoIds)==0:
            return result
        
        videos = self.getVideos(videoIds)
        videos = videos.get('items', [])
        for video in videos:
            _id = video.get('id', None)
            contentDetails = video.get('contentDetails', {})
            duration = contentDetails.get('duration', None)
            if id!=None and duration!=None:
                durationMatch = re.compile('PT((\d)*H)*((\d*)M)+((\d*)S)+').findall(duration)
                
                minutes = 1
                if durationMatch!=None and len(durationMatch)>0:
                    minutes = 1
                    if len(durationMatch[0])>=2 and durationMatch[0][3]!='':
                        minutes = int(durationMatch[0][3])
                        
                    if len(durationMatch[0])>=1 and durationMatch[0][1]!='':
                        minutes = minutes+ int(durationMatch[0][1])*60
                    pass
                
                duration = str(minutes)
                result[_id] = {'duration': duration}
                pass
            pass
        
        return result
    
    def getVideos(self, videoIds=[]):
        params = {'part': 'contentDetails',
                  'id': self._makeCommaSeparatedList(videoIds)}
        #'access_token': self.AccessToken}
        return self._executeApi('videos', params)
    
    def _sortItems(self, item):
        snippet = item.get('snippet', {})
        publishedAt = snippet.get('publishedAt', '') 
        return publishedAt
    
    def getSubscriptions(self, mine=None, order='alphabetical', nextPageToken=None):
        params = {'part': 'snippet',
                  'order': order,
                  'maxResults': self._MaxResult}
        
        if mine!=None and mine==True:
            params['access_token'] = self.AccessToken
            params['mine'] = 'true'
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
        
        return self._executeApi('subscriptions', params)
    
    def getGuideCategories(self):
        params = {'part': 'snippet',
                  'regionCode': self._RegionCode,
                  'hl': self._HL}
        return self._executeApi('guideCategories', params)
    
    def getChannelCategory(self, categoryId, nextPageToken=None):
        params = {'part': 'snippet,contentDetails',
                  'categoryId': categoryId,
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('channels', params)
    
    def getPlaylists(self, channelId=None, mine=None, nextPageToken=None):
        params = {'part': 'snippet',
                  'maxResults': self._MaxResult}
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
            
        if channelId!=None:
            params['channelId'] = channelId
        elif mine!=None and mine==True:
            params['access_token'] = self.AccessToken
            params['mine'] = 'true'

        return self._executeApi('playlists', params)
    
    def getPlaylistItems(self, playlistId, mine=False, nextPageToken=None):
        params = {'part': 'snippet',
                  'playlistId': playlistId,
                  'maxResults': self._MaxResult}
        
        if mine==True:
            params['access_token'] = self.AccessToken
            
        
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('playlistItems', params)
    
    def addPlayListItem(self, playlistId, videoId):
        params = {'part': 'snippet',
                  'mine': 'true',
                  'access_token': self.AccessToken}
        
        jsonData = {'kind': 'youtube#playlistItem',
                    'snippet':{'playlistId': playlistId,
                               'resourceId': {'kind': 'youtube#video',
                                              'videoId': videoId}
                               }
                    }
        
        result = self._executeApi('playlistItems', params=params, jsonData=jsonData, method='POST')
        pass
    
    def getActivities(self, channelId=None, home=None, mine=None, nextPageToken=None):
        #publishedAfter = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        
        params = {'part': 'snippet,contentDetails',
                  'maxResults': self._MaxResult,
                  #'regionCode': self._RegionCode,
                  #'publishedBefore': publishedAfter
                  }
        
        if channelId!=None:
            params['channelId'] = channelId
        elif home!=None and home==True:
            params['home'] = 'true'
            params['access_token'] = self.AccessToken
        elif mine!=None and mine==True:
            params['mine'] = 'true'
            params['access_token'] = self.AccessToken
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken
        
        jsonData = self._executeApi('activities', params)
        sortedItems = sorted(jsonData.get('items', []), key=self._sortItems, reverse=True)
        jsonData['items'] = sortedItems
        return jsonData
    
    def getChannels(self, channelId=None, mine=None, nextPageToken=None):
        params = {'part': 'snippet,contentDetails,brandingSettings'}
        
        if channelId!=None:
            params['id'] = channelId
            
        if mine!=None and mine==True:
            params['mine'] = 'true'
            params['access_token'] = self.AccessToken
            
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('channels', params)
    
    def search(self, text, searchVideos=None, searchChannels=None, searchPlaylists=None, nextPageToken=None):
        params = {'q': text,
                  'part': 'snippet',
                  'maxResults': self._MaxResult}
        
        types = []
        if searchVideos!=None and searchVideos==True:
            types.append('video')
        if searchChannels!=None and searchChannels==True:
            types.append('channel')
        if searchPlaylists!=None and searchPlaylists==True:
            types.append('playlist')
        if len(types)>0:
            params['type'] = self._makeCommaSeparatedList(types)
        
        if nextPageToken!=None:
            params['pageToken'] = nextPageToken

        return self._executeApi('search', params)