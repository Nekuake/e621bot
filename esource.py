# -*- coding: utf-8 -*-

import re

from bot_util import json_get

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class ESource:
	def __init__(self, domain, api_user = None, api_pass = None):
		self.domain = domain
		self.api_user = api_user
		self.api_pass = api_pass

	def search(self, tags, limit = 50):
		if not re.search(ORDER_REGEX, tags):
			tags = tags + ' order:random'

		params = {
			'tags': tags,
			'limit': limit,
			'login': self.api_user,
			'password_hash': self.api_pass
		}

		images = []
		blobs = json_get('%s/post/index.json' % (self.domain), params)
		for blob in blobs:
			image = blob['sample_url']
			if image[0:2] == '//':
				image = 'http:' + image
			elif image[0:8] != 'https://' and image[0:7] != 'http://':
				image = 'http://' + image

			images.append({
				'image': image,
				'rating': blob['rating'],
				'post_url': '%s/post/view/%d' % (self.domain, blob['id'])
			})

		return images

	def __repr__(self):
		return 'ESource(domain = %s, api_user = %s, api_pass = %s)' % (self.domain, self.api_user, self.api_pass)
