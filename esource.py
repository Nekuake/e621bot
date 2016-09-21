# -*- coding: utf-8 -*-

import re
from urllib.parse import urljoin

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class ESource:
	def __init__(self, domain, api_user = None, api_pass = None, tagLimit = None):
		self.domain = domain
		self.api_user = api_user
		self.api_pass = api_pass
		self.tagLimit = tagLimit

	def prepare(self, request):
		if not re.search(ORDER_REGEX, request.params):
			request.params = request.params + ' order:random'

	def search(self, request, limit = 50):
		params = {
			'tags': request.params,
			'limit': limit,
			'login': self.api_user,
			'password_hash': self.api_pass
		}

		images = []
		blobs = request.bot.httpClient.getJSON('%s/post/index.json' % (self.domain), params)
		for blob in blobs:
			image = urljoin(self.domain, blob['sample_url'])
			images.append({
				'image': image,
				'rating': blob['rating'],
				'post_url': '%s/post/show/%d' % (self.domain, blob['id'])
			})

		return images

	def __repr__(self):
		return 'ESource(domain = %s, api_user = %s, api_pass = %s)' % (self.domain, self.api_user, self.api_pass)
