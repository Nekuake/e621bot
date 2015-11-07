#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import re
import time
import threading

E621_USER = ''
E621_PASS = ''
apikey = '';

def json_get(url):
	response = urllib.request.urlopen(url, timeout = 300)
	content = response.read().decode('utf-8')
	data = json.loads(content)
	return data

def tg_request(url):
	reply = json_get(url)
	if not reply['ok']:
		raise ValueError('Telegram replied with an error')
	return reply['result']

def tg_status(key, start = 0):
	return tg_request('https://api.telegram.org/bot%s/getUpdates?offset=%d&timeout=300' % (key, start))

def tg_msg(key, chat, text, reply = None):
	params = {
		'chat_id': chat,
		'text': text,
		'reply_to_message_id': reply
	}
	tg_request('https://api.telegram.org/bot%s/sendMessage?%s' % (key, urllib.parse.urlencode(params)))

def e6_search(tags, lim = 1):
	params = {
		'tags': tags,
		'limit': lim,
		'login': E621_USER,
		'password_hash': E621_PASS
	}
	return json_get('https://e621.net/post/index.json?' + urllib.parse.urlencode(params))

def e6_post_string(post):
	ratings = {
		'e': 'explicit',
		'q': 'questionable',
		's': 'safe'
	}

	txt  = 'Image: %s\n' % (post['sample_url'])
	txt += 'Post: https://e621.net/post/view/%d\n' % (post['id'])
	txt += 'Rating: %s\n' % (ratings[post['rating']])
	return txt

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)
RATING_REGEX = re.compile(r'\brating:\w+\b', re.IGNORECASE)
FURRY_REGEX = re.compile(r'\/furry(?:@e621)?(?:\s+(.*))?', re.IGNORECASE)
YIFF_REGEX = re.compile(r'\/yiff(?:@e621)?(?:\s+(.*))?', re.IGNORECASE)
def parse_req(req):
	matches = re.match(FURRY_REGEX, req)
	defrating = ' rating:safe'
	if not matches:
		matches = re.match(YIFF_REGEX, req)
		defrating = ' -rating:safe'

	tags = None
	if matches:
		tags = matches.group(1)
		if not tags:
			tags = ''
		if not re.search(ORDER_REGEX, tags):
			tags = tags + ' order:random'
		if not re.search(RATING_REGEX, tags):
			tags = tags + defrating

	return tags

def exec_req(msg, tags):
	chatId = msg['message']['chat']['id']
	msgId = msg['message']['message_id']
	print("Searching %s" % (tags))

	images = []
	reply = 'Sorry, no images has been found by "%s"' % (tags)
	try:
		images = e6_search(tags)
	except Exception as e:
		print('Got an exception querying e621: ' + str(e))
		reply = 'Got an exception attempting to execute your query'

	if len(images) >= 1:
		reply = e6_post_string(images[0])

	while True:
		try:
			tg_msg(apikey, chatId, reply, msgId)
			break
		except Exception as e:
			print('Got an exception replying: ' + str(e))
			time.sleep(3)
	
reqstart = 0

while True:
	status = []
	try:
		status = tg_status(apikey, reqstart)
	except Exception as e:
		print('Got exception reading server status: ' + str(e))
		time.sleep(3)
		
	for msg in status:
		if 'text' in msg['message']:
			tags = parse_req(msg['message']['text'])

			if tags != None:
				threading.Thread(target = exec_req, args = (msg, tags)).start()

		reqstart = max(reqstart, msg['update_id'] + 1)
