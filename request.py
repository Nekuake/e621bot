# -*- coding: utf-8 -*-

import re

CMD_REGEX = re.compile(r'\/([a-z0-9]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?', re.IGNORECASE)

class Request:
	def __init__(self, bot, update):
		self.bot = bot

		if not 'text' in update['message']:
                        raise ValueError("No message in update")

		matches = re.match(CMD_REGEX, update['message']['text'])
		if not matches:
			raise ValueError("Not a command")

		botname = matches.group(2)
		if botname and botname.casefold() != bot.name.casefold():
			raise ValueError("Not for this bot")

		try:
			self.command = bot.commands[matches.group(1).casefold()]
		except KeyError:
			raise ValueError("Command not found")

		self.params = matches.group(3)
		if not self.params:
			self.params = ''

		self.date = update['message']['date']
		self.chat = update['message']['chat']
		self.author = update['message']['from']
		self.id = update['message']['message_id']

	def execute(self):
		self.command.execute(self)

	def reply(self, text):
		print("Reply %s\n" % (text))
		self.bot.send_message(self.chat['id'], text, self.id)
		return

		params = {
			'chat_id': chat,
			'text': text,
			'reply_to_message_id': replyTo
		}
		return self.request('sendMessage', params)
