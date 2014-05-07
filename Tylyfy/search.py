from Tylyfy.colors import *

class Search(object):
    def __init__(self, session, query):
        self.type = query.split(' ')[0]
        if not self.type in ('artist', 'playlist', 'track', 'album'):
            self.type = 'artist'
        self.search = session.search(' '.join(query.split(' ')[1:]))
        self.search.load()

    def more(self):
        self.search = self.search.more()
        self.search.load()

    def printResults(self):
        if self.search:
            if self.type == "artist":
                if self.search.artists:
                    for artist in self.search.artists:
                        print("%s<%s>%s %s%s" % (LINK, artist.link, ARTIST, artist.name, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif self.type == "playlist":
                if self.search.playlists:
                    for playlist in self.search.playlists:
                        print("%s<%s>%s %s%s" % (LINK, playlist.uri, PLAYLIST, playlist.name, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif self.type == "track":
                if self.search.tracks:
                    for track in self.search.tracks:
                        print("%s<%s>%s %s%s by%s %s%s (from%s %s%s)%s" % (LINK, track.link, TRACK, track.name, SEPARATOR, ARTIST, track.album.artist.name, SEPARATOR, ALBUM, track.album.name, SEPARATOR, RESET))
                else:
                    print(ERROR+"No results."+RESET)
            elif self.type == "album":
                if self.search.albums:
                    for album in self.search.albums:
                        if album.year > 0:
                            print("%s<%s>%s %s%s by%s %s %s(%s)%s" % (LINK, album.link, ALBUM, album.name, SEPARATOR, ARTIST, album.artist.name, ALBUM, album.year, RESET))
                        else:
                            print("%s<%s>%s %s%s by%s %s %s" % (LINK, album.link, ALBUM, album.name, SEPARATOR, ARTIST, album.artist.name, RESET))
                else:
                    print(ERROR+"No results."+RESET)
