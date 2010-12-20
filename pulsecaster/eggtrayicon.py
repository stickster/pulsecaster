# Copyright (C) 2010 Paul W. Frields and others.
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

from config import NAME
import pygtk
pygtk.require("2.0")
import gtk
import egg.trayicon

class PulseCasterTrayIcon:
    def __init__(self):
        self = egg.trayicon.TrayIcon(NAME)
        self.add(gtk.image_new_from_icon_name('pulsecaster', gtk.ICON_SIZE_LARGE_TOOLBAR))

# Later on the trayicon will have useful features, e.g. a tooltip
# showing the elapsed time.
