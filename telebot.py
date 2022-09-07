# -*- coding: utf-8 -*-

from httpclient import HttpClient
from request import Request, InvalidRequestException
from threading import Semaphore
import re
import time
import concurrent.futures
import socket
import requests.exceptions
import traceback
import logging
import datetime

CMD_REGEX = re.compile(r'\/([a-z0-9]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?', re.IGNORECASE)

class TeleBot:
	def __init__(self, apikey, name, commands, workers = 5):
		self.apikey = apikey
		self.name = name
		self.commands = commands
		self.lastUpdate = 0
		self.updateTimeout = 30

		self.workerPool = concurrent.futures.ThreadPoolExecutor(max_workers = workers)
		self.workerSemaphore = Semaphore(workers)

		self.httpClient = HttpClient()
		self.httpClient.userAgent = 'Telegram Bot (@%s)' % (name)
	def request(self, op, params, **kwargs):
		url = 'https://api.telegram.org/bot%s/%s' % (self.apikey, op)

		reply = self.httpClient.getJSON(url, params, **kwargs)
		if not reply['ok']:
			raise ValueError('Telegram replied with an error: %s' % repr(reply))

		return reply['result']

	def get_updates(self, start):
		params = {
			'offset': start,
			'timeout': self.updateTimeout
		}
		try:
			return self.request('getUpdates', params, timeout = self.updateTimeout)
		except requests.exceptions.Timeout:
			return []

	def send_message(self, chat, text, **kwargs):
		params = {
			'chat_id': chat,
			'text': text,
			'reply_to_message_id': kwargs.pop('reply_to', None),
			'parse_mode': kwargs.pop('markup', None)
		}
		return self.request('sendMessage', params)

	def handle_update(self, update):
		workerSemaphore = self.workerSemaphore
		logging.info(str(datetime.datetime.now()) + " REQUEST:" + update["message"]["from"]["username"] + update["message"]["text"])
		try:
			request = Request(self, update)
		except InvalidRequestException as e:
			logging.warning('Invalid request received: ' + str(e))
			return
		except Exception as e:
			logging.exception('Unexpected exception handling request')
			return

		def async_command(request):
			logging.info('Servicing %s' % (request.readable))

			try:
				request.execute()
			except Exception as e:
				logging.exception('Failed to run request handler')
				try:
					request.reply('Got an exception attempting to execute request: %s' % str(e))
				except:
					pass

		# Running it on callback ensures it will *always* free the semaphore no matter what the hell happens with the task
		def free_lock(future):
			workerSemaphore.release()

		workerSemaphore.acquire()
		future = self.workerPool.submit(async_command, request)
		future.add_done_callback(free_lock)

	def run_iteration(self):
		updates = []
		try:
			updates = self.get_updates(self.lastUpdate)
		except Exception as e:
			logging.exception('Got exception reading server status')
			time.sleep(3)

		for update in updates:
			self.handle_update(update)
			self.lastUpdate = max(self.lastUpdate, update['update_id'] + 1)

	def run_main(self):
		try:
			while True:
				self.run_iteration()
		except KeyboardInterrupt:
			pass

		logging.warning('Shutting down...')
		self.workerPool.shutdown()
