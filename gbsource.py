# -*- coding: utf-8 -*-

import re
import random
import math

from bot_util import xml_get

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class GelbooruSource:
	def __init__(self, domain):
		self.domain = domain

	def prepare(self, tags):
		return tags

	def search(self, tags, limit = 1):
		# simulate order:random by choosing a random page
		if not re.search(ORDER_REGEX, tags):
			params = {
				'page': 'dapi',
				's': 'post',
				'q': 'index',
				'limit': 0,
				'tags': tags
			}

			req = xml_get('%s/index.php' % (self.domain), params)
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
			'tags': tags,
			'pid': page
		}
		blobs = xml_get('%s/index.php' % (self.domain), params)

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
