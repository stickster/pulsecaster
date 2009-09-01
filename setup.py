#!/usr/bin/python
#
# Copyright (C) 2009 Paul W. Frields
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

from pulsecaster.config import *
from setuptools import setup, find_packages
setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    license = LICENSE,
    keywords = KEYWORDS,
    url = URL,

    install_requires = ['gtk>=2.14',
                        'dbus>=0.83'],
    # Also requires pulseaudio-libs >= 0.9.15
    scripts = ['pulsecaster.py'],
    include_package_data = True,
    package_data = {
        'pulsecaster': ['data/pulsecaster.glade'],
        },
    #message_extractors = {
    #    'pulsecaster': [('**.py', 'python', None),
    #                    ('**.glade', '', None),
    #                    ],
    #    },
    packages = find_packages(),
)
