# -*- coding: utf-8 -*-
#
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

NAME = u'PulseCaster'
LNAME = u'pulsecaster'

import gettext
_ = lambda x: gettext.ldgettext(NAME, x)

VERSION = '0.2'
AUTHOR = u'Paul W. Frields'
AUTHOR_EMAIL = u'stickster@gmail.com'
DESCRIPTION = _(u'PulseAudio based podcast recorder')
LICENSE = u'GPLv3+'
COPYRIGHT = _(u'Copyright © 2009-2010 ' + AUTHOR)
KEYWORDS = u'pulseaudio podcast recorder mixer gstreamer pygtk'
URL = u'http://pulsecaster.org'
CONTRIBUTORS = [u'Jürgen Geuter <tante@the-gay-bar.com>',
                u'Harry Karvonen <harry.karvonen@gmail.com>']

LICENSE_TEXT = u'''Licensed under the GNU General Public License Version 3

PulseCaster is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

PulseCaster is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.'''
