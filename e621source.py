# -*- coding: utf-8 -*-

import re

from bot_util import json_get

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class e621Source:
	def __init__(self, api_user = None, api_pass = None):
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
		blobs = json_get('https://e621.net/post/index.json', params)
		for blob in blobs:
			images.append({
				'image': blob['sample_url'],
				'rating': blob['rating'],
				'post_url': 'https://e621.net/post/view/%d' % (blob['id'])
			})

		return images
