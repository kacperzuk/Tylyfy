# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, Kacper Żuk
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.  2. Redistributions in
# binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

try:
    import pylast
except ImportError:
    working = False
else:
    working = True

import logging
import time
from Tylyfy.colors import *

class Scrobbler(object):
    def __init__(self, api_key, secret_key, login, password):
        try:
            self.network = pylast.LastFMNetwork(api_key=api_key, api_secret=secret_key, username=login, password_hash=password)
            self.enabled = True
        except pylast.WSError:
            print(ERROR+"Last.FM custom scrobbler error: invalid api_key, username or password hash"+RESET)
            self.enabled = False
        self.now_playing = None
        self.logger = logging.getLogger(__name__)

    def update_now_playing(self, artist, title, album, duration):
        if not self.enabled:
            return
        self.logger.info("now_playing notify sent")
        self.now_playing = [artist, title, album, duration, int(time.time())]
        self.network.update_now_playing(artist, title, album, duration=int(duration))

    def scrobble(self):
        if not self.enabled:
            return
        if self.now_playing:
            self.logger.info("scrobbling track")
            t = self.now_playing
            self.network.scrobble(t[0], t[1], t[4], t[2], duration=int(t[3]))
