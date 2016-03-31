# -*- coding: utf-8 -*-

import re
import random
import math

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class GelbooruSource:
	def __init__(self, domain):
		self.domain = domain
		self.tagLimit = None

	def prepare(self, request):
		return

	def search(self, request, limit = 1):
		# simulate order:random by choosing a random page
		if not re.search(ORDER_REGEX, request.params):
			params = {
				'page': 'dapi',
				's': 'post',
				'q': 'index',
				'limit': 0,
				'tags': request.params
			}

			req = request.bot.httpClient.getXML('%s/index.php' % (self.domain), params)
			count = int(req.get('count'))
			if count == 0:
				return []

			page = random.randint(0, math.trunc(count / limit))
		else:
			page = 0

		params = {
			'page': 'dapi',
			's': 'post',
			'q': 'index',
			'limit': limit,
			'tags': request.params,
			'pid': page
		}
		blobs = request.bot.httpClient.getXML('%s/index.php' % (self.domain), params)

		images = []
		for blob in blobs:
			images.append({
				'image': blob.get('sample_url'),
				'rating': blob.get('rating'),
				'post_url': '%s/index.php?page=post&s=view&id=%s' % (self.domain, blob.get('id'))
			})
		return images

	def __repr__(self):
		return 'GelbooruSource(domain = %s)' % (self.domain)
