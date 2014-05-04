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
