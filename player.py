import spotify
import logging

class Player(object):
    def __init__(self, player):
        self.player = player
        self.logger = logging.getLogger(__name__)
        self.loop = False
        self.playlist = []
        self.current = -1
        self.playing = False

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
                self.player.load(self.playlist[self.current])
                self.player.play()
                self.logger.debug("Playback started")

    def next(self):
        self.player.unload()
        self.current += 1
        if self.current >= len(self.playlist):
            if self.loop:
                self.current = 0
            else:
                self.player.pause()
                self.player.unload()
                self.playing = False
        if self.current < len(self.playlist):
            t = self.playlist[self.current]
            self.player.load(t)
            self.player.play()
            self.playing = True
