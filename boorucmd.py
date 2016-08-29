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

		if self.engine.tagLimit and len(tags) > self.engine.tagLimit:
			request.reply('Sorry, this command has a limit of %d tags, and therefore "%s" can\' be processed.' % (self.engine.tagLimit, request.params))
			return

		images = self.engine.search(request, 1)

		if images:
			txt  = '[Image](%s) - ' % (images[0]['image'])
			txt += '[Post](%s) - ' % (images[0]['post_url'])
			txt += '*%s*' % (self.rating(images[0]['rating']))
			request.reply(txt, 'Markdown')
		else:
			request.reply('Sorry, no images has been found by "%s"' % (request.params))

	def __repr__(self):
		return 'BooruCommand(engine = %s)' % (self.engine)
