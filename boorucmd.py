# -*- coding: utf-8 -*-

class BooruCommand:
	def __init__(self, engine):
		self.engine = engine

	def rating(self, rating):
		if rating == 's':
			return 'safe'
		if rating == 'q':
			return 'questionable'
		if rating == 'e':
			return 'explicit'
		return 'unknown (%s)' % (rating)

	def execute(self, request):
		images = self.engine.search(request, 1)

		if images:
			txt  = 'Image: %s\n' % (images[0]['image'])
			txt += 'Post: %s\n' % (images[0]['post_url'])
			txt += 'Rating: %s\n' % (self.rating(images[0]['rating']))
			return txt

		return 'Sorry, no images has been found by "%s"' % (request)
