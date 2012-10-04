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
from source import *
from gi.repository import Gtk, GObject
import os
import sys
import tempfile
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
        self.builder = Gtk.Builder()
        try:
            self.builder.add_from_file(os.path.join(os.getcwd(),
                                                    'data',
                                                    'pulsecaster.ui')
)
            _debugPrint(_("loading UI file from current subdir"))
        except:
            try:
                self.builder.add_from_file(os.path.join(sys.prefix,
                                                        'share',
                                                        'pulsecaster',
                                                        'pulsecaster.ui'))
            except:
                try:
                    self.builder.add_from_file(os.path.join
                                               (os.path.dirname(sys.argv[0]),
                                                'data', 'pulsecaster.ui'))
                except Exception,e:
                    print(e)
                    raise SystemExit(_("Cannot load resources"))

        self.icontheme = Gtk.IconTheme.get_default()
        # Convenience for developers
        self.icontheme.append_search_path(os.path.join(os.getcwd(),
                                                       'data',
                                                       'icons',
                                                       'scalable'))
        self.icontheme.append_search_path(os.path.join
                                          (os.path.dirname(sys.argv[0]),
                                           'data', 'icons', 'scalable'))
        self.logo = self.icontheme.load_icon('pulsecaster', -1,
                                             Gtk.IconLookupFlags.FORCE_SVG)
        Gtk.Window.set_default_icon(self.logo)
        self.gconfig = gconfig.PulseCasterGconf()
        
        self.warning = self.builder.get_object('warning')
        self.dismiss = self.builder.get_object('dismiss_warning')
        self.swckbox = self.builder.get_object('skip_warn_checkbox')
        self.swckbox.set_active(int(self.gconfig.skip_warn))
        self.dismiss.connect('clicked', self.hideWarn)
        self.warning.connect('destroy', self.on_close)
        self.warning.set_title(NAME)
        
        # Miscellaneous dialog strings
        s = _('Important notice')
        self.builder.get_object('warning-label2').set_label('<big><big>'+
                                                            '<b><i>'+
                                                            s+
                                                            '</i></b>'+
                                                            '</big></big>')
        s = _('This program can be used to record speech from remote ' +
              'locations. You are responsible for adhering to all '+
              'applicable laws and regulations when using this program. '+
              'In general you should not record other parties without '+
              'their consent.')
        self.builder.get_object('warning-label3').set_label(s)
        s = _('Do not show this again')
        self.builder.get_object('skip_warn_checkbox').set_label(s)
        s = _('Select the audio sources to mix')
        self.builder.get_object('label2').set_label(s)
        s = _('I understand.')
        self.builder.get_object('dismiss_warning').set_label(s)
        s = _('Your voice')
        self.builder.get_object('label3').set_label(s + ':')
        s = _('Subject\'s voice')
        self.builder.get_object('label4').set_label(s + ':')

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
        self.main_logo.set_from_icon_name('pulsecaster', Gtk.IconSize.DIALOG)
        self.main.set_icon_list([self.logo])
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
        self.about.set_logo(self.icontheme.load_icon
                            ('pulsecaster', 96, Gtk.IconLookupFlags.FORCE_SVG))

        # Create PulseAudio backing
        self.pa = PulseObj(clientName=NAME)

        # Create and populate combo boxes
        self.table = self.builder.get_object('table1')
        self.user_vox = PulseCasterSource()
        self.subject_vox = PulseCasterSource()

        self.table.set_col_spacing(2, 120)
        self.table.attach(self.user_vox.cbox, 1, 2, 0, 1,
                          xoptions=Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        self.table.attach(self.subject_vox.cbox, 1, 2, 1, 2,
                          xoptions=Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        self.table.attach(self.user_vox.pbar, 2, 3, 0, 1,
                          xoptions=Gtk.AttachOptions.FILL)
        self.table.attach(self.subject_vox.pbar, 2, 3, 1, 2,
                          xoptions=Gtk.AttachOptions.FILL)
        self.user_vox.cbox.connect('button-press-event',
                                   self.user_vox.repopulate,
                                   self.pa)
        self.subject_vox.cbox.connect('button-press-event',
                                      self.subject_vox.repopulate,
                                      self.pa)

        # Fill the combo boxes initially
        self.repop_sources()
        self.user_vox.cbox.set_active(0)
        self.subject_vox.cbox.set_active(0)
        self.table.show_all()

        self.listener = PulseCasterListener(self)
        self.filesinkpath = ''
        self.trayicon = Gtk.StatusIcon()
        self.trayicon.set_visible(False)
        self.trayicon.set_from_icon_name('pulsecaster')

        if self.gconfig.skip_warn is False:
            self.warning.show()
        else:
            self.hideWarn()

    def repop_sources(self, *args):
        self.main.set_sensitive(False)
        self.user_vox.repopulate(self.pa, use_source=True,
                                 use_monitor=False)
        self.subject_vox.repopulate(self.pa, use_source=False,
                                    use_monitor=True)
        self.table.show_all()
        self.main.set_sensitive(True)

    def on_record(self, *args):
        # Create temporary file
        (self.tempfd, self.temppath) = tempfile.mkstemp(prefix='%s-tmp.'
                                                        % (NAME))
        self.tempfile = os.fdopen(self.tempfd)
        _debugPrint('tempfile: %s (fd %s)' % (self.temppath, self.tempfd))
        # Adjust UI
        self.user_vox.cbox.set_sensitive(False)
        self.subject_vox.cbox.set_sensitive(False)
        self.close.set_sensitive(False)

        self.combiner = gst.Pipeline('PulseCasterCombinePipe')
        self.lsource = gst.element_factory_make('pulsesrc', 'lsrc')
        self.lsource.set_property('device', self.user_vox.pulsesrc)
        self.rsource = gst.element_factory_make('pulsesrc', 'rsrc')
        self.rsource.set_property('device', self.subject_vox.pulsesrc)
        
        self.adder = gst.element_factory_make('adder', 'mix')
        self.encoder = gst.element_factory_make(self.gconfig.codec + 'enc',
                                                'enc')
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
        self.record.set_label(Gtk.STOCK_MEDIA_STOP)
        self.record.disconnect(self.record_id)
        self.stop_id = self.record.connect('clicked', self.on_stop)
        self.record.show()
        self.combiner.set_state(gst.STATE_PLAYING)
        # Start timer
        self.starttime = datetime.now()
        self._update_time()
        self.timeout = 1000
        GObject.timeout_add(self.timeout, self._update_time)
        self.trayicon.set_visible(True)

    def on_stop(self, *args):
        self.combiner.set_state(gst.STATE_NULL)
        self.showFileChooser()
        self.record.set_label(Gtk.STOCK_MEDIA_RECORD)
        self.record.disconnect(self.stop_id)
        self.record_id = self.record.connect('clicked', self.on_record)
        self.user_vox.cbox.set_sensitive(True)
        self.subject_vox.cbox.set_sensitive(True)
        self.close.set_sensitive(True)
        self.record.show()

    def on_close(self, *args):
        try:
            self.pa.disconnect()
        except:
            pass
        Gtk.main_quit()

    def hideWarn(self, *args):
        self.gconfig.change_warn(self.swckbox.get_active())
        self.warning.hide()
        self.main.show()
    
    def showAbout(self, *args):
        self.about.show()

    def hideAbout(self, *args):
        self.about.hide()
        
    def showFileChooser(self, *args):
        self.file_chooser = Gtk.FileChooserDialog(title=_('Save your recording'),
                                                  action=Gtk.FileChooserAction.SAVE,
                                                  buttons=('Cancel', 
                                                           Gtk.ResponseType.CANCEL,
                                                           'OK',
                                                           Gtk.ResponseType.OK))
        self.file_chooser.set_local_only(True)
        response = self.file_chooser.run()
        if response == Gtk.ResponseType.OK:
            self.updateFileSinkPath()
        elif response == Gtk.ResponseType.CANCEL:
            self.hideFileChooser()
        elif response == Gtk.ResponseType.DELETE_EVENT:
            self.hideFileChooser()

    def hideFileChooser(self, *args):
        if not self.filesinkpath:
            confirm_message=_('Are you sure you want to cancel saving '+
                              'your work? If you choose Yes your audio '+
                              'recording will be erased permanently.')
            confirm = Gtk.MessageDialog(type=Gtk.MessageType.WARNING,
                                        buttons=Gtk.ButtonsType.YES_NO,
                                        message_format=confirm_message)
            response = confirm.run()
            confirm.destroy()
            if response == Gtk.ResponseType.YES:
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
        confirm_message = _('File exists. OK to overwrite?')
        confirm = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                                    buttons=Gtk.ButtonsType.YES_NO,
                                    message_format=confirm_message)
        response = confirm.run()
        if response == Gtk.ResponseType.YES:
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
    Gtk.main()
