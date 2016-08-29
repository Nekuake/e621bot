#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telebot import TeleBot
from esource import ESource
from boorucmd import BooruCommand
from staticcmd import StaticCommand
from gbsource import GelbooruSource

bot = TeleBot(
	'YOUR TELEGRAM API KEY',
	'YOUR TELEGRAM BOT NAME/PREFIX',
	{
		'yiff': BooruCommand(ESource('https://e621.net')),
		'furry': BooruCommand(ESource('https://e926.net')),
		'r34': BooruCommand(GelbooruSource('http://rule34.xxx')),
		'gb': StaticCommand('This command is WIP')
	}
)

bot.run_main()
