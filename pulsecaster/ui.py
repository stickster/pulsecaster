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
import gsettings
from pulseaudio.PulseObj import PulseObj
from listener import *
from source import *
from gi.repository import Gtk, GObject, Gst
import os
import sys
import tempfile
from datetime import datetime

import gettext
gettext.install(LNAME)

def _debugPrint(text):
    if _debug:
        print ('%s: %s' % (NAME, text))

class PulseCasterUI(Gtk.Application):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(NAME)
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

        self.tempgsettings = Gtk.Settings.get_default()
        self.tempgsettings.set_property('gtk-application-prefer-dark-theme',
                                    True)
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
        self.gsettings = gsettings.PulseCasterGSettings()
        
        self.warning = self.builder.get_object('warning')
        self.dismiss = self.builder.get_object('dismiss_warning')
        self.swckbox = self.builder.get_object('skip_warn_checkbox')
        self.swckbox.set_active(int(self.gsettings.skip_warn))
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
        self.adv_button = self.builder.get_object('adv_button')
        self.adv_button.connect('clicked', self.showAdv)
        self.close = self.builder.get_object('close_button')
        self.close.connect('clicked', self.on_close)
        self.record = self.builder.get_object('record_button')
        self.record_id = self.record.connect('clicked', self.on_record)
        self.record.set_sensitive(True)
        self.main_logo = self.builder.get_object('logo')
        self.main_logo.set_from_icon_name('pulsecaster', Gtk.IconSize.DIALOG)
        self.main.set_icon_list([self.logo])
        # Advanced dialog basics
        self.adv = self.builder.get_object('adv_dialog')
        self.adv.set_icon_list([self.logo])
        self.adv.set_title(NAME)
        self.adv.connect('delete_event', self.hideAdv)
        self.adv.connect('response', self.hideAdv)
        self.adv_stdlabel1 = self.builder.get_object('adv_stdlabel1')
        self.adv_stdlabel2 = self.builder.get_object('adv_stdlabel2')
        self.adv_explabel1 = self.builder.get_object('adv_explabel1')
        self.adv_explabel2 = self.builder.get_object('adv_explabel2')
        self.adv_stdlabel1.set_label(_('Standard settings'))
        self.adv_explabel1.set_label(_('Expert settings'))
        lbl = _('Save the conversation as a single audio file with compression. This is the right option for most people.')
        self.adv_stdlabel2.set_label('<small><i>' + lbl + '</i></small>')
        lbl = _('Save each voice as a separate audio file without compression. Use this option to mix and encode audio yourself.')
        self.adv_explabel2.set_label('<small><i>' + lbl + '</i></small>')
        # TODO: Add bits to set radio buttons and make them work
        self.vorbis_button = self.builder.get_object('vorbis_button')
        self.vorbis_button.connect('clicked', self.set_standard)
        self.flac_button = self.builder.get_object('flac_button')
        self.flac_button.connect('clicked', self.set_expert)
        self.flac_button.join_group(self.vorbis_button)
        if self.gsettings.expert is True:
            self.flac_button.set_active(True)
        else:
            self.vorbis_button.set_active(True)
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

        self.table.attach(self.user_vox.cbox, 1, 0, 1, 1)
        self.table.attach(self.subject_vox.cbox, 1, 1, 1, 1)
        self.table.attach(self.user_vox.pbar, 2, 0, 1, 1)
        self.table.attach(self.subject_vox.pbar, 2, 1, 1, 1)
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

        if self.gsettings.skip_warn is False:
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
        # Adjust UI
        self.user_vox.cbox.set_sensitive(False)
        self.subject_vox.cbox.set_sensitive(False)
        self.close.set_sensitive(False)
        self.adv_button.set_sensitive(False)

        self.combiner = Gst.Pipeline()
        self.lsource = Gst.ElementFactory.make('pulsesrc', 'lsrc')
        self.lsource.set_property('device', self.user_vox.pulsesrc)
        self.rsource = Gst.ElementFactory.make('pulsesrc', 'rsrc')
        self.rsource.set_property('device', self.subject_vox.pulsesrc)

        self._default_caps = Gst.Caps.from_string('audio/x-raw-int, '
                                                  'rate=(int)%d' % 
                                                  (self.gsettings.audiorate))
        self.adder = Gst.ElementFactory.make('adder', 'mix')
        self.lfilter = Gst.ElementFactory.make('capsfilter', 'lfilter')
        self.rfilter = Gst.ElementFactory.make('capsfilter', 'rfilter')
        _debugPrint('audiorate: %d' % self.gsettings.audiorate)

        if self.gsettings.expert is not True:
            # Create temporary file
            (self.tempfd, self.temppath) = tempfile.mkstemp(prefix='%s-tmp.'
                                                            % (NAME))
            self.tempfile = os.fdopen(self.tempfd)
            _debugPrint('tempfile: %s (fd %s)' % (self.temppath, self.tempfd))
            self.encoder = Gst.ElementFactory.make(self.gsettings.codec +
                                                    'enc', 'enc')
            if self.gsettings.codec == 'vorbis':
                self.muxer = Gst.ElementFactory.make('oggmux', 'mux')
            self.filesink = Gst.ElementFactory.make('filesink', 'fsink')
            self.filesink.set_property('location', self.temppath)

            for e in (self.lsource,
                      self.lfilter,
                      self.rsource,
                      self.rfilter,
                      self.adder,
                      self.encoder,
                      self.filesink):
                self.combiner.add(e)
            if self.gsettings.codec == 'vorbis':
                self.combiner.add(self.muxer)
            self.lsource.link(self.lfilter)
            self.lfilter.link(self.adder)
            self.adder.link(self.encoder)
            if self.gsettings.codec == 'vorbis':
                self.encoder.link(self.muxer)
                self.muxer.link(self.filesink)
            else: # flac
                self.encoder.link(self.filesink)
            self.rsource.link(self.rfilter)
            self.rfilter.link(self.adder)
        else:
            # Create temporary file
            (self.tempfd1, self.temppath1) = tempfile.mkstemp(prefix='%s-1-tmp.'
                                                              % (NAME))
            (self.tempfd2, self.temppath2) = tempfile.mkstemp(prefix='%s-2-tmp.'
                                                              % (NAME))
            self.tempfile1 = os.fdopen(self.tempfd1)
            self.tempfile2 = os.fdopen(self.tempfd2)
            _debugPrint('tempfiles: %s (fd %s), %s (fd %s)' %
                        (self.temppath1, self.tempfd1, self.temppath2,
                         self.temppath2))
            # We're in expert mode
            # Disregard vorbis, use WAV
            self.encoder1 = Gst.ElementFactory.make('wavenc', 'enc1')
            self.encoder2 = Gst.ElementFactory.make('wavenc', 'enc2')
            self.filesink1 = Gst.ElementFactory.make('filesink', 'fsink1')
            self.filesink1.set_property('location', self.temppath1)
            self.filesink2 = Gst.ElementFactory.make('filesink', 'fsink2')
            self.filesink2.set_property('location', self.temppath2)
            for e in (self.lsource,
                      self.lfilter,
                      self.rsource,
                      self.rfilter,
                      self.encoder1,
                      self.encoder2,
                      self.filesink1,
                      self.filesink2):
                self.combiner.add(e)
            self.lsource.link(self.lfilter)
            self.lfilter.link(self.encoder1)
            self.encoder1.link(self.filesink1)
            self.rsource.link(self.rfilter)
            self.rfilter.link(self.encoder2)
            self.encoder2.link(self.filesink2)

        # FIXME: Dim elements other than the 'record' widget
        self.record.set_label(Gtk.STOCK_MEDIA_STOP)
        self.record.disconnect(self.record_id)
        self.stop_id = self.record.connect('clicked', self.on_stop)
        self.record.show()
        self.combiner.set_state(Gst.State.PLAYING)
        # Start timer
        self.starttime = datetime.now()
        self._update_time()
        self.timeout = 1000
        GObject.timeout_add(self.timeout, self._update_time)
        self.trayicon.set_visible(True)

    def on_stop(self, *args):
        self.combiner.set_state(Gst.State.NULL)
        self.showFileChooser()
        self.record.set_label(Gtk.STOCK_MEDIA_RECORD)
        self.record.disconnect(self.stop_id)
        self.record_id = self.record.connect('clicked', self.on_record)
        self.user_vox.cbox.set_sensitive(True)
        self.subject_vox.cbox.set_sensitive(True)
        self.close.set_sensitive(True)
        self.adv_button.set_sensitive(True)
        self.record.show()

    def on_close(self, *args):
        try:
            self.pa.disconnect()
        except:
            pass
        Gtk.main_quit()

    def hideWarn(self, *args):
        self.gsettings.change_warn(self.swckbox.get_active())
        self.warning.hide()
        self.main.show()
    
    def showAbout(self, *args):
        self.about.show()

    def hideAbout(self, *args):
        self.about.hide()

    def showAdv(self, *args):
        if self.gsettings.expert is True:
            self.flac_button.set_active(True)
        else:
            self.vorbis_button.set_active(True)
        self.adv.show()

    def hideAdv(self, *args):
        self.adv.hide()

    def set_standard(self, *args):
        self.gsettings.gsettings.set_boolean('expert', False)
        self.gsettings.gsettings.set_string('codec', 'vorbis')
        self.gsettings.expert = False
        self.gsettings.gsettings.sync()

    def set_expert(self, *args):
        self.gsettings.gsettings.set_boolean('expert', True)
        self.gsettings.gsettings.set_string('codec', 'flac')
        self.gsettings.expert = True
        self.gsettings.gsettings.sync()

    def showFileChooser(self, *args):
        self.file_chooser = Gtk.FileChooserDialog(title=_('Save your recording'),
                                                  action=Gtk.FileChooserAction.SAVE,
                                                  buttons=(Gtk.STOCK_CANCEL,
                                                           Gtk.ResponseType.CANCEL,
                                                           Gtk.STOCK_OK,
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
                if self.gsettings.expert is False:
                    self._remove_tempfile(self.tempfile, self.temppath)
                else:
                    self._remove_tempfile(self.tempfile1, self.temppath1)
                    self._remove_tempfile(self.tempfile2, self.temppath2)
            else:
                return
        self.file_chooser.destroy()

    def updateFileSinkPath(self, *args):
        self.filesinkpath = self.file_chooser.get_filename()
        if not self.filesinkpath:
            return
        self.hideFileChooser()
        if self.gsettings.expert is False:
            if not self.filesinkpath.endswith('.ogg'):
                self.filesinkpath += '.ogg'
            if os.path.lexists(self.filesinkpath):
                if not self._confirm_overwrite():
                    self.showFileChooser()
                    return
        else:
            if os.path.lexists(self.filesinkpath+'-1.wav') or \
                    os.path.lexists(self.filesinkpath+'-2.wav'):
                if not self._confirm_overwrite():
                    self.showFileChooser()
                    return
        # Copy the temporary file to its new home
        self._copy_temp_to_perm()
        if self.gsettings.expert is False:
            self._remove_tempfile(self.tempfile, self.temppath)
        else:
            expert_message = _('WAV files are written here:')
            expert_message += '\n%s\n%s' % (self.filesinkpath+'-1.wav',
                                            self.filesinkpath+'-2.wav')
            expertdlg = Gtk.MessageDialog(type=Gtk.MessageType.INFO,
                                          buttons=Gtk.ButtonsType.OK,
                                          message_format=expert_message)
            response = expertdlg.run()
            expertdlg.destroy()
            self._remove_tempfile(self.tempfile1, self.temppath1)
            self._remove_tempfile(self.tempfile2, self.temppath2)
        self.record.set_sensitive(True)
    
    def _update_time(self, *args):
        if self.combiner.get_state(Gst.CLOCK_TIME_NONE)[1] == Gst.State.NULL:
            self.trayicon.set_tooltip_text('')
            self.trayicon.set_visible(False)
            return False
        delta = datetime.now() - self.starttime
        deltamin = delta.seconds // 60
        deltasec = delta.seconds - (deltamin * 60)
        self.trayicon.set_tooltip_text(_('Recording') + ': %d:%02d' %
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
        # This is a really stupid way to do this.
        # FIXME: abstract out the duplicated code, lazybones.
        if self.gsettings.expert is False:
            self.permfile = open(self.filesinkpath, 'w')
            self.tempfile.seek(0)
            while True:
                buf = self.tempfile.read(1024*1024)
                if buf:
                    self.permfile.write(buf)
                else:
                    break
            self.permfile.close()
        else:
            self.permfile1 = open(self.filesinkpath + '-1.wav', 'w')
            self.permfile2 = open(self.filesinkpath + '-2.wav', 'w')
            for pf, tf in ([1, self.tempfile1], [2, self.tempfile2]):
                permfile = open(self.filesinkpath + '-%d.wav' % (pf), 'w')
                while True:
                    buf = tf.read(1024*1024)
                    if buf:
                        permfile.write(buf)
                    else:
                        break
                permfile.close()

    def _remove_tempfile(self, tempfile, temppath):
        tempfile.close()
        os.remove(temppath)


if __name__ == '__main__':
    pulseCaster = PulseCasterUI()
    Gtk.main()
