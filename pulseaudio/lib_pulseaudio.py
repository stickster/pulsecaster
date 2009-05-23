#!/usr/bin/python
# vi: et sw=2
#
# lib_pulseaudio.py
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
# Provides pulseaudio interface for python
#
# Author: Harry Karvonen <harry.karvonen@gmail.com>
#

from ctypes import *

pulse = CDLL("libpulse.so.0");

################################################################################
#
# Constrants
#
################################################################################

PA_CHANNELS_MAX = 32
PA_VOLUME_NORM = 0x10000

################################################################################
#
# Structs
#
################################################################################

class PA_IO_EVENT(Structure):
  _fields_ = [("_opaque_struct", c_int)]

class PA_MAINLOOP(Structure):
  _fields_ = [("_opaque_struct", c_int)]

class PA_MAINLOOP_API(Structure):
  _fields_ = [("_opaque_struct", c_int)]

class PA_CONTEXT(Structure):
  _fields_ = [("_opaque_struct", c_int)]

class PA_OPERATION(Structure):
  _fields_ = [("_opaque_struct", c_int)]

class PA_SAMPLE_SPEC(Structure):
  _fields_ = [
    ("format", c_int), # FIXME check this
    ("rate", c_uint32),
    ("channels", c_uint32)
  ]

class PA_CHANNEL_MAP(Structure):
  _fields_ = [
    ("channels", c_uint8),
    ("map", c_int * PA_CHANNELS_MAX)
  ]

class PA_CVOLUME(Structure):
  _fields_ = [
    ("channels", c_uint8),
    ("values", c_uint32 * PA_CHANNELS_MAX)
  ]

PA_USEC_T = c_uint64

class PA_SINK_INPUT_INFO(Structure):
  __slots__ = [
    'index',
    'name',
    'owner_module',
    'client',
    'sink',
    'sample_spec',
    'channel_map',
    'volume',
    'buffer_usec',
    'sink_usec',
    'resample_method',
    'driver',
    'mute',
  ] 
  _fields_ = [
    ("index",           c_uint32),
    ("name",            c_char_p),
    ("owner_module",    c_uint32),
    ("client",          c_uint32),
    ("sink",            c_uint32),
    ("sample_spec",     PA_SAMPLE_SPEC),
    ("channel_map",     PA_CHANNEL_MAP),
    ("volume",          PA_CVOLUME),
    ("buffer_usec",     PA_USEC_T),
    ("sink_usec",       PA_USEC_T),
    ("resample_method", c_char_p),
    ("driver",          c_char_p),
    ("mute",            c_int)
    #("proplist",        POINTER(c_int))
  ]

class PA_SINK_INFO(Structure):
  _fields_ = [
    ("name",                c_char_p),
    ("index",               c_uint32),
    ("description",         c_char_p),
    ("sample_spec",         PA_SAMPLE_SPEC),
    ("channel_map",         PA_CHANNEL_MAP),
    ("owner_module",        c_uint32),
    ("volume",              PA_CVOLUME),
    ("mute",                c_int),
    ("monitor_source",      c_uint32),
    ("monitor_source_name", c_char_p),
    ("latency",             PA_USEC_T),
    ("driver",              c_char_p),
    ("flags",               c_int),
    ("proplist",            POINTER(c_int)),
    ("configured_latency",  PA_USEC_T)
  ]

class PA_SOURCE_OUTPUT_INFO(Structure):
  __slots__ = [
    'index',
    'name',
    'owner_module',
    'client',
    'source',
    'sample_spec',
    'channel_map',
    'volume',
    'buffer_usec',
    'sink_usec',
    'resample_method',
    'driver',
    'mute',
  ] 
  _fields_ = [
    ("index",           c_uint32),
    ("name",            c_char_p),
    ("owner_module",    c_uint32),
    ("client",          c_uint32),
    ("source",            c_uint32),
    ("sample_spec",     PA_SAMPLE_SPEC),
    ("channel_map",     PA_CHANNEL_MAP),
    ("volume",          PA_CVOLUME),
    ("buffer_usec",     PA_USEC_T),
    ("sink_usec",       PA_USEC_T),
    ("resample_method", c_char_p),
    ("driver",          c_char_p),
    ("mute",            c_int)
    #("proplist",        POINTER(c_int))
  ]

class PA_SOURCE_INFO(Structure):
  _fields_ = [
    ("name",                 c_char_p),
    ("index",                c_uint32),
    ("description",          c_char_p),
    ("sample_spec",          PA_SAMPLE_SPEC),
    ("channel_map",          PA_CHANNEL_MAP),
    ("owner_module",         c_uint32),
    ("volume",               PA_CVOLUME),
    ("mute",                 c_int),
    ("monitor_of_sink",      c_uint32),
    ("monitor_of_sink_name", c_char_p),
    ("latency",              PA_USEC_T),
    ("driver",               c_char_p),
    ("flags",                c_int),
    ("proplist",             POINTER(c_int)),
    ("configured_latency",   PA_USEC_T)
  ]

class PA_CLIENT_INFO(Structure):
  _fields_ = [
    ("index",        c_uint32),
    ("name",         c_char_p),
    ("owner_module", c_uint32),
    ("driver",       c_char_p)
    #("proplist",    POINTER(c_int))
  ]

################################################################################
#
# Callback types
#
################################################################################

#PA_IO_EVENT_CB_T = CFUNCTYPE(c_void_p,
#                             POINTER(PA_MAINLOOP_API),
#                             POINTER(PA_IO_EVENT),
#                             c_int,
#                             c_int,
#                             c_void_p)

# SIGNAL
PA_SIGNAL_CB_T = CFUNCTYPE(c_void_p,
                           POINTER(PA_MAINLOOP_API),
                           POINTER(c_int), # FIXME wrong type
                           c_int,
                           c_void_p)

# STATE
PA_STATE_CB_T = CFUNCTYPE(c_int,
                          POINTER(PA_CONTEXT),
                          c_void_p)

# CLIENT
PA_CLIENT_INFO_CB_T = CFUNCTYPE(c_void_p,
                                POINTER(PA_CONTEXT),
                                POINTER(PA_CLIENT_INFO),
                                c_int,
                                c_void_p)
# SINK INPUT
PA_SINK_INPUT_INFO_CB_T = CFUNCTYPE(c_int, #FIXME wrong type
                                    POINTER(PA_CONTEXT),
                                    POINTER(PA_SINK_INPUT_INFO),
                                    c_int,
                                    c_void_p)
                
# SINK
PA_SINK_INFO_CB_T = CFUNCTYPE(c_int, #FIXME wrong type
                              POINTER(PA_CONTEXT),
                              POINTER(PA_SINK_INFO),
                              c_int,
                              c_void_p)
# SOURCE OUTPUT
PA_SOURCE_OUTPUT_INFO_CB_T = CFUNCTYPE(c_int, #FIXME wrong type
                                       POINTER(PA_CONTEXT),
                                       POINTER(PA_SOURCE_OUTPUT_INFO),
                                       c_int,
                                       c_void_p)
                
# SOURCE
PA_SOURCE_INFO_CB_T = CFUNCTYPE(c_int, #FIXME wrong type
                                POINTER(PA_CONTEXT),
                                POINTER(PA_SOURCE_INFO),
                                c_int,
                                c_void_p)
# CONTEXT
PA_CONTEXT_DRAIN_CB_T = CFUNCTYPE(c_void_p,
                                  POINTER(PA_CONTEXT),
                                  c_void_p)

PA_CONTEXT_SUCCESS_CB_T = CFUNCTYPE(c_void_p,
                                    POINTER(PA_CONTEXT),
                                    c_int,
                                    c_void_p)

################################################################################
#
# Functions
#
################################################################################

#
# pa_strerror
pa_strerror = pulse.pa_strerror
pa_strerror.restype = c_char_p
pa_strerror.argtypes = [
        c_int
]

#
# pa_mainloop_*
pa_mainloop_new = pulse.pa_mainloop_new
pa_mainloop_new.restype = POINTER(PA_MAINLOOP)
pa_mainloop_new.argtypes = [
]

pa_mainloop_get_api = pulse.pa_mainloop_get_api
pa_mainloop_get_api.restype = POINTER(PA_MAINLOOP_API)
pa_mainloop_get_api.argtypes = [
        POINTER(PA_MAINLOOP)
]

pa_mainloop_run = pulse.pa_mainloop_run
pa_mainloop_run.restype = c_int
pa_mainloop_run.argtypes = [
        POINTER(PA_MAINLOOP),
        POINTER(c_int)
]

pa_mainloop_iterate = pulse.pa_mainloop_iterate
pa_mainloop_iterate.restype = c_int
pa_mainloop_iterate.argtypes = [
        POINTER(PA_MAINLOOP),
        c_int,
        POINTER(c_int)
]

pa_mainloop_quit = pulse.pa_mainloop_quit
pa_mainloop_quit.restype = c_int
pa_mainloop_quit.argtypes = [
        POINTER(PA_MAINLOOP),
        c_int
]

pa_mainloop_dispatch = pulse.pa_mainloop_dispatch
pa_mainloop_dispatch.restype = c_int
pa_mainloop_dispatch.argtypes = [
        POINTER(PA_MAINLOOP)
]

pa_mainloop_free = pulse.pa_mainloop_run
pa_mainloop_free.restype = c_int
pa_mainloop_free.argtypes = [
        POINTER(PA_MAINLOOP)
]

#
# pa_signal_*
pa_signal_init = pulse.pa_signal_init
pa_signal_init.restype = c_int
pa_signal_init.argtypes = [
        POINTER(PA_MAINLOOP_API)
]

pa_signal_new = pulse.pa_signal_new
pa_signal_new.restype = None #POINTER(c_int) #FIXME PA_SIGNAL_EVENT)
pa_signal_new.argtypes = [
        c_int,
        PA_SIGNAL_CB_T,
        POINTER(c_int)
]

#
# pa_context_*
pa_context_errno = pulse.pa_context_errno
pa_context_errno.restype = c_int
pa_context_errno.argtypes = [
        POINTER(PA_CONTEXT)
]

pa_context_new = pulse.pa_context_new
pa_context_new.restype = POINTER(PA_CONTEXT)
pa_context_new.argtypes = [
        POINTER(PA_MAINLOOP_API),
        c_char_p
]


pa_context_set_state_callback = pulse.pa_context_set_state_callback
pa_context_set_state_callback.restype = None
pa_context_set_state_callback.argtypes = [
        POINTER(PA_CONTEXT),
        PA_STATE_CB_T,
        c_void_p
]

pa_context_connect = pulse.pa_context_connect
pa_context_connect.restype = c_int
pa_context_connect.argtypes = [
        POINTER(PA_CONTEXT),
        c_char_p,
        c_int, #FIXME | isn't correct
        POINTER(c_int)
]

pa_context_get_state = pulse.pa_context_get_state
pa_context_get_state.restype = c_int;
pa_context_get_state.argtypes = [
        POINTER(PA_CONTEXT)
]

pa_context_drain = pulse.pa_context_drain
pa_context_drain.restype = POINTER(PA_OPERATION)
pa_context_drain.argtypes = [
        POINTER(PA_CONTEXT),
        PA_CONTEXT_DRAIN_CB_T,
        c_void_p
]

pa_context_disconnect = pulse.pa_context_disconnect
pa_context_disconnect.restype = c_int;
pa_context_disconnect.argtypes = [
        POINTER(PA_CONTEXT)
]

#
# pa_context_*_sink_*
pa_context_get_sink_input_info_list = pulse.pa_context_get_sink_input_info_list
pa_context_get_sink_input_info_list.restype = POINTER(c_int)
pa_context_get_sink_input_info_list.argtypes = [
        POINTER(PA_CONTEXT),
        PA_SINK_INPUT_INFO_CB_T,
        c_void_p
]

pa_context_get_sink_info_list = pulse.pa_context_get_sink_info_list
pa_context_get_sink_info_list.restype = POINTER(c_int)
pa_context_get_sink_info_list.argtypes = [
        POINTER(PA_CONTEXT),
        PA_SINK_INFO_CB_T,
        c_void_p
]

pa_context_set_sink_mute_by_index = pulse.pa_context_set_sink_mute_by_index
pa_context_set_sink_mute_by_index.restype = POINTER(c_int)
pa_context_set_sink_mute_by_index.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        c_int,
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

pa_context_set_sink_input_mute = pulse.pa_context_set_sink_input_mute
pa_context_set_sink_input_mute.restype = POINTER(c_int)
pa_context_set_sink_input_mute.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        c_int,
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

pa_context_set_sink_volume_by_index = pulse.pa_context_set_sink_volume_by_index
pa_context_set_sink_volume_by_index.restype = POINTER(c_int)
pa_context_set_sink_volume_by_index.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        POINTER(PA_CVOLUME),
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

pa_context_set_sink_input_volume = pulse.pa_context_set_sink_input_volume
pa_context_set_sink_input_volume.restype = POINTER(c_int)
pa_context_set_sink_input_volume.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        POINTER(PA_CVOLUME),
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

#
# pa_context_*_source_*
pa_context_get_source_output_info_list = pulse.pa_context_get_source_output_info_list
pa_context_get_source_output_info_list.restype = POINTER(c_int)
pa_context_get_source_output_info_list.argtypes = [
        POINTER(PA_CONTEXT),
        PA_SOURCE_OUTPUT_INFO_CB_T,
        c_void_p
]

pa_context_get_source_info_list = pulse.pa_context_get_source_info_list
pa_context_get_source_info_list.restype = POINTER(c_int)
pa_context_get_source_info_list.argtypes = [
        POINTER(PA_CONTEXT),
        PA_SOURCE_INFO_CB_T,
        c_void_p
]

pa_context_set_source_mute_by_index = pulse.pa_context_set_source_mute_by_index
pa_context_set_source_mute_by_index.restype = POINTER(c_int)
pa_context_set_source_mute_by_index.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        c_int,
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

pa_context_set_source_volume_by_index = pulse.pa_context_set_source_volume_by_index
pa_context_set_source_volume_by_index.restype = POINTER(c_int)
pa_context_set_source_volume_by_index.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        POINTER(PA_CVOLUME),
        PA_CONTEXT_SUCCESS_CB_T,
        c_void_p
]

#
# pa_context_*_client_*

pa_context_get_client_info_list = pulse.pa_context_get_client_info_list
pa_context_get_client_info_list.restype = POINTER(c_int)
pa_context_get_client_info_list.argtypes = [
        POINTER(PA_CONTEXT),
        PA_CLIENT_INFO_CB_T,
        c_void_p
]
pa_context_get_client_info = pulse.pa_context_get_client_info
pa_context_get_client_info.restype = POINTER(c_int)
pa_context_get_client_info.argtypes = [
        POINTER(PA_CONTEXT),
        c_uint32,
        PA_CLIENT_INFO_CB_T,
        c_void_p
]

#
# pa_operation_*
pa_operation_unref = pulse.pa_operation_unref
pa_operation_unref.restype = c_int
pa_operation_unref.argtypes = [
        POINTER(PA_OPERATION)
]

