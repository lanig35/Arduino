#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, logging.handlers

def init_log (name, quiet):
	logger = logging.getLogger (name)
	logger.setLevel (logging.DEBUG)
	formatter = logging.Formatter (fmt='%(asctime)s;%(name)s;%(levelname)s;%(message)s',
								datefmt='%Y-%m-%d %H:%M:%S')
	
	file_name = 'log/' + name + '.log'	
	file_handler = logging.handlers.RotatingFileHandler (filename=file_name, mode='a',
														maxBytes=100000, backupCount=5,
														encoding='utf8', delay=False)
	file_handler.setLevel (logging.INFO)
	file_handler.setFormatter (formatter)
	logger.addHandler (file_handler)

	if quiet is False:
		stream_handler = logging.StreamHandler ()
		stream_handler.setLevel (logging.DEBUG)
		stream_handler.setFormatter (formatter)
		logger.addHandler (stream_handler)
		
	return logger
