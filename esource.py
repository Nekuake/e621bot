# -*- coding: utf-8 -*-

import re
import time
from urllib.parse import urljoin

ORDER_REGEX = re.compile(r'\border:\w+\b', re.IGNORECASE)

class ESource:
	def __init__(self, domain, api_user=None, api_key=None, tagLimit=None):
		self.domain = domain
		self.api_user = api_user
		self.api_key = api_key
		self.tagLimit = tagLimit

	def prepare(self, request):
		if not re.search(ORDER_REGEX, request.params):
			request.params = request.params + ' order:random randseed:' + str(time.time())

	def _get_sample_img(self, post):
		if post['sample']['has'] == True:
			return post['sample']['url']
		return post['file']['url']

	def _check_reply(self, reply):
		if 'success' in reply:
			if reply['success'] == False:
				if 'message' in reply:
					raise Exception('Query did not succeed: ' + reply['message'])
				else:
					raise Exception('Query did not succeed')
		if 'posts' not in reply:
			raise Exception('Query succeeded but posts are missing!')

	def search(self, request, limit = 5):
		params = {
			'tags': request.params,
			'limit': limit,
		}
		if self.api_user is not None and self.api_key is not None:
			params.update({
				'login': self.api_user,
				'api_key': self.api_key
			})

		processed = []
		reply = request.bot.httpClient.getJSON('%s/posts.json' % (self.domain), params)
		self._check_reply(reply)

		for post in reply['posts']:
			image = self._get_sample_img(post)
			image = urljoin(self.domain, image)
			processed.append({
				'image': image,
				'rating': post['rating'],
				'post_url': '%s/posts/%d' % (self.domain, post['id'])
			})

		return processed

	def __repr__(self):
		return 'ESource(domain = %s, api_user = %s, api_pass = %s)' % (self.domain, self.api_user, self.api_pass)
