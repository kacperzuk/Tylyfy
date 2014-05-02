import spotify
import threading
import alsaaudio
import time
from copy import copy

class Sink(object):
    pillow_size = 8 # bigger means smoother playback and bigger delays on state changes
    def __init__(self, session):
        self.output = None
        session.on(spotify.SessionEvent.MUSIC_DELIVERY, self.music_delivery)
        self.lock = threading.Lock()
        self.data = []

    def worker(self):
        while True:
            if self.data:
                self.lock.acquire()
                tmp_data = copy(self.data)
                self.data = []
                l = len(tmp_data)
                released = False
                for i in range(0, l):
                    if not released and l - i < self.pillow_size:
                        self.lock.release()
                        released = True
                    self.output.write(tmp_data[i])
            else:
                time.sleep(0.05)

    def music_delivery(self, session, audio_format, frames, num_frames):
        if not self.output:
            self.output = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, card='default')
            self.output.setchannels(audio_format.channels)
            self.output.setrate(audio_format.sample_rate)
            self.output.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            self.output.setperiodsize(160)
            threading.Thread(target=self.worker).start()
        if not self.lock.acquire(False):
            return 0
        self.data.append(frames)
        self.lock.release()
        return num_frames
