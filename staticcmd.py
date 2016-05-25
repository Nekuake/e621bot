# -*- coding: utf-8 -*-

import random

class StaticCommand:
	def __init__(self, messages):
		if not isinstance(messages, list):
			messages = [ messages ]
		self.messages = messages

	def execute(self, request):
		request.reply(random.choice(self.messages))

	def __repr__(self):
		return 'StaticCommand(messages = %s)' % (self.messages)
