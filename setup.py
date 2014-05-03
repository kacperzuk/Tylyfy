#!/usr/bin/env python2
#-*- coding: utf-8 -*-

from setuptools import setup

deps = [ 'pyspotify', 'pyalsaaudio' ]

setup(name='Tylyfy',
      version='0.0.2',
      description='CLI-based Spotify player',
      author='Kacper Żuk',
      author_email='kacper.b.zuk+tylyfy@gmail.com',
      url='https://bitbucket.org/Kazuldur/tylyfy',
      packages=['Tylyfy'],
      scripts=['tylyfy'],
      install_requires = [
                           'pyspotify>=2.0.0b2',
                           'pyalsaaudio>=0.7'
                         ],
      license='BSD'
     )
