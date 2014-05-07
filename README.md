Tylyfy
======

About
-----

Tylyfy is a simple CLI-based Spotify player for Premium users.

Instalation
-----------

#### Packages

- [ArchLinux](https://aur.archlinux.org/packages/tylyfy-git/)

#### Manual installation

- install [setuptools](https://pypi.python.org/pypi/setuptools)
- clone repository with `git clone http://bitbucket.org/Kazuldur/tylyfy.git`
- change directory to cloned repository and launch `python setup.py install` as root

Requirements
------------

- [Python](http://python.org) (both 2 and 3 are supported)
- [pyspotify](http://pyspotify.mopidy.com/en/latest/) >= 2.0.0
- [alsaaudio](http://pyalsaaudio.sourceforge.net/) or [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)

#### Optional

- [pylast](https://code.google.com/p/pylast/) for an alternative Last.FM Scrobbler (see Troubleshooting section below)

Basic usage
-----------

#### First run and configuration:

Before the first run you must obtain a _Spotify API_ key [here](https://developer.spotify.com/my-account/keys). Download the binary version and save it in `~/.config/tylyfy/spotify_appkey.key`.
After the first run of Tylyfy, you'll have to login to Spotify using command:
```
login <username> <password>
```

Your password won't be stored, but a blob returned by Spotify will, so you won't have to login after each restart.

#### Scrobbling:

To scrobble to Last.FM you must first provide your username and password. Edit `~/.config/tylyfy/settings.ini` and add your username and password to the `[lastfm]` section:
```
[lastfm]
username = YourLogin
password = YourPassword
custom_scrobbler = False
```

Scrobbling to Facebook and to Spotify works without any configuration.

#### Getting help:

See command `help`. You can also write `help <command>` to get help about specific command.

Troubleshooting:
----------------

#### Broken sound

If your sound is choppy and CPU usage is really high, try this:

1. make sure you have [alsaaudio](http://pyalsaaudio.sourceforge.net/) installed
2. edit `~/.config/tylyfy/settings.ini` and set `custom_sink` in `[core]` section to `True`:
```
[core]
custom_sink = True
```
3. If the sound is choppy, set `pillow_size` in `[core]` section to something bigger then the default 8. If the lag is too big, set it to something lower.

#### Scrobbling to Last.FM doesn't work
If scrobbling to Last.FM doesn't work, try this:

1. get API key and API secret from [Last.FM](http://www.lastfm.pl/api/account/create)
2. edit `~/.config/tylyfy/settings.ini` and set this in `[lastfm]` section:
```
[lastfm]
username = YourUsername
password_md5 = MD5HashOfYourPassword
api_key = APIkey
secrey_key = APIsecret
```
Unhashed password isn't needed anymore.

~/.config/tylyfy/settings.json reference
----------------------------------------

- *core*
  - *loglevel*: possible values debug, info, warning, error, critical
    sets what messages will be printed
  - *custom_sink* - possible values True, False
    enables or disables custom sink (see Troubleshooting section)
  - *pillow_size*: takes integer value, sets buffer size (used only with custom_sink)
- *spotify*
  - *loglevel*: possible values debug, info, warning, error, critical
    sets what messages will be printed
  - *blob*: used internally, don't touch
  - *username*: used internally, don't touch
- *lastfm*
  - *username*: sets Last.fm username
  - *custom_scrobbler*: possible values True, False
    enables or disables custom scrobbler (see Troubleshooting section)
  - *password*: sets Last.fm password (used only without custom_scrobbler)
  - *password_md5*: sets password's MD5 hash (used only with custom_scrobbler)
  - *api_key*: sets Last.fm API key (used only with custom_scrobbler)
  - *secret_key*: sets Last.fm API secret key (used only with custom_scrobbler)
