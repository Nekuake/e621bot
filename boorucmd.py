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
		self.engine.prepare(request)

		# Normalize requests to lower case and sort alphabetically
		tags = request.params.lower().split()
		tags.sort()
		request.params = ' '.join(tags)

		images = self.engine.search(request, 1)

		if images:
			txt  = 'Image: %s\n' % (images[0]['image'])
			txt += 'Post: %s\n' % (images[0]['post_url'])
			txt += 'Rating: %s\n' % (self.rating(images[0]['rating']))
			request.reply(txt)
		else:
			request.reply('Sorry, no images has been found by "%s"' % (request))

	def __repr__(self):
		return 'BooruCommand(engine = %s)' % (self.engine)
