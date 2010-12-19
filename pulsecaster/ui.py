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
import gconfig
from pulseaudio.PulseObj import PulseObj
from listener import *
import gtk
import os
import sys
import tempfile
import glob
import gobject
import pygst
pygst.require('0.10')
import gst

import gettext
_ = lambda x: gettext.ldgettext(NAME, x)

_debug = True

def _debugPrint(text):
    if _debug:
        print (text)

class PulseCasterUI:
    def __init__(self):
        self.builder = gtk.Builder()
        try:
            self.builder.add_from_file(os.path.join(os.getcwd(),'data','pulsecaster.glade')
)
            _debugPrint(_("loading glade file from current subdir"))
        except:
            try:
                self.builder.add_from_file(os.path.join(sys.prefix,'share','pulsecaster','pulsecaster.glade'))
            except Exception,e:
                print(e)
                raise SystemExit(_("Cannot load resources"))

        self.icontheme = gtk.icon_theme_get_default()
        
        # Convenience for developers
        self.icontheme.append_search_path(os.path.join(os.getcwd(),'data','icons','scalable'))
        self.icontheme.append_search_path(os.path.join(sys.prefix,'share','pulsecaster','icons','scalable'))
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

        self.file_chooser = self.builder.get_object('file_chooser')
        self.file_chooser_cancel_button = self.builder.get_object('file_chooser_cancel_button')
        self.file_chooser_cancel_button.connect('clicked', self.hideFileChooser)
        self.file_chooser_save_button = self.builder.get_object('file_chooser_save_button')
        self.file_chooser_save_button.connect('clicked', self.updateFileSinkPath)
        self.file_chooser.set_do_overwrite_confirmation(True)
        self.file_chooser.connect('confirm-overwrite', self._confirm_overwrite)

        # Create PulseAudio backing
        self.pa = PulseObj(clientName=NAME)

        # Create and populate combo boxes
        self.table = self.builder.get_object('table1')
        self.user_vox = gtk.combo_box_new_text()
        self.subject_vox = gtk.combo_box_new_text()
        self.table.attach(self.user_vox, 1, 2, 0, 1,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.table.attach(self.subject_vox, 1, 2, 1, 2,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.user_vox.connect('button-press-event', self.repop_sources)
        self.subject_vox.connect('button-press-event', self.repop_sources)

        # Fill the combo boxes initially
        self.repop_sources()
        self.listener = PulseCasterListener(self)
        
        self.filesinkpath = ''
        
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
        self.table.show_all()

        if self.gconfig.skip_warn is False:
            self.warning.show()
        else:
            self.hideWarn()

    def on_record(self, *args):
        # Create temporary file
        (self.tempfd, self.temppath) = tempfile.mkstemp(prefix='%s-tmp.' % (NAME))
        self.tempfile = os.fdopen(self.tempfd)
        _debugPrint('%s (%s)' % (self.temppath, self.tempfd))
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
        self.file_chooser.show()

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
        self.file_chooser.hide()

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
        self.permfile = open(self.filesinkpath, 'w')
        self._copy_temp_to_perm(self.tempfile, self.permfile)
        self.permfile.close()
        self._remove_tempfile(self.tempfile, self.temppath)
        self.record.set_sensitive(True)

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
    
    def _copy_temp_to_perm(self, src, dest):
        src.seek(0)
        while True:
            buf = src.read(1024*1024)
            if buf:
                dest.write(buf)
            else:
                break

    def _remove_tempfile(self, tempfile, temppath):
        tempfile.close()
        os.remove(temppath)
if __name__ == '__main__':
    pulseCaster = PulseCasterUI()
    gtk.main()
