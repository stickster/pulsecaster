import dbus
import dbus.mainloop.glib

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
        

