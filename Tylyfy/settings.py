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
