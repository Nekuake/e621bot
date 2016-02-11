# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
from lxml import etree

def filter_null_values(orig):
	new = dict()

	for k in orig:
		v = orig[k]
		if v != None:
			new[k] = v

	return new

class HttpClient:
	def __init__(self):
		self.timeout = 30
		self.userAgent = None;

	def get(self, url, params = {}):
		params = filter_null_values(params)
		if params != {}:
			url = '%s?%s' % (url, urllib.parse.urlencode(params))

		headers = filter_null_values({
			'User-Agent': self.userAgent
		})

		request = urllib.request.Request(url, headers = headers)
		response = urllib.request.urlopen(request, timeout = self.timeout)
		return response.read()

	def getJSON(self, url, params = {}):
		return json.loads(self.get(url, params).decode('utf-8'))

	def getXML(self, url, params = {}):
		return etree.fromstring(self.get(url, params))
