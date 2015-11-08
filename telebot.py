# -*- coding: utf-8 -*-

from bot_util import json_get
import re
import time

CMD_REGEX = re.compile(r'\/([a-z]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?', re.IGNORECASE)

class TeleBot:
	def __init__(self, apikey, name, commands):
		self.apikey = apikey
		self.name = name
		self.commands = commands
		self.lastUpdate = 0

	def request(self, op, params, timeout = 10):
		url = 'https://api.telegram.org/bot%s/%s' % (self.apikey, op)

		reply = json_get(url, params, timeout)
		if not reply['ok']:
			raise ValueError('Telegram replied with an error')

		return reply['result']

	def get_updates(self, start, timeout = 300):
		params = {
			'offset': start,
			'timeout': timeout
		}
		return self.request('getUpdates', params, timeout)

	def send_message(self, chat, text, replyTo = None):
		params = {
			'chat_id': chat,
			'text': text,
			'reply_to_message_id': replyTo
		}
		return self.request('sendMessage', params)

	def execute_command(self, chat, command, params, replyTo = None):
		try:
			reply = command.execute(params)
		except Exception as e:
			reply = 'Got an exception attempting to serve your request: %s' % (str(e))

		self.send_message(chat, reply, replyTo)

	def parse_message(self, message):
		matches = re.match(CMD_REGEX, message)
		if not matches:
			return None

		botname = matches.group(2)
		if botname and botname.casefold() != self.name.casefold():
			return None

		try:
			command = self.commands[matches.group(1).casefold()]
		except KeyError:
			return

		params = matches.group(3)
		if not params:
			params = ''

		return {
			'command': command,
			'params': params
		}

	def handle_update(self, update):
		if not 'text' in update['message']:
			return

		info = self.parse_message(update['message']['text'])
		if not info:
			return

		print('Servicing %s' % (repr(info)))
		try:
			self.execute_command(
					update['message']['chat']['id'],
					info['command'],
					info['params'],
					update['message']['message_id']
			)
		except Exception as e:
			print('Got an exception attempting to execute request: %s' % (repr(e)))

	def run_iteration(self):
		updates = []
		try:
			updates = self.get_updates(self.lastUpdate)
		except Exception as e:
			print('Got exception reading server status: ' + str(e))
			time.sleep(3)

		for update in updates:
			self.handle_update(update)
			self.lastUpdate = max(self.lastUpdate, update['update_id'] + 1)

	def run_main(self):
		while True:
			self.run_iteration()
