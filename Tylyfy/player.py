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

import spotify
import logging
import random

class Player(object):
    def __init__(self, player, scrobbler=None):
        self.player = player
        self.logger = logging.getLogger(__name__)
        self.loop = False
        self.loop_one = False
        self.random = False
        self.playlist = []
        self.current = -1
        self.playing = False
        self.scrobbler = scrobbler

    def enqueue(self, tracks):
        if isinstance(tracks, spotify.Track):
            tracks = [ tracks ]
        self.playlist.extend(tracks)
        self.logger.debug("Current playlist: %s" % str(self.playlist))

    def clear(self):
        self.playlist = []
        self.current = -1
        self.logger.debug("Current playlist: %s" % str(self.playlist))

    def pause(self):
        self.player.pause()
        self.logger.debug("Paused")

    def play(self):
        if self.playing:
            self.logger.debug("Resumed")
            self.player.play()
        else:
            if self.current < len(self.playlist) and self.current >= 0:
                t = self.playlist[self.current]
                self.player.load(t)
                self.player.play()
                if self.scrobbler:
                    self.scrobbler.update_now_playing(t.album.artist.name, t.name, t.album.name, int(t.duration/1000))
                self.logger.debug("Playback started")

    def jump(self, n):
        n = n-1
        if n > 0 and n < len(self.playlist):
            if self.scrobbler:
                self.scrobbler.scrobble()
            self.player.unload()
            self.current = n
            t = self.playlist[self.current]
            self.player.load(t)
            self.player.play()
            if self.scrobbler:
                self.scrobbler.update_now_playing(t.album.artist.name, t.name, t.album.name, int(t.duration/1000))

    def next(self, force=False):
        if self.scrobbler:
            self.scrobbler.scrobble()
        self.player.unload()
        if force or not self.loop_one or self.current == -1:
            if self.random:
                old = self.current
                while old == self.current:
                    self.current = random.randrange(0, len(self.playlist))
            else:
                self.current += 1
        if self.current >= len(self.playlist):
            if self.loop:
                self.current = 0
            else:
                self.player.pause()
                self.playing = False
        if self.current < len(self.playlist):
            t = self.playlist[self.current]
            if not t.availability == spotify.TrackAvailability.AVAILABLE:
                return self.next(True)
            if self.scrobbler:
                self.scrobbler.update_now_playing(t.album.artist.name, t.name, t.album.name, int(t.duration/1000))
            self.player.load(t)
            self.player.play()
            self.playing = True
