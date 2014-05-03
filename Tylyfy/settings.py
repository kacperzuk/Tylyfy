import os
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

class Settings(object):
    def __init__(self):
        directory = os.path.join(os.path.expanduser("~"), ".config", "tylyfy")
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.path = os.path.join(directory, "settings.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def get(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except configparser.NoSectionError:
            pass
        except configparser.NoOptionError:
            pass
        self.set(section, option, default)
        return default

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))

    def sync(self):
        with open(self.path, 'wb') as f:
            self.config.write(f)
