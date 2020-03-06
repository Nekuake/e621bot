# -*- coding: utf-8 -*-

from threading import Lock
from cachetools import LRUCache

class ListLRUCache(LRUCache):
	def __missing__(self, key):
		return list()

class BooruCommand:
	def __init__(self, engine, cache_size=1024, images_per_search=16):
		self.engine = engine
		self.cache = ListLRUCache(maxsize=cache_size)
		self.cache_lock = Lock()
		self.images_per_search = images_per_search

	def rating(self, rating):
		if rating == 's':
			return 'safe'
		if rating == 'q':
			return 'questionable'
		if rating == 'e':
			return 'explicit'
		return 'unknown (%s)' % (rating)

	def get_image(self, request):
		# First try fetching one from cache
		with self.cache_lock:
			try:
				return self.cache[request.params].pop()
			except:
				pass

		# If it fails, fetch one from the engine
		found_images = self.engine.search(request, self.images_per_search)
		if len(found_images) == 0:
			return None

		image = found_images.pop()
		if len(found_images) > 0:
			with self.cache_lock:
				self.cache[request.params].extend(found_images)

		return image

	def execute(self, request):
		self.engine.prepare(request)

		# Normalize requests to lower case and sort alphabetically
		tags = request.params.lower().split()
		tags.sort()
		request.params = ' '.join(tags)

		if self.engine.tagLimit and len(tags) > self.engine.tagLimit:
			request.reply('Sorry, this command has a limit of %d tags, and therefore "%s" can\'t be processed.' % (self.engine.tagLimit, request.params))
			return

		image = self.get_image(request)
		if image:
			txt  = '[Image](%s) - ' % (image['image'])
			txt += '[Post](%s) - ' % (image['post_url'])
			txt += '*%s*' % (self.rating(image['rating']))
			request.reply(txt, 'Markdown')
		else:
			request.reply('Sorry, no images found by "%s"' % (request.params))

	def __repr__(self):
		return 'BooruCommand(engine = %s)' % (self.engine)
