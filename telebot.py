# -*- coding: utf-8 -*-

from bot_util import json_get
from request import Request
import re
import time
import concurrent.futures;
import socket

CMD_REGEX = re.compile(r'\/([a-z0-9]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?', re.IGNORECASE)

class TeleBot:
	def __init__(self, apikey, name, commands, workers = 5):
		self.apikey = apikey
		self.name = name
		self.commands = commands
		self.lastUpdate = 0

		if workers:
			self.workerPool = concurrent.futures.ThreadPoolExecutor(max_workers = workers)
		else:
			self.workerPool = None

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
		try:
			return self.request('getUpdates', params, timeout)
		except socket.timeout:
			return []

	def send_message(self, chat, text, replyTo = None):
		params = {
			'chat_id': chat,
			'text': text,
			'reply_to_message_id': replyTo
		}
		return self.request('sendMessage', params)

	def handle_update(self, update):
		try:
			request = Request(self, update)
		except Exception as e:
			print('Could not parse request: %s' % (repr(e)))
			return

		def async_command(request):
			print('Servicing %s' % (repr(request)))

			try:
				request.execute()
			except Exception as e:
				request.reply('Got an exception attempting to execute request: %s' % (repr(e)))


		if self.workerPool:
			self.workerPool.submit(async_command, request)
		else:
			async_command(request)

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
