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


import gconf
from config import *

class PulseCasterGconf:
    def __init__(self):
        self.dirbase = '/apps/' + NAME
        self.client = gconf.client_get_default()
        self.warn = self.client.get_without_default(self.dirbase + '/warn')
        if type(self.warn) is None:
            self.warn = True
            self.client.set_value(self.dirbase + '/warn', False)
        self.vorbisq = self.client.get_without_default(self.dirbase + '/vorbisq')
        if type(self.vorbisq) is None:
            self.vorbisq = 4
            self.client.set_value(self.dirbase + '/vorbisq', self.vorbisq)

