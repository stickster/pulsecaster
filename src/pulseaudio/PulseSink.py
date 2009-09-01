#!/usr/bin/python
# vi: et sw=2
#
# PulseSink.py
# Copyright (C) 2009  Harry Karvonen
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
# Author: Harry Karvonen <harry.karvonen@gmail.com>
#

from lib_pulseaudio import *

from PulseClient import PulseClient
from PulseVolume import PulseVolumeCtypes

# This class contains all commons features from PulseSinkInputInfo and
# PulseSinkInfo
class PulseSink:
  def __init__(self, index, name, mute, volume, client):
    self.index  = index
    self.name   = name
    self.mute   = mute
    self.volume = volume
    self.client = client
    return

  # PROTOTYPE
  def unmuteStream(self):
    raise Exception("ABSTRACT METHOD CALLED")
    return

  # PROTOTYPE
  def muteStream(self):
    raise Exception("ABSTRACT METHOD CALLED")
    return

  # PROTOTYPE
  def setVolume(self):
    raise Exception("ABSTRACT METHOD CALLED")
    return

  def printDebug(self):
    print "self.index:", self.index
    print "self.name:", self.name
    print "self.mute:", self.mute
    print "self.volume:", self.volume
    print "self.client:", self.client
    return

################################################################################

class PulseSinkInfo(PulseSink):
  def __init__(self, pa_sink_info):
    PulseSink.__init__(self, pa_sink_info.index,
                             pa_sink_info.name,
                             pa_sink_info.mute,
                             PulseVolumeCtypes(pa_sink_info.volume),
                             PulseClient("Selected Sink"))

    self.description         = pa_sink_info.description
    self.sample_spec         = pa_sink_info.sample_spec
    self.channel_map         = pa_sink_info.channel_map
    self.owner_module        = pa_sink_info.owner_module
    self.monitor_source      = pa_sink_info.monitor_source
    self.monitor_source_name = pa_sink_info.monitor_source_name
    self.latency             = pa_sink_info.latency
    self.driver              = pa_sink_info.driver
    self.flags               = pa_sink_info.flags
    self.proplist            = pa_sink_info.proplist
    self.configured_latency  = pa_sink_info.configured_latency

    return

  ###
  #
  # Define PROTOTYPE functions

  def unmuteStream(self, pulseInterface):
    pulseInterface.pulse_unmute_sink(self.index)

    self.mute = 0
    return

  ###

  def muteStream(self, pulseInterface):
    pulseInterface.pulse_mute_sink(self.index)

    self.mute = 1
    return

  ###

  def setVolume(self, pulseInterface, volume):
    pulseInterface.pulse_set_sink_volume(self.index, volume)

    self.volume = volume
    return

  ###

  def printDebug(self):
    print "PulseSinkInfo"
    PulseSink.printDebug(self)
    print "self.description", self.description
    print "self.sample_spec", self.sample_spec
    print "self.channel_map", self.channel_map
    print "self.owner_module", self.owner_module
    print "self.monitor_source", self.monitor_source
    print "self.monitor_source_name", self.monitor_source_name
    print "self.latency", self.latency
    print "self.driver", self.driver
    print "self.flags", self.flags
    print "self.proplist", self.proplist
    print "self.configured_latency", self.configured_latency
    return

  ###

  def __str__(self):
    return "ID: " + str(self.index) + ", Name: \"" + \
           self.name + "\""

################################################################################

class PulseSinkInputInfo(PulseSink):
  def __init__(self, pa_sink_input_info):
    PulseSink.__init__(self, pa_sink_input_info.index,
                             pa_sink_input_info.name,
                             pa_sink_input_info.mute,
                             PulseVolumeCtypes(pa_sink_input_info.volume),
                             PulseClient("Unknown client"))
    self.owner_module    = pa_sink_input_info.owner_module
    self.client_id       = pa_sink_input_info.client
    self.sink            = pa_sink_input_info.sink
    self.sample_spec     = pa_sink_input_info.sample_spec
    self.channel_map     = pa_sink_input_info.channel_map
    self.buffer_usec     = pa_sink_input_info.buffer_usec
    self.sink_usec       = pa_sink_input_info.sink_usec
    self.resample_method = pa_sink_input_info.resample_method
    self.driver          = pa_sink_input_info.driver
    #self.proplist        = pa_sink_input_info.proplist

    return

  ###

  def setClient(self, c):
    self.client = c

  ###
  #
  # Define PROTOTYPE functions

  def unmuteStream(self, pulseInterface):
    pulseInterface.pulse_unmute_stream(self.index)

    self.mute = 0
    return

  ###

  def muteStream(self, pulseInterface):
    pulseInterface.pulse_mute_stream(self.index)

    self.mute = 1
    return

  ###

  def setVolume(self, pulseInterface, volume):
    pulseInterface.pulse_set_sink_input_volume(self.index, volume)

    self.volume = volume
    return

  ###

  def printDebug(self):
    print "PulseSinkInputInfo"
    PulseSink.printDebug(self)

    print "self.owner_module:", self.owner_module
    print "self.client_id:", self.client_id
    print "self.sink:", self.sink
    print "self.sample_spec:", self.sample_spec
    print "self.channel_map:", self.channel_map
    print "self.buffer_usec:", self.buffer_usec
    print "self.sink_usec:", self.sink_usec
    print "self.resample_method:", self.resample_method
    print "self.driver:", self.driver

  ###

  def __str__(self):
    if self.client:
      return "ID: " + str(self.index) + ", Name: \"" + \
             self.name + "\", mute: " + str(self.mute) + ", " + str(self.client)
    return "ID: " + str(self.index) + ", Name: \"" + \
           self.name + "\", mute: " + str(self.mute)
