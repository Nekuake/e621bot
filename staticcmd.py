# -*- coding: utf-8 -*-

class StaticCommand:
	def __init__(self, message):
		self.message = message

	def execute(self, request):
		request.reply(self.message)

	def __repr__(self):
		return 'StaticCommand(message = %s)' % (self.message)
