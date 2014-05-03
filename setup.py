#!/usr/bin/env python2
#-*- coding: utf-8 -*-

from distutils.core import setup

setup(name='Tylyfy',
      version='0.0.1',
      description='CLI-based Spotify player',
      author='Kacper Żuk',
      author_email='kacper.b.zuk+tylyfy@gmail.com',
      url='https://bitbucket.org/Kazuldur/tylyfy',
      packages=['tylyfy'],
      scripts=['tylyfy/tylyfy'],
      requires = [
          'pyspotify',
          'pyalsaaudio'
          ],
      license='BSD'
     )
