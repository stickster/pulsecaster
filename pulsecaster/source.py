# Copyright (C) 2011-2015 Paul W. Frields and others.
# -*- coding: utf-8 -*-
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

from config import *
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, GObject, Gst
GObject.threads_init()
Gst.init(None)
import os

class PulseCasterSource:
    '''A source object that provides sound data for PulseCaster'''
    def __init__(self):
        '''Construct the source object'''
        # Should include a PA source, a GtkCombBox, and a GtkProgressBar
        self.store = Gtk.ListStore(GObject.TYPE_STRING,
                                   GObject.TYPE_STRING,
                                   GObject.TYPE_PYOBJECT)
        self.bus = None
        self.cbox = Gtk.ComboBox.new_with_model(self.store)
        self.cell = Gtk.CellRendererText()
        self.cbox.pack_start(self.cell, True)
        self.cbox.add_attribute(self.cell, 'text', True)
        self.cbox.connect('changed', self.set_meters)
        self.pbar = Gtk.ProgressBar()
        self.pipeline = None
        debugPrint('out of __init__')
        
    def repopulate(self, pa, use_source=True, use_monitor=True):
        '''Repopulate the ComboBox for this object'''
        debugPrint('in repopulate')
        sources = pa.source_list()
        self.store.clear()
        for source in sources:
            if source.monitor_of_sink_name == None:
                if use_source == True:
                    self.store.append([str(source.name, 'ascii'),
                                       str(source.description, 'ascii'),
                                       source])
            else:
                if use_monitor == True:
                    self.store.append([str(source.name, 'ascii'),
                                       str(source.description, 'ascii'),
                                       source])
        # Don't leave without resetting a source
        self.cbox.set_active(0)
        debugPrint('out of repopulate')

    def create_level_pipeline(self, *args):
        '''Make a GStreamer pipeline that allows level checking'''
        debugPrint('in create_level_pipeline')
        pl = 'pulsesrc device=%s' % (self.pulsesrc)
        pl += ' ! level message=true interval=100000000 ! fakesink'
        debugPrint(pl)
        self.pipeline = Gst.parse_launch(pl)
        self.pipeline.get_bus().add_signal_watch()
        self.conn = self.pipeline.get_bus().connect('message::element', self.update_level)
        self.pipeline.set_state(Gst.State.PLAYING)
        debugPrint('out of create_level_pipeline')
    
    def remove_level_pipeline(self, *args):
        '''Tear down the GStreamer pipeline attached to this object'''
        debugPrint('in remove_level_pipeline')
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.get_bus().remove_signal_watch()
        self.pipeline.get_bus().disconnect(self.conn)
        self.conn = None
        self.pipeline = None
        debugPrint('out of remove_level_pipeline')
    
    def set_meters(self, *args):
        debugPrint('in set_meters')
        self.cbox.set_sensitive(False)
        if self.pipeline is not None:
            self.remove_level_pipeline()
        i = self.cbox.get_active_iter()
        if i is not None:
            self.pulsesrc = self.cbox.get_model().get_value(i, 0)
            self.create_level_pipeline()
        self.cbox.set_sensitive(True)
        debugPrint('out of set_meters')
        
    def update_level(self, bus, message, *args):
        '''Update this object's GtkProgressBar to reflect current level'''
        if message.get_structure().get_name() == 'level':
            # stick with left channel in stereo setups
            peak = message.get_structure().get_value('peak')[0]
            self.pbar.set_fraction(self.iec_scale(peak)/100)
            self.pbar.queue_draw()
        return True
    
    def iec_scale(self, db):
        '''For a given dB value, return the iEC-268-18 standard value''' 
        pct = 0.0
        if db < -70.0:
            pct = 0.0
        elif db < -60.0:
            pct = (db + 70.0) * 0.25
        elif db < -50.0:
            pct = (db + 60.0) * 0.5 + 2.5
        elif db < -40.0:
            pct = (db + 50.0) * 0.75 + 7.5
        elif db < -30.0:
            pct = (db + 40.0) * 1.5 + 15.0
        elif db < -20.0:
            pct = (db + 30.0) * 2.0 + 30.0
        elif db < 0.0:
            pct = (db + 20.0) * 2.5 + 50.0
        else:
            pct = 100.0
        return pct
