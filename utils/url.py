# -*- coding: utf-8 -*-

"""
This file is part of Magpie OnlineJudge Project
Authors: DarcJC
"""

from functools import wraps
import tornado.web


class RouterModified(tornado.web.Application):
    """
    Modify the router to use decorator to set url
    """
    def route(self, url):
        def register(handler):
            self.add_handlers(".*$", [(url, handler)])
            return handler
        return register
