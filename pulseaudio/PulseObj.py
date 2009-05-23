#!/usr/bin/python
# vi: et sw=2
#
# PulseObj.py
# Copyright (C) 2009  Harry Karvonen
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
# Author: Harry Karvonen <harry.karvonen@gmail.com>
#

from lib_pulseaudio import *
from PulseSink      import PulseSinkInputInfo, PulseSinkInfo
from PulseSource    import PulseSourceOutputInfo, PulseSourceInfo
from PulseClient    import PulseClientCtypes

################################################################################
#
# Classes
#
################################################################################

class PulseObj:
  "Basic PulseAudio object"

  ##############################################################################
  #
  # Init
  #
  ##############################################################################

  def __init__(self, server = None, retry = False):
    "Initialise pulseaudio connection"

    # Variables
    self.server       = server
    self.mainloop     = None
    self.mainloop_api = None
    self.context      = None
    self.ret          = None
    self.retry        = retry
    self.operation    = None
    self.connected    = False
    self.action_done  = False
    self.data         = None

    # Init

    #
    # Callbacks
    #
    self.PA_SIGNAL_CB = PA_SIGNAL_CB_T(self.py_signal_cb)

    self.PA_STATE_CB = PA_STATE_CB_T(self.py_state_cb)
    #
    # Mainloop init
    #
    self.mainloop = pa_mainloop_new()

    self.mainloop_api = pa_mainloop_get_api(self.mainloop)

    #
    # Signal binding
    #
    r = pa_signal_init(self.mainloop_api)

    if r != 0:
      # FIXME
      print "FIXME Do something. Something is wrong"

    # SIGINT
    pa_signal_new(2, self.PA_SIGNAL_CB, None)

    # SIGTERM
    pa_signal_new(15, self.PA_SIGNAL_CB, None)

    #
    # Context creating
    #
    self.context = pa_context_new(self.mainloop_api, "PulseApplet")

    pa_context_set_state_callback(self.context, self.PA_STATE_CB, None)

    self.start_action()

    #
    # Connect
    #
    if 0 > pa_context_connect(self.context,
                              self.server,
                              0,
                              None):
        if self.retry:
          pa_context_disconnect(self.context)
          return
        self.pulse_context_error()

    self.pulse_iterate()

    return

  ##############################################################################
  #
  # Callback methods
  #
  # FIXME: rename methods better
  #
  ##############################################################################

  def py_signal_cb(self, api, e, sig, userdata):
    #print "py_signal_cb:", api, e, sig, userdata

    if sig == 2:
      self.pulse_disconnect()
    elif sig == 15:
      self.pulse_disconnect()

    return 0

  ###

  def py_state_cb(self, c, b):
    #print "py_state_cb:", c[0]._opaque_struct, b
    state = pa_context_get_state(c);


    if state == 0:
      None
      #print "py_state_cb: Unconnected"

    elif state == 1:
      None
      #print "py_state_cb: Connecting"

    elif state == 2:
      None
      #print "py_state_cb: Authorizing"

    elif state == 3:
      None
      #print "py_state_cb: Setting name"

    elif state == 4:
      #print "py_state_cb: Ready"
      self.complete_action()
      self.connected = True

    elif state == 5:
      None
      #print "py_state_cb: Failed"

    elif state == 6:
      None
      #print "py_state_cb: Terminated"
      if not self.retry:
        import sys
        sys.exit(pa_context_errno(c))

      self.complete_action()

    else:
      None
      #print "py_state_cb: Unknown state", state


    #print "py_state_cb:", pa_strerror(pa_context_errno(c))
    return 0

  ###

  def py_client_cb(self, c, client_info, endofdata, userdata):
    "Sink callback"
    #print "py_client_cb:", c, client_info, endofdata, userdata

    if (endofdata):
      self.complete_action()
      return 0

    if self.data == None:
      self.data = [ PulseClientCtypes(client_info[0]) ]
    else:
      self.data.append(PulseClientCtypes(client_info[0]))

    return 0

  ###

  def py_sink_input_cb(self, c, sink_input_info, endofdata, userdata):
    "Sink input callback"
    #print "py_sink_input_cb:", c, sink_input_info, endofdata, userdata

    if (endofdata):
      self.complete_action()
      return 0

    if self.data == None:
      self.data = [ PulseSinkInputInfo(sink_input_info[0]) ]
    else:
      self.data.append(PulseSinkInputInfo(sink_input_info[0]))

    return 0

  ###

  def py_sink_cb(self, c, sink_info, endofdata, userdata):
    "Sink callback"
    #print "py_sink_cb:", c, sink_info, endofdata, userdata

    if (endofdata):
      self.complete_action()
      return 0

    if self.data == None:
      self.data = [ PulseSinkInfo(sink_info[0]) ]
    else:
      self.data.append(PulseSinkInfo(sink_info[0]))

    return 0
  ###

  def py_source_output_cb(self, c, source_output_info, endofdata, userdata):
    "Source output callback"
    #print "py_source_output_cb:", c, source_output_info, endofdata, userdata

    if (endofdata):
      self.complete_action()
      return 0

    if self.data == None:
      self.data = [ PulseSourceOutputInfo(source_output_info[0]) ]
    else:
      self.data.append(PulseSourceOutputInfo(source_output_info[0]))

    return 0

  ###

  def py_source_cb(self, c, source_info, endofdata, userdata):
    "Source callback"
    #print "py_source_cb:", c, source_info, endofdata, userdata

    if (endofdata):
      self.complete_action()
      return 0

    if self.data == None:
      self.data = [ PulseSourceInfo(source_info[0]) ]
    else:
      self.data.append(PulseSourceInfo(source_info[0]))

    return 0
  ###

  def py_drain_cb(self, c, userdata):
    #print "py_drain_cb: called"
    return

  ###

  def py_context_success(self, c, success, userdata):
    if success == 0:
      None
      #print "py_context_success: Failed"
    else:
      None
      #print "py_context_success: Success"

    self.complete_action()
    return 0

  ##############################################################################
  #
  ##############################################################################

  def complete_action(self):
    "Completed action"
    #print "complete_action: Called"
    self.action_done = True
    return

  ###

  def start_action(self):
    "Call every time when starting action"
    #print "start_action: Called"
    self.action_done = False
    return

  ###

  def pulse_disconnect(self):
    "Call when disconnect object"

    #print "pulse_disconnect: Disconnecting"
    pa_context_disconnect(self.context)
    pa_mainloop_free(self.mainloop)
    return

  ###

  def pulse_context_error(self):
    "Print context error msg"

    #print "pulse_context_error:", pa_strerror(pa_context_errno(self.context))
    self.pulse_disconnect()
    return

  ###

  def pulse_sink_input_list(self):
    "List all sink input"
    #print "pulse_sink_input_list: Called";

    return_data = None

    self.start_action()

    # Callback function
    SINK_INPUT_LIST_CB = PA_SINK_INPUT_INFO_CB_T(self.py_sink_input_cb)

    self.operation = pa_context_get_sink_input_info_list(self.context,
                                                         SINK_INPUT_LIST_CB,
                                                         None)
    self.pulse_iterate()
                        
    #print "pulse_sink_input_list:", self.data
    return_data = self.data
    self.data = None

    return return_data

  ###

  def pulse_sink_list(self):
    "List all sinks"
    #print "pulse_sink_list: Called";

    return_data = None

    self.start_action()

    # Callback function
    SINK_LIST_CB = PA_SINK_INFO_CB_T(self.py_sink_cb)

    self.operation = pa_context_get_sink_info_list(self.context,
                                                   SINK_LIST_CB,
                                                   None)
    self.pulse_iterate()
                        
    #print "pulse_sink_list:", self.data
    return_data = self.data
    self.data = None

    return return_data

  ###

  def pulse_source_output_list(self):
    "List all source outputs"
    #print "pulse_source_output_list: Called";

    return_data = None

    self.start_action()

    # Callback function
    SOURCE_OUTPUT_LIST_CB = PA_SOURCE_OUTPUT_INFO_CB_T(self.py_source_output_cb)

    self.operation = pa_context_get_source_output_info_list(self.context,
                                                            SOURCE_OUTPUT_LIST_CB,
                                                            None)
    self.pulse_iterate()
                        
    #print "pulse_source_output_list:", self.data
    return_data = self.data
    self.data = None

    return return_data

  ###

  def pulse_source_list(self):
    "List all sources"
    #print "pulse_source_list: Called";

    return_data = None

    self.start_action()

    # Callback function
    SOURCE_LIST_CB = PA_SOURCE_INFO_CB_T(self.py_source_cb)

    self.operation = pa_context_get_source_info_list(self.context,
                                                     SOURCE_LIST_CB,
                                                     None)
    self.pulse_iterate()
                        
    #print "pulse_source_list:", self.data
    return_data = self.data
    self.data = None

    return return_data

  ###
  def pulse_client_list(self):
    "Fetch all clients"

    self.start_action()

    CLIENT_INFO_CB = PA_CLIENT_INFO_CB_T(self.py_client_cb)

    self.operation = pa_context_get_client_info_list(self.context,
                                                     CLIENT_INFO_CB,
                                                     None)

    self.pulse_iterate()

    #print "pulse_client_list:", self.data
    return_data = self.data
    self.data = None

    return return_data

  ###

  def pulse_sink_input_mute(self, index, mute):
    "Mute one stream by index"

    self.start_action()

    CONTEXT_SUCCESS = PA_CONTEXT_SUCCESS_CB_T(self.py_context_success)

    self.operation = pa_context_set_sink_input_mute(self.context,
                                                    index,
                                                    mute, # Mute = 1
                                                    CONTEXT_SUCCESS,
                                                    None)

    self.pulse_iterate()

    return

  ###

  def pulse_sink_mute(self, index, mute):
    "Mute sink by index"

    self.start_action()

    CONTEXT_SUCCESS = PA_CONTEXT_SUCCESS_CB_T(self.py_context_success)

    self.operation = pa_context_set_sink_mute_by_index(self.context,
                                                       index,
                                                       mute, # Mute = 1
                                                       CONTEXT_SUCCESS,
                                                       None)

    self.pulse_iterate()

    return

  ###

  def pulse_mute_stream(self, index):
    self.pulse_sink_input_mute(index, 1)
    return

  ###

  def pulse_unmute_stream(self, index):
    self.pulse_sink_input_mute(index, 0)
    return

  ###

  def pulse_mute_sink(self, index):
    self.pulse_sink_mute(index, 1)
    return

  ###

  def pulse_unmute_sink(self, index):
    self.pulse_sink_mute(index, 0)
    return

  ###

  def pulse_set_sink_input_volume(self, index, vol):
    "Set volume by index"
    self.start_action()

    #print "pulse_set_sink_input_volume:", index, "Vol:", vol

    #print vol.values
    #for a in vol.toCtypes().values:
    #  print a
    #return

    PA_CONTEXT_SUCCESS_CB = PA_CONTEXT_SUCCESS_CB_T(self.py_context_success)

    self.opertarion = pa_context_set_sink_input_volume(self.context,
                                                       index,
                                                       vol.toCtypes(),
                                                       PA_CONTEXT_SUCCESS_CB,
                                                       None)

    self.pulse_iterate()

    return

  ###

  def pulse_set_sink_volume(self, index, vol):
    "Set volume by index"
    self.start_action()

    #print "pulse_set_sink_volume:", index, "Vol:", vol

    PA_CONTEXT_SUCCESS_CB = PA_CONTEXT_SUCCESS_CB_T(self.py_context_success)

    self.opertarion = pa_context_set_sink_volume_by_index(self.context,
                                                          index,
                                                          vol.toCtypes(),
                                                          PA_CONTEXT_SUCCESS_CB,
                                                          None)

    self.pulse_iterate()

    return

  ###

  def reconnect(self):
    self.context = pa_context_new(self.mainloop_api, "PulseApplet")

    pa_context_set_state_callback(self.context, self.PA_STATE_CB, None)

    self.start_action()


    if 0 > pa_context_connect(self.context,
                              self.server,
                              0,
                              None):
        if self.retry:
          pa_context_disconnect(self.context)
          #print "bar"
          return
        self.pulse_context_error()
        #print "foo"

    self.pulse_iterate()

    return

  ###

  def pulse_iterate(self, times = 1):
    "Runs queries"
    #print "pulse_iterate: Called"
    self.ret = pointer(c_int())

    pa_mainloop_iterate(self.mainloop, times, self.ret)

    while not self.action_done:
      pa_mainloop_iterate(self.mainloop, times, self.ret)

    return

  ###

  def pulse_run(self):
    self.ret = pointer(c_int(0))

    #pa_mainloop_iterate(self.mainloop, 11, self.ret)
    pa_mainloop_run(self.mainloop, self.ret)
    return
