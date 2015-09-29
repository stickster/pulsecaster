# Copyright (C) 2010-2015 Paul W. Frields and others.
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

import dbus
import dbus.mainloop.glib

class PulseCasterListener:
    def __init__(self, ui):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        
        self.bus.add_signal_receiver(ui.repop_sources,
                                     signal_name='DeviceAdded', 
                                     dbus_interface='org.freedesktop.Hal.Manager',
                                     path='/org/freedesktop/Hal/Manager')
        self.bus.add_signal_receiver(ui.repop_sources,
                                     signal_name='DeviceRemoved',
                                     dbus_interface='org.freedesktop.Hal.Manager',
                                     path='/org/freedesktop/Hal/Manager')
        

