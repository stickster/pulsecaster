#!/usr/bin/python
# vi: et sw=2
#
# PulseClient.py
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

# This class contains all basic client features
class PulseClient:
  def __init__(self, name, index = 0):
    self.index = index
    self.name  = name
    return

  ###

  def printDebug(self):
    print "self.index:", self.index
    print "self.name:", self.name
    return

  ###

  def __str__(self):
    return "Client-ID: " + str(self.index) + ", Name: \"" + self.name + "\""

################################################################################

# This class is used with Ctypes
class PulseClientCtypes(PulseClient):
  def __init__(self, pa_client):
    PulseClient.__init__(self, pa_client.name, pa_client.index)

    self.owner_module = pa_client.owner_module
    self.driver       = pa_client.driver
    #self.proplist     = pa_sink_input_info.proplist
    return

  ###

  def printDebug(self):
    print "PulseClientCtypes"
    PulseClient.printDebug(self)
    print "self.owner_module:", self.owner_module
    print "self.driver:", self.driver
    #print "self.proplist:", self.proplist
    return

