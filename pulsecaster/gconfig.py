# Copyright (C) 2009, 2010 Paul W. Frields
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


from gi.repository import GConf
from config import *

class PulseCasterGconf:
    def __init__(self):
        self.dirbase = '/apps/' + NAME
        self.client = GConf.Client.get_default()
        if self.client.dir_exists(self.dirbase) is False:
            self.client.add_dir(self.dirbase, GConf.ClientPreloadType.PRELOAD_NONE)
            
        self.skip_warn = self.client.get_bool(self.dirbase + '/skip_warning')
        if self.skip_warn is None or type(self.skip_warn) is not bool:
            self.skip_warn = False
        
        self.vorbisq = self.client.get(self.dirbase + '/vorbisq')
        if type(self.vorbisq) is not int:
            self.vorbisq = 4
            self.client.set_int(self.dirbase + '/vorbisq', self.vorbisq)

        self.codec = self.client.get_string(self.dirbase + '/codec')
        if type(self.codec) is not str or \
                self.codec not in ['flac',
                                   'vorbis']:
            self.codec = 'vorbis'
            self.client.set_string(self.dirbase + '/codec', self.codec)

        self.expert = self.client.get_bool(self.dirbase + '/expert')
        if type(self.expert) is not bool:
            self.expert = False
            self.client.set_bool(self.dirbase + '/expert', self.expert)

        self.audiorate = self.client.get_int(self.dirbase + '/audiorate')
        if type(self.audiorate) is not int or \
               self.audiorate not in [44100, 48000]:
            self.client.set_int(self.dirbase + '/audiorate', 48000)
            self.audiorate = 48000

    def change_warn(self, val):
        if type(val) is not bool:
            raise ValueError, "requires bool value"
        self.client.set_bool(self.dirbase + '/skip_warning', val)
