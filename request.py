# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import re

CMD_REGEX = re.compile(r'\/([a-z0-9]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?', re.IGNORECASE)


class InvalidRequestException(Exception):
    pass


class Request:
    def __init__(self, bot, update):
        self.bot = bot

        if not 'text' in update['message']:
            raise InvalidRequestException("No message in update")

        matches = re.match(CMD_REGEX, update['message']['text'])
        if not matches:
            raise InvalidRequestException("Not a command")

        botname = matches.group(2)
        if botname and botname.casefold() != bot.name.casefold():
            raise InvalidRequestException("Not for this bot")

        try:
            self.commandName = matches.group(1).casefold()
            self.command = bot.commands[self.commandName]
        except KeyError:
            raise InvalidRequestException("Command not found")

        self.params = matches.group(3)
        if not self.params:
            self.params = ''

        self.date = update['message']['date']
        self.chat = update['message']['chat']
        self.author = update['message']['from']
        self.id = update['message']['message_id']

    def execute(self):
        self.command.execute(self)

    def reply(self, text, markup=None):
        self.bot.send_message(self.chat['id'], text, reply_to=self.id, markup=markup)

    @property
    def readable(self):
        return "/%s %s" % (self.commandName, self.params)
