#!/usr/bin/env python

import requests, json, sys, re
from pathlib import Path
home = str(Path.home())
import youtube_dl
import os, errno
import pprint
from slugify import slugify

def main():
  arg = sys.argv
  if len(arg) < 2:
    print ('usage:')
    print ('  %s username' % __file__)
    print ('  %s vodID\n' % __file__)
    sys.exit(1)
  else:
    if arg[1] == "latest" and arg[2].isalpha():
      #metro = getMetro(getLatestVideo(arg[2]))
      #print('https://vod-metro.twitch.tv/{}/chunked/index-dvr.m3u8 - {}'.format(metro,
      #    getLatestTitle(arg[2])))
        logYoutubeDL(YoutubeDL_Latest(arg[2])['entries'][0])
    elif arg[1].isdigit():
      #metro = getMetro(arg[1])
      #print('https://vod-metro.twitch.tv/{}/chunked/index-dvr.m3u8'.format(metro))
      #writeLog('https://vod-metro.twitch.tv/{}/chunked/index-dvr.m3u8'.format(metro))
        logYoutubeDL(YoutubeDL_ID(arg[1]))
    elif arg[1].isalpha():
        logYoutubeDL(YoutubeDL_Live(arg[1]))


def YoutubeDL_Latest(name):
    ydl_opts = { 'skip_download': True, 'playlist_items': '1' }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.twitch.tv/{name}/videos', download=False)
        return result

def YoutubeDL_Live(name):
    ydl_opts = { 'skip_download': True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.twitch.tv/{name}', download=False)
        print(result)
        return result


def YoutubeDL_ID(vod_id):
    ydl_opts = { 'skip_download': True }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.twitch.tv/videos/{vod_id}', download=False)
        return result


def logYoutubeDL(json):
    folder = f'{home}/Dev/VODIndex/vods/{json["uploader_id"]}'
    pretty_output = pprint.pformat(json)
    if 'duration' in json:
        filename = f'{json["title"]} - {json["id"]} - {json["duration"]}s.log'
    else:
        filename = f'{json["title"]} - {json["id"]}s.log'
    filename = filename.replace('/', '-')
    print(filename)
    try:
        os.makedirs(folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(f'{folder}/{filename}', 'w') as file:
        file.write(pretty_output)
    print(f'Done logging {json["title"]}')
    print(f'm3u8: {json["url"]}')
    print(f'VOD Url: {json["webpage_url"]}')

def getAllVideosJSON(streamer):
  header = {
    "Host": "gql.twitch.tv",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Accept": "*/*",
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip, deflate, br",
    #"Referer": "https://www.twitch.tv/destiny/videos?filter=archives&sort=time",
    "Client-Id": "",
    "X-Device-Id": "089be54175fb54da",
    "Authorization": "OAuth ",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.twitch.tv",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
  }

  payload = [{
    "operationName": "FilterableVideoTower_Videos",
    "variables": {
      "limit": 30,
      "channelOwnerLogin": streamer,
      "broadcastType": "ARCHIVE",
      "videoSort": "TIME"
    },
    "extensions": {
      "persistedQuery": {
        "version": 1,
        "sha256Hash": ""
      }
    }
  }]

  r = requests.post('https://gql.twitch.tv/gql', data=json.dumps(payload), headers=header)
  rj = r.json()
  print(rj)

  return rj[0]['data']['user']['videos']['edges']

def getAllVideos(streamer):
  for elem in getAllVideosJSON(streamer):
    print(elem['node']['id'], '-', elem['node']['owner']['displayName'], '-', elem['node']['title'])

def getLatestVideo(streamer):
  vodIDs = getAllVideosJSON(streamer)[0]

  print('{}\'s latest VOD is: {} - {}'.format(vodIDs['node']['owner']['displayName'], vodIDs['node']['id'], vodIDs['node']['title']))
  return vodIDs['node']['id']

def getLatestTitle(streamer):
  vodIDs = getAllVideosJSON(streamer)[0]

  return ('{} - {} - {}'.format(vodIDs['node']['owner']['displayName'], vodIDs['node']['id'], vodIDs['node']['title']))

def writeLog(text):
  with open(home + '/Dev/VODIndex/output.log', 'a') as file:
    file.write(text + "\n")

def getMetro(video):
  from seleniumwire import webdriver
  from selenium.webdriver.firefox.options import Options as FirefoxOptions

  options = FirefoxOptions()
  options.add_argument("--headless")
  driver = webdriver.Firefox(options=options)

  print("Headless Firefox Initialized")
  print('Looking for {}\'s metro'.format(video))
  driver.get("https://www.twitch.tv/videos/" + video)

  driver.scopes = [
      '.*vod-secure.twitch.tv.*',
      '.*cloudfront.net.*'
  ]


  for request in driver.requests:
      if request.response:
        if "/chunked/index-dvr.m3u8" in request.path:
          driver.quit()
          print('Found index-dvr')
          return re.search('/(.*)\/chunked', request.path).group(1)
        if "-info.json" in request.path:
          driver.quit()
          print('Found info.json')
          return re.search('.net\/(.*)\/storyboards', request.path).group(1)
          



if __name__ == '__main__':
    main()
