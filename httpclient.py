# -*- coding: utf-8 -*-

import requests
import json
from lxml import etree

class HttpClient:
	def __init__(self):
		self.timeout = 5
		self.userAgent = None;

	def request(self, url, params = {}, **kwargs):
		if 'timeout' not in kwargs:
			kwargs['timeout'] = self.timeout
		if 'headers' not in kwargs:
			kwargs['headers'] = {}

		kwargs['headers'].update({
			'User-Agent': self.userAgent
		})

		return requests.get(url, params, **kwargs)

	def getJSON(self, *args, **kwargs):
		return self.request(*args, **kwargs).json()

	def getXML(self, *args, **kwargs):
		# TODO: figure out how to use stream
		return etree.XML(self.request(*args, **kwargs).content)
