#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rpyc
from rpyc.utils.server import ThreadedServer

server = ThreadedServer(rpyc.SlaveService, port=18888)
server.start()
