#!/usr/bin/env python2

import logging
import traceback
from handler import Handler
import cmd

class Prompt(object):
    def __init__(self, player):
        self.player = player

    def __str__(self):
        if not self.player.playing or self.player.current >= len(self.player.playlist):
            return "tylyfy>"
        t = self.player.playlist[self.player.current]
        return "\nNow playing: %s by %s (%s)\nTracks to the end of playlist: %d\ntylyfy> " % (t.name, t.album.artist.name, t.album.name, len(self.player.playlist)-self.player.current -1)

class Tylyfy(cmd.Cmd):
    doc_header = 'Available commands'
    prompt = 'tylyfy> '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.handler = Handler()
        self.prompt = Prompt(self.handler.player)

    def do_EOF(self, line):
        """exit """
        self.handler.quit()
        return True

    def emptyline(self):
        self.do_help("")

    def do_login(self, line):
        """login <username> <password> - password won't be stored, you only have to do this once"""
        username, password = line.split(' ')
        self.handler.login(username, password)

    def do_search(self, line):
        """search <type> <query> - search for <type>. Type can be:
    artist
    playlist
    track
    album
If type isn't supplied it's assumed to be artist."""
        line = line.strip().split(' ')
        t = line[0]
        if t in ('artist', 'playlist', 'track', 'album'):
            query = ' '.join(line[1:])
        else:
            t = 'artist'
            query = ' '.join(line)
        if self.handler.search(t, query):
            self.handler.print_results()

    def do_more(self, line):
        """more - show more search results"""
        if self.handler.more():
            self.handler.print_results()

    def do_clear(self, q):
        """clear: clear playlist"""
        self.handler.player.clear()

    def do_next(self, q):
        """next: skip to next song"""
        self.handler.player.next()

    def do_pause(self, q):
        """pause: pause playback"""
        self.handler.player.pause()

    def do_resume(self, q):
        """resume: resume playback"""
        self.handler.player.play()

    def do_play(self, query):
        """play: clear playlist and play object:
    play <spotify:track:song_id> - play song
    play <spotify:album:album_id> - play album
    play <spotify:artist:artist_id> - play all albums of an artist
    play <similar:spotify:artist:artist_id> - play all albums of similar artists
    play <spotify:...:playlist:playlist_id> - play Spotify playlist
    play <search query> - play first 20 elements of a search query"""
        
        self.handler.player.clear()
        self.do_enqueue(query)
        self.handler.player.next()

    def do_current(self, query):
        """Show current playlist and track"""
        i = 0
        for track in self.handler.player.playlist:
            if self.handler.player.current == i:
                print("** %s by %s (%s) (currently played)" % (track.name, track.album.artist.name, track.album.name))
            else:
                print("%s by %s (%s)" % (track.name, track.album.artist.name, track.album.name))
            i += 1

    def do_repeat(self, query):
        """Toggle looping through playlist"""
        self.handler.player.loop = not self.handler.player.loop
        if(self.handler.player.loop):
            print("Repeat: on")
        else:
            print("Repeat: off")

    def do_shell(self, query):
        """exec(query)"""
        try:
            exec query
        except Exception:
            traceback.print_exc()

    def do_playlists(self, query):
        """playlists - show your playlists"""
        self.handler.showPlaylists()

    def do_enqueue(self, query):
        """enqueue: add object to playlist:
    enqueue <spotify:track:song_id> - enqueue song
    enqueue <spotify:album:album_id> - enqueue album
    enqueue <spotify:artist:artist_id> - enqueue all albums of an artist
    enqueue <similar:spotify:artist:artist_id> - enqueue all albums of similar artists
    enqueue <spotify:...:playlist:playlist_id> - enqueue Spotify playlist
    enqueue <search query> - enqueue first 20 elements of a search query"""

        if query.find("spotify:track") == 0:
            ret = self.handler.getTracks("track", query)
        elif query.find("spotify:album") == 0:
            ret = self.handler.getTracks("album", query)
        elif query.find("spotify:artist") == 0:
            ret = self.handler.getTracks("artist", query)
        elif query.find("similar:spotify:artist") == 0:
            query = ':'.join(query.split(':')[1:])
            ret = self.handler.getTracks("similar", query)
        elif query.find("spotify:") == 0 and query.find(":playlist:") != -1:
            ret = self.handler.getTracks("playlist", query)
        else:
            ret = self.handler.getTracks("search", query)

        if ret:
            self.handler.enqueueResults()

Tylyfy().cmdloop()
