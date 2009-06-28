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


from config import *
from pulseaudio.PulseObj import PulseObj
import gtk
import gtk.glade
import os
import dbus
import gobject
import dbus.mainloop.glib
import pygst
pygst.require('0.10')
import gst

# FIXME
fname = os.getcwd() + '/data/pulsecaster.glade'
logofile = os.getcwd() + '/data/icons/scalable/pulsecaster.svg'
_debug = True

def _debugPrint(text):
    if _debug:
        print (text)

class PulseCasterUI:
    def __init__(self):
        self.xml = gtk.glade.XML(fname)
        self.logo = gtk.gdk.pixbuf_new_from_file(logofile)
        
        # Main dialog basics
        self.main = self.xml.get_widget('main_dialog')
        self.main.set_title(NAME)
        self.main_title = self.xml.get_widget('main_title')
        self.main_title.set_label('<big><big><big><b><i>' +
                                  NAME + '</i></b></big></big></big>')
        self.main.connect('delete_event', self.on_close)
        self.about_button = self.xml.get_widget('about_button')
        self.about_button.connect('clicked', self.showAbout)
        self.close = self.xml.get_widget('close_button')
        self.close.connect('clicked', self.on_close)
        self.record = self.xml.get_widget('record_button')
        self.record_id = self.record.connect('clicked', self.on_record)
        
        # About dialog basics
        self.about = self.xml.get_widget('about_dialog')
        self.about.connect('delete_event', self.hideAbout)
        self.about.connect('response', self.hideAbout)
        self.about.set_name(NAME)
        self.about.set_version(VERSION)
        self.about.set_copyright(COPYRIGHT)
        self.about.set_comments(DESCRIPTION)
        self.about.set_license(LICENSE_TEXT)
        self.about.set_website(URL)
        self.about.set_website_label(URL)
        self.authors = [AUTHOR + ' <' + AUTHOR_EMAIL + '>']
        for contrib in CONTRIBUTORS:
            self.authors.append(contrib)
        self.about.set_authors(self.authors)
        self.about.set_logo(self.logo)
        self.about.set_program_name(NAME)

        # Create PulseAudio backing
        self.pa = PulseObj(clientName=NAME)

        # Create and populate combo boxes
        self.combo_vbox = self.xml.get_widget('combo_vbox')
        self.user_vox = gtk.combo_box_new_text()
        self.subject_vox = gtk.combo_box_new_text()
        self.combo_vbox.add(self.user_vox)
        self.combo_vbox.add(self.subject_vox)
        self.user_vox.connect('button-press-event', self.repop_sources)
        self.subject_vox.connect('button-press-event', self.repop_sources)

        # Fill the combo boxes initially
        self.repop_sources()
        self.listener = PulseCasterListener(self)
        
        self.file_entry = self.xml.get_widget('file_entry')
        self.file_chooser = self.xml.get_widget('file_chooser')
        self.open_button = self.xml.get_widget('open_button')
        self.open_button.connect('button-press-event', self.showFileChooser)
        self.file_chooser_cancel_button = self.xml.get_widget('file_chooser_cancel_button')
        self.file_chooser_cancel_button.connect('button-press-event', self.hideFileChooser)
        self.file_chooser_save_button = self.xml.get_widget('file_chooser_save_button')
        self.file_chooser_save_button.connect('button-press-event', self.updateFileSinkPath)
        self.filesinkpath = os.path.join(os.getenv('HOME'), 'podcast.ogg')
        self.file_chooser.set_filename(self.filesinkpath)
        self.file_entry.set_text(self.filesinkpath)
        
    def repop_sources(self, *args):
        self.sources = self.pa.pulse_source_list()
        l = self.user_vox.get_model()
        l.clear()
        l = self.subject_vox.get_model()
        l.clear()
        self.uservoxes = []
        self.subjectvoxes = []
        for source in self.sources:
            if source.monitor_of_sink_name == None:
                self.uservoxes.append((source.name, source.description))
                self.user_vox.append_text(source.description)
            else:
                self.subjectvoxes.append((source.name, source.description))
                self.subject_vox.append_text(source.description)
        self.user_vox.set_active(0)
        self.subject_vox.set_active(0)
        self.combo_vbox.reorder_child(self.user_vox, 0)
        self.combo_vbox.reorder_child(self.subject_vox, 1)
        self.combo_vbox.show_all()

    def on_record(self, *args):
        # Get filename
        # Check whether filename exists, if so, overwrite? y/n
        filesinkpath = self.file_button.get_file()
        if filesinkpath is None:
            return
        # Set up GStreamer stuff
        self.combiner = gst.Pipeline('PulseCasterCombinePipe')
        self.lsource = gst.element_factory_make('pulsesrc', 'lsrc')
        self.lsource.set_property('device', 
                                  self.uservoxes[self.user_vox.get_active()][0])
        self.rsource = gst.element_factory_make('pulsesrc', 'rsrc')
        self.rsource.set_property('device',
                                  self.subjectvoxes[self.subject_vox.get_active()][0])
        
        self.adder = gst.element_factory_make('adder', 'mix')
        self.encoder = gst.element_factory_make('vorbisenc', 'enc')
        self.muxer = gst.element_factory_make('oggmux', 'mux')
        self.filesink = gst.element_factory_make('filesink', 'fsink')
        self.filesink.set_property('location', filesinkpath)

        self.combiner.add(self.lsource, 
                          self.rsource, 
                          self.adder, 
                          self.encoder, 
                          self.muxer, 
                          self.filesink)
        gst.element_link_many(self.lsource,
                              self.adder, 
                              self.encoder, 
                              self.muxer,
                              self.filesink)
        gst.element_link_many(self.rsource, self.adder)

        # FIXME: Dim elements other than the 'record' widget
        self.record.set_label(gtk.STOCK_MEDIA_STOP)
        self.record.disconnect(self.record_id)
        self.stop_id = self.record.connect('clicked', self.on_stop)
        self.record.show()
        self.combiner.set_state(gst.STATE_PLAYING)

    def on_stop(self, *args):
        self.combiner.set_state(gst.STATE_NULL)
        self.record.set_label(gtk.STOCK_MEDIA_RECORD)
        self.record.disconnect(self.stop_id)
        self.record_id = self.record.connect('clicked', self.on_record)
        self.record.show()

    def on_close(self, *args):
        try:
            self.pa.disconnect()
        except:
            pass
        gtk.main_quit()

    def showAbout(self, *args):
        self.about.show()

    def hideAbout(self, *args):
        self.about.hide()
        
    def showFileChooser(self, *args):
        self.file_chooser.set_filename(self.filesinkpath)
        self.file_chooser.show()
    
    def hideFileChooser(self, *args):
        self.file_chooser.hide()

    def updateFileSinkPath(self, *args):
        self.hideFileChooser()
        self.filesinkpath = self.file_chooser.get_filename()
        self.file_entry.set_text(self.filesinkpath)
    

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
        

if __name__ == '__main__':
    pulseCaster = PulseCasterUI()
    pulseCaster.main.show_all()
    gtk.main()
