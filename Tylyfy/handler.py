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

from Tylyfy import settings
from Tylyfy import player
from Tylyfy import scrobble
import logging
import threading
import spotify
import os
import textwrap
import sys
from Tylyfy.colors import *
from Tylyfy.tracks import Tracks

def require_login(f):
    def wrapper(*args):
        if args[0].events.connected.is_set():
            f(*args)
            return True
        else:
            print(ERROR+"You must login first!"+RESET)
            return False
    return wrapper

class Events(object):
    def __init__(self, settings):
        self.settings = settings
        self.connected = threading.Event()
        self.blob_updated = threading.Event()
        self.blob_data = ""
        self.logged_out_event = threading.Event()
        self.login_event = threading.Event()
        self.bad_login = threading.Event()
        self.logger = logging.getLogger("Events")

    def connection_state_updated(self, session):
        if session.connection.state == spotify.ConnectionState.LOGGED_IN:
            self.connected.set()
            self.logged_out_event.clear()

            session.social.set_scrobbling(spotify.SocialProvider.SPOTIFY, spotify.ScrobblingState.LOCAL_ENABLED)
            session.social.set_scrobbling(spotify.SocialProvider.FACEBOOK, spotify.ScrobblingState.LOCAL_ENABLED)
            if not self.settings.get("lastfm", "custom_scrobbler", "True") == "True":
                lastfm_user = self.settings.get("lastfm", "username", False)
                if lastfm_user:
                    session.social.set_social_credentials(spotify.SocialProvider.LASTFM, lastfm_user, self.settings.get("lastfm", "password", ""))
                session.social.set_scrobbling(spotify.SocialProvider.LASTFM, spotify.ScrobblingState.LOCAL_ENABLED)
            else:
                session.social.set_scrobbling(spotify.SocialProvider.LASTFM, spotify.ScrobblingState.LOCAL_DISABLED)
            self.logger.debug("Scrobblers enabled")

    def logged_in(self, session, error):
        if error == spotify.ErrorType.BAD_USERNAME_OR_PASSWORD:
            self.bad_login.set()
        self.login_event.set()

    def message_to_user(self, session, data):
        print("%sLibspotify message: %s%s" % (INFO, data, RESET))

    def logged_out(self, session):
        self.connected.clear()
        self.logged_out_event.set()

    def credentials_blob_updated(self, session, blob):
        self.blob_data = blob
        self.blob_updated.set()

    def scrobble_error(self, session, error):
        print("%sScrobble error: %s%s" % (ERROR, str(error), RESET))

class Handler(object):
    def __init__(self):
        self.settings = settings.Settings()
        self.logger = self.setupLogging()
        self.events = Events(self.settings)
        self.spotify_session = self.setupSpotify()
        self.scrobbler = None
        if self.settings.get("lastfm", "custom_scrobbler", "True") == "True":
            if scrobble.working:
                self.scrobbler = scrobble.Scrobbler(
                        self.settings.get("lastfm", "api_key", ""),
                        self.settings.get("lastfm", "secret_key", ""),
                        self.settings.get("lastfm", "username", ""),
                        self.settings.get("lastfm", "password_md5", ""))
            else:
                print(ERROR+"pylast is missing, disabling LastFM scrobbling"+RESET)
        self.player = player.Player(self.spotify_session.player, self.scrobbler)
        self.last_search = None

    def setupLogging(self):
        levels = {'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL}

        core_loglevel = self.settings.get('core', 'loglevel', 'warning')
        spotify_loglevel = self.settings.get('spotify', 'loglevel', 'warning')

        logging.basicConfig(level=levels[core_loglevel])
        logging.getLogger('spotify').setLevel(levels[spotify_loglevel])
        logger =  logging.getLogger(__name__)
        logger.debug("Logging initialized")
        return logger

    def setupSpotify(self):
        username = self.settings.get('spotify', 'username', None)
        blob = self.settings.get('spotify', 'blob', None)

        config = spotify.Config()
        config.user_agent = 'Tylyfy - CLI Player'
        config.tracefile = b'/tmp/tylyfy.trace.log'
        config.cache_location = os.path.join(os.path.expanduser(b'~'), b'.config', b'tylyfy', b'spotify')
        config.settings_location = os.path.join(os.path.expanduser(b'~'), b'.config', b'tylyfy', b'spotify')
        try:
            config.load_application_key_file(os.path.join(os.path.expanduser("~"), ".config", "tylyfy", "spotify_appkey.key"))
        except:
            print(ERROR+"\nMissing spotify_appkey.key!"+RESET)
            print(textwrap.dedent("""
                To start Tylyfy you need to obtain a Spotify API key. You can get it from:
                https://devaccount.spotify.com/my-account/keys/. Download the Binary version,
                save it to ~/.config/tylyfy/spotify_appkey.key and try again.
                """))
            sys.exit(1)

        session = spotify.Session(config=config)
        if str(self.settings.get('core', 'custom_sink', "False")) == "False":
            try:
                spotify.PortAudioSink(session)
            except:
                try:
                    spotify.AlsaSink(session)
                except:
                    raise Exception("No pyAlsaAudio nor pyAudio found, bailing out...")
        else:
            from Tylyfy import sink
            print(INFO+"Enabling custom sink. If you get choppy sound or too long lag, change pillow_size in ~/.config/tylyfy/settings.ini."+RESET)
            sink.Sink(session, int(self.settings.get("core", "pillo_size", "8")))
            self.settings.sync()
        self.loop = spotify.EventLoop(session)
        self.loop.start()
        session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, self.events.connection_state_updated)
        session.on(spotify.SessionEvent.CREDENTIALS_BLOB_UPDATED, self.events.credentials_blob_updated)
        session.on(spotify.SessionEvent.LOGGED_OUT, self.events.logged_out)
        session.on(spotify.SessionEvent.LOGGED_IN, self.events.logged_in)
        session.on(spotify.SessionEvent.SCROBBLE_ERROR, self.events.scrobble_error)
        session.on(spotify.SessionEvent.MESSAGE_TO_USER, self.events.message_to_user)
        session.on(spotify.SessionEvent.END_OF_TRACK, self.endOfTrack)

        if username:
            print("%sLogged in as: %s%s" % (INFO, username, RESET))
            session.login(username, blob=blob)
            self.events.connected.wait()
            self.logger.debug('Login and connection successful')
        else:
            print(NOTICE+"Remember to login"+RESET)
        return session

    def login(self, username, password):
        self.spotify_session.login(username, password)
        print(WAIT_MESSAGE+"Logging in..."+RESET)
        if self.events.login_event.wait(10):
            if self.events.bad_login.is_set():
                print(ERROR+"Bad username or password"+RESET)
                self.events.bad_login.clear()
                self.events.login_event.clear()
            else:

                if self.events.blob_updated.wait(8):
                    self.logger.debug("Blob updated")
                    self.settings.set('spotify', 'username', username)
                    if not isinstance(self.events.blob_data, str):
                        self.events.blob_data = self.events.blob_data.decode('utf-8')
                    self.settings.set('spotify', 'blob', self.events.blob_data)
                    self.settings.sync()
        else:
            print(ERROR+"Timeout"+RESET)

    @require_login
    def endOfTrack(self, session):
        self.logger.debug("Track end")
        self.player.next()

    @require_login
    def playSong(self, song):
        track = self.spotify_session.get_track(song)
        track.load()
        self.player.clear()
        self.player.enqueue(track)
        self.player.next()
        self.player.play()

    @require_login
    def search(self, t, query):
        self.last_search = self.spotify_session.search(query)
        self.last_search.load()
        self.last_search.type = t

    @require_login
    def more(self):
        if self.last_search:
            t = self.last_search.type
            self.last_search = self.last_search.more()
            self.last_search.load()
            self.last_search.type = t

    @require_login
    def setStarred(self, star):
        try:
            self.player.playlist[self.player.current].starred = bool(star)
        except IndexError:
            pass

    @require_login
    def showPlaylists(self):
        c = self.spotify_session.playlist_container
        if not c.is_loaded:
            c.load()
        
        in_folder = 0
        if len(c) > 0:
            print(HEADING+"Your playlists:"+RESET)
        else:
            print(ERROR+"You don't have any playlists."+RESET)
            return

        i = 0
        for item in c:
            if (i) % 15 == 14:
                try:
                    r = raw_input("%s==== %d more results. Press enter to see them, or anything else and enter to skip ====%s\n" % (RULER, len(c)-i+1, RESET))
                except NameError:
                    r = input("%s==== %d more results. Press enter to see them, or anything else and enter to skip ====%s\n" % (RULER, len(c)-i+1, RESET))

                if r:
                    return
            i += 1
            if isinstance(item, spotify.Playlist):
                name = "%s%s %s(%s tracks)%s" % (PLAYLIST, item.name, TRACKS_NUMBER, len(item.tracks), RESET)
                print("%s%s|- %s%s" % ("|--"*(in_folder), RULER, name, RESET))
            elif item.type == spotify.PlaylistType.START_FOLDER:
                print("%s%s|%s" % (RULER, "|--"*(in_folder), RESET))
                print("%s%s|--/-- %sFolder: %s:%s" % ("|--"*(in_folder), RULER, HEADING, item.name, RESET))
                in_folder += 1
            elif item.type == spotify.PlaylistType.END_FOLDER:
                print("%s%s\\------%s" % ("|--"*(in_folder), RULER, RESET))
                in_folder -= 1
                print("%s%s|%s" % (RULER, "|--"*(in_folder), RESET))

    @require_login
    def print_results(self):
        if self.last_search:
            t = self.last_search.type
            if t == "artist":
                if self.last_search.artists:
                    for artist in self.last_search.artists:
                        print("%s<%s>%s %s%s" % (LINK, artist.link, ARTIST, artist.name, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif t == "playlist":
                if self.last_search.playlists:
                    for playlist in self.last_search.playlists:
                        print("%s<%s>%s %s%s" % (LINK, playlist.uri, PLAYLIST, playlist.name, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif t == "track":
                if self.last_search.tracks:
                    for track in self.last_search.tracks:
                        print("%s<%s>%s %s%s by%s %s%s (from%s %s%s)%s" % (LINK, track.link, TRACK, track.name, SEPARATOR, ARTIST, track.album.artist.name, SEPARATOR, ALBUM, track.album.name, SEPARATOR, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif t == "album":
                if self.last_search.albums:
                    for album in self.last_search.albums:
                        print("%s<%s>%s %s%s by%s %s %s(%s)%s" % (LINK, album.link, ALBUM, album.name, SEPARATOR, ARTIST, album.artist.name, ALBUM, album.year, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            else:
                raise ValueError("Wrong search type")

    def quit(self):
        if self.events.connected.is_set():
            self.spotify_session.logout()
            self.events.logged_out_event.wait()
        self.loop.stop()

    @require_login
    def enqueue(self, query):
        tracks = Tracks(self.spotify_session, query)
        if(tracks):
            self.player.enqueue(tracks)
        else:
            print(ERROR+"No results."+RESET)
