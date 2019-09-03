# Copyright (C) 2013-2015 Paul W. Frields
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


from gi.repository import Gio
try:
    from pulsecaster.config import *
except ModuleNotFoundError:
    sys.path.append(os.getcwd())
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from pulsecaster.config import *

class PulseCasterGSettings:
    def __init__(self):
        gss = Gio.SettingsSchemaSource.get_default()
        schema = gss.lookup(GIO_ID, True)
        if schema == None:
            # We're probably developing, then.
            gss = Gio.SettingsSchemaSource.new_from_directory('.', None, False)
            schema = gss.lookup(GIO_ID, True)

        self.gsettings = Gio.Settings.new_full(schema, None, GIO_PATH)

        try:
            self.skip_warn = self.gsettings.get_boolean('skip-warning')
        except:
            self.gsettings.set_boolean('skip-warning', False)
            self.skip_warn = self.gsettings.get_boolean('skip-warning')

        try:
            self.vorbisq = self.gsettings.get_int('vorbisq')
        except:
            self.gsettings.set_int('vorbisq', 4)
            self.vorbisq = self.gsettings.get_int('vorbisq')

        try:
            self.codec = self.gsettings.get_string('codec')
        except:
            self.gsettings.set_string('codec', 'vorbis')
            self.codec = self.gsettings.get_string('codec')

        try:
            self.expert = self.gsettings.get_boolean('expert')
        except:
            self.gsettings.set_boolean('expert', False)
            self.expert = self.gsettings.get_boolean('expert')

        try:
            self.audiorate = self.gsettings.get_int('audiorate')
        except:
            self.gsettings.set_int('audiorate', 48000)
            self.audiorate = self.gsettings.get_int('audiorate')

    def change_warn(self, val):
        if type(val) is not bool:
            raise ValueError("requires bool value")
        self.gsettings.set_boolean('skip-warning', val)
