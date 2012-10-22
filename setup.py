#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, 2010, 2012 Paul W. Frields and others.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Author: Paul W. Frields <stickster@gmail.com>
#         Jürgen Geuter <tante@the-gay-bar.com>

from setuptools import setup, find_packages
from pulsecaster.config import *
from glob import glob

def get_mo_files(*args):
    mo = []
    for f in glob('po/*.mo'):
        locale = f.replace('po/', '').split('.')[0]
        mo.append(('/usr/share/locale/%s/LC_MESSAGES/' % locale, [f]))
    return mo

my_data_files = [
    ('/usr/share/pulsecaster/', ["pulsecaster/data/pulsecaster.ui"]),
    ('/usr/share/icons/hicolor/scalable/apps/', ['pulsecaster/data/icons/scalable/pulsecaster.svg', 'pulsecaster/data/icons/scalable/pulsecaster-logo.svg']),
    ('/usr/share/icons/hicolor/16x16/apps/', ['pulsecaster/data/icons/16x16/pulsecaster-16.png']),
    ('/usr/share/icons/hicolor/24x24/apps/', ['pulsecaster/data/icons/24x24/pulsecaster-24.png']),
    ('/usr/share/icons/hicolor/32x32/apps/', ['pulsecaster/data/icons/32x32/pulsecaster-32.png']),
    ('/usr/share/icons/hicolor/48x48/apps/', ['pulsecaster/data/icons/48x48/pulsecaster-48.png']),
    ('/usr/share/icons/hicolor/64x64/apps/', ['pulsecaster/data/icons/64x64/pulsecaster-64.png']),
    ('/usr/share/applications/', ['pulsecaster.desktop']),
    ]
my_data_files.extend(get_mo_files())

setup(
    name = "pulsecaster",
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    license = LICENSE,
    keywords = KEYWORDS,
    url = URL,

    scripts = ['pulsecaster/pulsecaster'],
    data_files = my_data_files,
    
    message_extractors = {
        'pulsecaster': [('**.py', 'python', None),
                        ],
        },
    packages = find_packages(),
)
