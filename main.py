#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of Magpie OnlineJudge Project
Authors: DarcJC
"""

import tornado.ioloop
import tornado.web
import utils.url
from settings import URLS, PORT, SUBPROCESS_NUMBER

app = utils.url.RouterModified(URLS)

if __name__ == "__main__":
    server = tornado.web.HTTPServer(app)
    server.bind(PORT)
    server.start(SUBPROCESS_NUMBER)
    tornado.ioloop.IOLoop.current().start()
