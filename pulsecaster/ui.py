# Copyright (C) 2009, 2010 Paul W. Frields and others.
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
#         Jürgen Geuter <tante@the-gay-bar.com>


from config import *
import gconfig
from pulseaudio.PulseObj import PulseObj
from listener import *
import gtk
import os
import sys
import tempfile
import gobject
import pygst
pygst.require('0.10')
import gst
from datetime import datetime

import gettext
_ = lambda x: gettext.ldgettext(NAME, x)

try:
    _debug = os.environ['PULSECASTER_DEBUG']
except:
    _debug = False

def _debugPrint(text):
    if _debug:
        print ('%s: %s' % (NAME, text))

class PulseCasterUI:
    def __init__(self):
        self.builder = gtk.Builder()
        try:
            self.builder.add_from_file(os.path.join(os.getcwd(),'data','pulsecaster.ui')
)
            _debugPrint(_("loading UI file from current subdir"))
        except:
            try:
                self.builder.add_from_file(os.path.join(sys.prefix,'share','pulsecaster','pulsecaster.ui'))
            except:
                try:
                    self.builder.add_from_file(os.path.join(os.path.dirname(sys.argv[0]),
                                               'data', 'pulsecaster.ui'))
                except Exception,e:
                    print(e)
                    raise SystemExit(_("Cannot load resources"))

        self.icontheme = gtk.icon_theme_get_default()
        # Convenience for developers
        self.icontheme.append_search_path(os.path.join(os.getcwd(),'data','icons','scalable'))
        self.icontheme.append_search_path(os.path.join(os.path.dirname(sys.argv[0]),
                                          'data', 'icons', 'scalable'))
        self.logo = self.icontheme.load_icon('pulsecaster', -1,
                                             gtk.ICON_LOOKUP_FORCE_SVG)
        gtk.window_set_default_icon(self.logo)
        self.gconfig = gconfig.PulseCasterGconf()
        
        self.warning = self.builder.get_object('warning')
        self.dismiss = self.builder.get_object('dismiss_warning')
        self.swckbox = self.builder.get_object('skip_warn_checkbox')
        self.swckbox.set_active(int(self.gconfig.skip_warn))
        self.dismiss.connect('clicked', self.hideWarn)
        self.warning.connect('destroy', self.on_close)
        self.warning.set_title(NAME)
        
        # Main dialog basics
        self.main = self.builder.get_object('main_dialog')
        self.main.set_title(NAME)
        self.main_title = self.builder.get_object('main_title')
        self.main_title.set_label('<big><big><big><b><i>' +
                                  NAME + '</i></b></big></big></big>')
        self.main.connect('delete_event', self.on_close)
        self.about_button = self.builder.get_object('about_button')
        self.about_button.connect('clicked', self.showAbout)
        self.close = self.builder.get_object('close_button')
        self.close.connect('clicked', self.on_close)
        self.record = self.builder.get_object('record_button')
        self.record_id = self.record.connect('clicked', self.on_record)
        self.record.set_sensitive(True)
        self.main_logo = self.builder.get_object('logo')
        self.main_logo.set_from_icon_name('pulsecaster', gtk.ICON_SIZE_DIALOG)
        self.main.set_icon_list(self.logo)
        # About dialog basics
        self.about = self.builder.get_object('about_dialog')
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
        self.about.set_program_name(NAME)
        self.about.set_logo(self.icontheme.load_icon('pulsecaster', 96, gtk.ICON_LOOKUP_FORCE_SVG))

        # Create PulseAudio backing
        self.pa = PulseObj(clientName=NAME)

        # Create and populate combo boxes
        self.table = self.builder.get_object('table1')
        # The list stores will contain device description, a value based
        # on the sound level at the device, and whether the vu meter should
        # be updated.  (Not sure whether I'll use the last one or not.)
        self.user_vox_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT,
                                            gobject.TYPE_BOOLEAN)
        self.subject_vox_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT,
                                               gobject.TYPE_BOOLEAN)
        self.user_vox = gtk.ComboBox(self.user_vox_store)
        self.subject_vox = gtk.ComboBox(self.subject_vox_store)
        self.table.attach(self.user_vox, 1, 2, 0, 1,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.table.attach(self.subject_vox, 1, 2, 1, 2,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.user_vox.connect('button-press-event', self.repop_sources)
        self.subject_vox.connect('button-press-event', self.repop_sources)

        # Fill the combo boxes initially
        self.repop_sources()
        self.user_vox.connect('changed', self.activate_vu)
        self.subject_vox.connect('changed', self.activate_vu)
        self.listener = PulseCasterListener(self)
        
        self.filesinkpath = ''
        
        self.trayicon = gtk.StatusIcon()
        self.trayicon.set_visible(False)
        self.trayicon.set_from_icon_name('pulsecaster')

    def repop_sources(self, *args):
        self.sources = self.pa.pulse_source_list()
        self.user_vox_store.clear()
        self.subject_vox_store.clear()
        self.uservoxes = []
        self.subjectvoxes = []
        for source in self.sources:
            if source.monitor_of_sink_name == None:
                self.uservoxes.append((source.name, source.description))
                self.user_vox_store.append([source.description, 0, False])
            else:
                self.subjectvoxes.append((source.name, source.description))
                self.subject_vox_store.append([source.description, 0, False])
        # Set up cell layouts
        self.user_vox_crt = gtk.CellRendererText()
        self.subject_vox_crt = gtk.CellRendererText()
        self.user_vox_crp = gtk.CellRendererProgress()
        self.user_vox_crp.set_fixed_size(width=100, height=-1)
        self.user_vox_crp.set_property('text', '')
        self.subject_vox_crp = gtk.CellRendererProgress()
        self.subject_vox_crp.set_fixed_size(width=100, height=-1)
        self.subject_vox_crp.set_property('text', '')
        self.user_vox.pack_start(self.user_vox_crt, True)
        self.user_vox.add_attribute(self.user_vox_crt, 'text', 0)
        self.subject_vox.pack_start(self.subject_vox_crt, True)
        self.subject_vox.add_attribute(self.subject_vox_crt, 'text', 0)
        self.user_vox.pack_start(self.user_vox_crp, False)
        self.user_vox.add_attribute(self.user_vox_crp, 'value', 1)
        self.subject_vox.pack_start(self.subject_vox_crp, False)
        self.subject_vox.add_attribute(self.subject_vox_crp, 'value', 1)
        # Default choice
        # FIXME: Use the GNOME default sound setting?
        self.user_vox.set_active(0)
        self.subject_vox.set_active(0)
        # Whenever a row in the combo box is selected
        # its boolean should become True.
        # Set a gobject.timeout_add() that updates the value of the progress
        # bar according to boolean.
        self.table.show_all()

        if self.gconfig.skip_warn is False:
            self.warning.show()
        else:
            self.hideWarn()

    def activate_vu(self, cb):
        model = cb.get_model()
        entries = len(model)
        for entry in model:
            iter = entry.iter
            index = entry.path[0]
            # Set the boolean based on whether this entry is active
            model.set_value(iter, 2, index == cb.get_active())
            self.set_db(model, iter)

    def set_db(self, model, iter):
        vu_active = model.get_value(iter, 2)
        if vu_active == False:
            model.set_value(iter, 1, 0)
        else:
            # FIXME - this will build a new pipeline to get levels, and
            # set up a gobject.timeout_add() to keep riding it.
            model.set_value(iter, 1, 100)
        return vu_active

    def on_record(self, *args):
        # Create temporary file
        (self.tempfd, self.temppath) = tempfile.mkstemp(prefix='%s-tmp.' % (NAME))
        self.tempfile = os.fdopen(self.tempfd)
        _debugPrint('tempfile: %s (fd %s)' % (self.temppath, self.tempfd))
        # Adjust UI
        self.user_vox.set_sensitive(False)
        self.subject_vox.set_sensitive(False)
        self.close.set_sensitive(False)

        self.combiner = gst.Pipeline('PulseCasterCombinePipe')
        self.lsource = gst.element_factory_make('pulsesrc', 'lsrc')
        self.lsource.set_property('device', 
                                  self.uservoxes[self.user_vox.get_active()][0])
        self.rsource = gst.element_factory_make('pulsesrc', 'rsrc')
        self.rsource.set_property('device',
                                  self.subjectvoxes[self.subject_vox.get_active()][0])
        
        self.adder = gst.element_factory_make('adder', 'mix')
        self.encoder = gst.element_factory_make(self.gconfig.codec + 'enc', 'enc')
        if self.gconfig.codec == 'vorbis':
            self.muxer = gst.element_factory_make('oggmux', 'mux')
        self.filesink = gst.element_factory_make('filesink', 'fsink')
        self.filesink.set_property('location', self.temppath)

        self.combiner.add(self.lsource, 
                          self.rsource, 
                          self.adder, 
                          self.encoder,
                          self.filesink)
        if self.gconfig.codec == 'vorbis':
            self.combiner.add(self.muxer)
        gst.element_link_many(self.lsource,
                              self.adder,
                              self.encoder)
        if self.gconfig.codec == 'vorbis':
            self.encoder.link(self.muxer)
            self.muxer.link(self.filesink)
        else: # flac
            self.encoder.link(self.filesink)
        gst.element_link_many(self.rsource, self.adder)

        # FIXME: Dim elements other than the 'record' widget
        self.record.set_label(gtk.STOCK_MEDIA_STOP)
        self.record.disconnect(self.record_id)
        self.stop_id = self.record.connect('clicked', self.on_stop)
        self.record.show()
        self.combiner.set_state(gst.STATE_PLAYING)
        # Start timer
        self.starttime = datetime.now()
        self._update_time()
        self.timeout = 1000
        gobject.timeout_add(self.timeout, self._update_time)
        self.trayicon.set_visible(True)

    def on_stop(self, *args):
        self.combiner.set_state(gst.STATE_NULL)
        self.showFileChooser()
        self.record.set_label(gtk.STOCK_MEDIA_RECORD)
        self.record.disconnect(self.stop_id)
        self.record_id = self.record.connect('clicked', self.on_record)
        self.user_vox.set_sensitive(True)
        self.subject_vox.set_sensitive(True)
        self.close.set_sensitive(True)
        self.record.show()

    def on_close(self, *args):
        try:
            self.pa.disconnect()
        except:
            pass
        gtk.main_quit()

    def hideWarn(self, *args):
        self.gconfig.change_warn(self.swckbox.get_active())
        self.warning.hide()
        self.main.show()
    
    def showAbout(self, *args):
        self.about.show()

    def hideAbout(self, *args):
        self.about.hide()
        
    def showFileChooser(self, *args):
        self.file_chooser = gtk.FileChooserDialog(title=_('Save your recording'),
                                                  action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                                  buttons=('Cancel', gtk.RESPONSE_CANCEL,
                                                           'OK', gtk.RESPONSE_OK))
        self.file_chooser.set_local_only(True)
        response = self.file_chooser.run()
        if response == gtk.RESPONSE_OK:
            self.updateFileSinkPath()
        elif response == gtk.RESPONSE_CANCEL:
            self.hideFileChooser()
        elif response == gtk.RESPONSE_DELETE_EVENT:
            self.hideFileChooser()

    def hideFileChooser(self, *args):
        if not self.filesinkpath:
            confirm = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                        buttons=gtk.BUTTONS_YES_NO,
                                        message_format=_('Are you sure you want to cancel ' + 
                                                         'saving your work? If you choose "Yes" ' +
                                                         'your audio recording will be erased ' +
                                                         'permanently.'))
            response = confirm.run()
            confirm.destroy()
            if response == gtk.RESPONSE_YES:
                self._remove_tempfile(self.tempfile, self.temppath)
            else:
                return
        self.file_chooser.destroy()

    def updateFileSinkPath(self, *args):
        self.filesinkpath = self.file_chooser.get_filename()
        if not self.filesinkpath:
            return
        self.hideFileChooser()
        if os.path.lexists(self.filesinkpath):
            if not self._confirm_overwrite():
                self.showFileChooser()
                return
        # Copy the temporary file to its new home
        self._copy_temp_to_perm()
        self._remove_tempfile(self.tempfile, self.temppath)
        self.record.set_sensitive(True)
    
    def _update_time(self, *args):
        if self.combiner.get_state()[1] == gst.STATE_NULL:
            self.trayicon.set_tooltip_text('')
            self.trayicon.set_visible(False)
            return False
        delta = datetime.now() - self.starttime
        deltamin = delta.seconds // 60
        deltasec = delta.seconds - (deltamin * 60)
        self.trayicon.set_tooltip_text('Recording: %d:%02d' %
                                  (deltamin, deltasec))
        return True

    def _confirm_overwrite(self, *args):
        confirm = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                                    buttons=gtk.BUTTONS_YES_NO,
                                    message_format=_('File exists. OK to overwrite?'))
        response = confirm.run()
        if response == gtk.RESPONSE_YES:
            retval = True
        else:
            retval = False
        confirm.destroy()
        return retval
    
    def _copy_temp_to_perm(self):
        self.permfile = open(self.filesinkpath, 'w')
        self.tempfile.seek(0)
        while True:
            buf = self.tempfile.read(1024*1024)
            if buf:
                self.permfile.write(buf)
            else:
                break
        self.permfile.close()

    def _remove_tempfile(self, tempfile, temppath):
        tempfile.close()
        os.remove(temppath)


if __name__ == '__main__':
    pulseCaster = PulseCasterUI()
    gtk.main()
