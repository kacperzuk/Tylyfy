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

import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

class Settings(object):
    DEFAULT={
            "core": {
                "loglevel": "warning",
                "custom_sink": "False"
                },
            "spotify": {
                "loglevel": "warning"
                },
            "lastfm": {
                "custom_scrobbler": "False",
                "username": "",
                "password": ""
                }
            }
    def __init__(self):
        directory = os.path.join(os.path.expanduser("~"), ".config", "tylyfy")
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.path = os.path.join(directory, "settings.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

        self._initDefaults()

    def get(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except configparser.NoSectionError:
            pass
        except configparser.NoOptionError:
            pass
        if default:
            self.set(section, option, default)
        return default

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def sync(self):
        with open(self.path, 'w') as f:
            self.config.write(f)

    def _initDefaults(self):
        for section, values in self.DEFAULT.items():
            for k,v in values.items():
                if not self.get(section, k, v):
                    self.set(section, k, v)
        self.sync()
