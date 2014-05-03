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
                self.scrobbler.update_now_playing(t.album.artist.name, t.name, t.album.name, int(t.duration/1000))
                self.logger.debug("Playback started")

    def jump(self, n):
        n = n-1
        if n > 0 and n < len(self.playlist):
            self.scrobbler.scrobble()
            self.player.unload()
            self.current = n
            t = self.playlist[self.current]
            self.player.load(t)
            self.player.play()
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
            if self.scrobbler:
                self.scrobbler.update_now_playing(t.album.artist.name, t.name, t.album.name, int(t.duration/1000))
            self.player.load(t)
            self.player.play()
            self.playing = True
