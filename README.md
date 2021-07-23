A PulseAudio based podcasting application

Thanks to Harry Karvonen for his Python ctypes-based bindings for
PulseAudio. (These are now removed in favor of the pulsectl module.)
Thanks also to Jürgen Geuter for helping me understand distutils and
contributing some fixes.

## Requirements

PulseCaster has been updated to require Python 3. It will no longer
run on Python 2. If you must use Python 2, please use a release
prior to version 0.9.

## Instructions

If you are looking at the source, 'cd' to the top of this project and
then run the following command to try it out:

    $ cd pulsecaster
    $ ./pulsecaster/pulsecaster

## Advanced Tips

The code currently contains a very hacky function to allow you to
record to FLAC (the Free Lossless Audio Codec) instead of Ogg Vorbis,
which is the default.  To turn that capability on, run this command:

    $ gsettings set org.pulsecaster.PulseCaster codec flac

To switch back to Vorbis:

    $ gsettings set org.pulsecaster.PulseCaster codec vorbis

There's an additional function for setting audio rate (default is
48000 Hz):

    $ gsettings set org.pulsecaster.PulseCaster audiorate 44100
    $ gsettings set org.pulsecaster.PulseCaster audiorate 48000

## Installing

The easiest way to use this application is to simply install it using
your platform's preferred tool set.  To install it using Fedora, run
the folowing command:

    dnf install pulsecaster

To install it on another flavor of Linux, check the documentation for
your particular distribution.

To install directly from this source code, use the handy "distutils"
script that's provided:

    $ python setup.py build
    $ python setup.py install

Refer to the wiki at http://pulsecaster.org/ for a full list of
dependencies and requirements.

## Translation

Translation is done via Transifex:
https://www.transifex.com/stickster/pulsecaster/dashboard/

## GStreamer

The pipeline for capturing from a running PulseAudio source:

    gst-launch pulsesrc device-name='<NAME>' \
	   ! vorbisenc quality=0.5 \
	   ! oggmux \
	   ! filesink location=foo.ogg

