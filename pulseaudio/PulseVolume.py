#!/usr/bin/python
# vi: et sw=2
#
# PulseVolume.py
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
import math

# This contains all basic volume features
class PulseVolume:
  def __init__(self, vol = 0, channels = 2):
    self.channels = channels

    if vol > 100 or vol < 0:
      print "WARNING: Volume is invalid!"
      vol = 0

    self.values   = [vol] * self.channels

    return

  ##############################
  #
  # Type conversions
  #
  #def fromCtypes(self, pa_cvolume):
  #  self.channels = pa_cvolume.channels
  #  self.values   = map(lambda x: (math.ceil(float(x) * 100 / PA_VOLUME_NORM)),
  #                      pa_cvolume.values[0:self.channels])
  #  return self

  def toCtypes(self):
    ct = PA_CVOLUME()
    ct.channels = self.channels

    for x in range(0, self.channels):
      ct.values[x] = (self.values[x] * PA_VOLUME_NORM) / 100
    
    return ct

  ###

  def printDebug(self):
    print "PulseVolume"
    print "self.channels:", self.channels
    print "self.values:", self.values
    #print "self.proplist:", self.proplist

  ###

  def incVolume(self, vol):
    "Increment volume level (mono only)"
    vol += sum(self.values) / len(self.values)

    vol = int(vol)

    if vol > 100:
      vol = 100
    elif vol < 0:
      vol = 0

    self.setVolume(vol)

    return

  ###

  def setVolume(self, vol, balance = None):
    if not balance:
      self.values = [vol] * self.channels
    else:
      self.values[balance] = vol

    return

  ###

  def getVolume(self):
    "Return mono volume"
    return int(sum(self.values) / len(self.values))

  ###

  def __str__(self):
    return "Channels: " + str(self.channels) + \
           ", values: \"" + str(map(lambda x: str(x) + "%", self.values)) + "\""

################################################################################

class PulseVolumeCtypes(PulseVolume):
  def __init__(self, pa_cvolume):
    self.channels = pa_cvolume.channels
    self.values   = map(lambda x: (math.ceil(float(x) * 100 / PA_VOLUME_NORM)),
                        pa_cvolume.values[0:self.channels])
    return

