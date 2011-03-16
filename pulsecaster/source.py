# Copyright (C) 2011 Paul W. Frields and others.
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
import gtk
import pygst
import gobject
pygst.require('0.10')
import gst
from pulseaudio.PulseObj import PulseObj

class PulseCasterSource:
    '''A source object that provides sound data for PulseCaster'''
    def __init__(self):
        '''Construct the source object'''
        # Should include a PA source, a GtkCombBox, and a GtkProgressBar
        self.store = gtk.ListStore(gobject.TYPE_STRING,
                                   gobject.TYPE_STRING,
                                   gobject.TYPE_PYOBJECT)
        self.bus = None
        self.cbox = gtk.ComboBox(self.store)
        self.cell = gtk.CellRendererText()
        self.cbox.pack_start(self.cell, True)
        self.cbox.add_attribute(self.cell, 'text', True)
        self.cbox.connect('changed', self.set_meters)
        self.pbar = gtk.ProgressBar()
        self.pipeline = None
        print 'out of __init__'
        
    def repopulate(self, pa, use_source=True, use_monitor=True):
        '''Repopulate the ComboBox for this object'''
        print 'in repopulate'
        sources = pa.pulse_source_list()
        self.store.clear()
        for source in sources:
            if source.monitor_of_sink_name == None:
                if use_source == True:
                    self.store.append([source.name,
                                       source.description,
                                       source])
            else:
                if use_monitor == True:
                    self.store.append([source.name,
                                       source.description,
                                       source])
        print 'out of repopulate'

    def create_level_pipeline(self, *args):
        '''Make a GStreamer pipeline that allows level checking'''
        print 'in create_level_pipeline'
        pl = 'pulsesrc device=%s' % (self.pulsesrc)
        pl += '! level message=true interval=50000000 ! fakesink'
        print pl
        self.pipeline = gst.parse_launch(pl)
        self.pipeline.get_bus().add_signal_watch()
        self.conn = self.pipeline.get_bus().connect('message::element', self.update_level)
        self.pipeline.set_state(gst.STATE_PLAYING)
        print 'out of create_level_pipeline'
    
    def remove_level_pipeline(self, *args):
        '''Tear down the GStreamer pipeline attached to this object'''
        print 'in remove_level_pipeline'
        self.pipeline.set_state(gst.STATE_NULL)
        self.pipeline.get_bus().remove_signal_watch()
        self.pipeline.get_bus().disconnect(self.conn)
        self.conn = None
        self.pipeline = None
        print 'out of remove_level_pipeline'
    
    def set_meters(self, *args):
        print 'in set_meters'
        self.cbox.set_sensitive(False)
        if self.pipeline is not None:
            self.remove_level_pipeline()
        active = self.cbox.get_active()
        i = self.cbox.get_active_iter()
        self.pulsesrc = self.cbox.get_model().get_value(i, 0)
        self.create_level_pipeline()
        self.cbox.set_sensitive(True)
        print 'out of set_meters'
        
    def update_level(self, bus, message, *args):
        '''Update this object's GtkProgressBar to reflect current level'''
        print 'in update_level'
        print message
        if message.structure.get_name() == 'level':
            peaks = message.structure['peak']
            channels = len(peaks)
            for peak in peaks:
                v = v + peak
            v = iec_scale(v/channels)
            self.pbar.set_fraction(v)
        self.main.queue_draw()
        print 'out of update_level'
        return True
    
    def iec_scale(self, db):
        '''For a given dB value, return the iEC-268-18 standard percentage''' 
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
