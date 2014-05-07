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
import threading
import alsaaudio
import time
from copy import copy

class Sink(object):
    def __init__(self, session, pillow_size):
        self.pillow_size = pillow_size
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
