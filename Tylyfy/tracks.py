import spotify
import logging
from Tylyfy.colors import *

class Tracks(list):
    def __init__(self, session, query):
        list.__init__(self)
        self.logger = logging.getLogger(__name__)

        t = query.split(' ')[0].split(':')[0]
        if t == "spotify":
            t = query.split(':')[1]
            if t == "user":
                t = query.split(':')[3]
        self.logger.debug("Query type: %s" % t)
        if t == "track":
            self.append(session.get_track(query))
        elif t == "album":
            album = session.get_album(query)
            browser = album.browse()
            browser.load()
            self.extend(browser.tracks)
        elif t == "artist":
            artist = session.get_artist(query)
            browser = artist.browse()
            browser.load()
            self.extend(browser.tracks)
        elif t == "similar":
            query = ':'.join(query.split(':')[1:])
            artist = session.get_artist(query)
            browser = artist.browse()
            browser.load()
            for sim in browser.similar_artists:
                b = sim.browse()
                b.load()
                if(b.tracks):
                    self.append(b.tracks[0])
        elif t == "playlist":
            print(query.split(' ')[0])
            if query.split(' ')[0] == "playlist": # search user's playlist names
                c = session.playlist_container
                if not c.is_loaded:
                    c.load()
                result = None
                for item in c:
                    if item.name.lower() == query.lower():
                        self.logger.debug("Direct hit on playlist")
                        result = item
                        break
                    elif not item.name.lower().find(query.lower()):
                        if result == None:
                            self.logger.debug("Playlist candidate")
                            result = item
                        else:
                            self.logger.debug("Another candidate, allow only direct hit now")
                            result = False
                if result:
                    if not result.is_loaded:
                        result.load()
                    self.extend(result.tracks)
                elif result == False:
                    print(INFO+"Ambiguous query, multiple playlists match it"+RESET)
            else: #assume full URI
                playlist = session.get_playlist(query)
                playlist.load()
                self.extend(playlist.tracks)
        elif t == "starred":
            playlist = session.get_starred()
            playlist.load()
            self.extend(playlist.tracks)
        else:
            search = session.search(query)
            search.load()
            self.extend(list(search.tracks))
            search = search.more()
            search.load()
            self.extend(list(search.tracks))

        for track in self:
            track.load()
            if not track.availability == spotify.TrackAvailability.AVAILABLE:
                self.remove(track)
