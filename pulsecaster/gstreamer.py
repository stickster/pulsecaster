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


import pygst
pygst.require('0.10')
import gst
from sys import stdout

class PulseCatcherPipeline:
    def __init__(self, pulseDeviceMyVoice, pulseDeviceOtherVoice):
        # Set up one branch of the Y
        self.yleft = gst.Pipeline('pcPipelineLeft')
        self.lsource = gst.element_factory_make('pulsesrc', 'lsource')
        self.lsource.set_property('device', pulseDeviceMyVoice)
        self.lencoder = gst.element_factory_make('vorbisenc', 'lencoder')
        self.lencoder.set_property('quality', 0.5)
        self.lmuxer = gst.element_factory_make('oggmux', 'lmuxer')
        #self.add(self.lsource, self.lencoder, self.lmuxer)
        # Set up other branch
        self.yright = gst.Pipeline('pcPipelineRight')
        self.rsource = gst.element_factory_make('pulsesrc', 'rsource')
        self.rsource.set_property('device', pulseDeviceOtherVoice)
        self.rencoder = gst.element_factory_make('vorbisenc', 'rencoder')
        self.rencoder.set_property('quality', 0.5)
        self.rmuxer = gst.element_factory_make('oggmux', 'rmuxer')
