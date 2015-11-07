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

def http_get(url, params = {}, timeout = 30):
	params = filter_null_values(params)
	if params != {}:
		url = '%s?%s' % (url, urllib.parse.urlencode(params))

	response = urllib.request.urlopen(url, timeout = timeout)
	return response.read()

def json_get(url, params = {}, timeout = 30):
	return json.loads(http_get(url, params).decode('utf-8'))

def xml_get(url, params = {}, timeout = 30):
	return etree.fromstring(http_get(url, params))
