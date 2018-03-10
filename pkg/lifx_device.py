"""Lifx adapter for Mozilla IoT Gateway."""

import functools
import threading
import time

import gateway_addon
from gateway_addon import Device

from lifxlan import LifxLAN
from lifxlan import Device as LifxLANDevice

from .lifx_property import LifxBulbProperty
from .util import hsv_to_rgb

print = functools.partial(print, flush=True)

_POLL_INTERVAL = 5


class LifxDevice(Device):
    """Lifx device type."""

    def __init__(self, adapter, _id, lifxlan_dev):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        lifxlan_dev -- the lifxlan device object to initialize from
        """
        Device.__init__(self, adapter, _id)

        self.lifxlan_dev = lifxlan_dev
        self.description = lifxlan_dev.get_product_name()
        self.name = lifxlan_dev.get_label()
        if not self.name:
            self.name = self.description

        self.t = threading.Thread(target=self.poll)
        self.t.daemon = True
        self.t.start()



class LifxBulb(LifxDevice):
    """Lifx smart bulb type."""

    def __init__(self, adapter, _id, lifxlan_dev):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        lifxlan_dev -- the lifxlan device object to initialize from
        """
        LifxDevice.__init__(self, adapter, _id, lifxlan_dev)

        if self.is_color():
            print("Bulb supports color")
            self.type = 'onOffColorLight'

            self.properties['color'] = LifxBulbProperty(self,
                                                       'color',
                                                       {  
                                                           'type': 'string'
                                                       },
                                                       hsv_to_rgb(*self.hsv()))
        elif gateway_addon.API_VERSION >= 2 and self.is_white_temperature():
            print("Bulb supports white temperature") 
            self.type = 'dimmableColorLight'

            self.properties['colorTemperature'] = \
                LifxBulbProperty(self,
                                 'colorTemperature',
                                 {  
                                     'type': 'number',
                                     'unit': 'kelvin',
                                     'min': 1500,
                                     'max': 9000
                                 },
                                 self.temperature())
        else:
            self.type = 'dimmableLight'

        if not self.is_color()
            self.properties['level'] = LifxBulbProperty(self,
                                                       'level',
                                                       {  
                                                          'type': 'number',
                                                          'unit': 'percent',
                                                          'min': 0,
                                                          'max': 100
                                                       },
                                                       self.brightness())

        self.properties['on'] = LifxBulbProperty(self, 
                                                 'on', 
                                                 {
                                                     'type': 'boolean'
                                                 }, 
                                                 self.is_on())


    def poll(self):
        """Poll the device for changes."""
        while True:
            time.sleep(_POLL_INTERVAL)
            try:
                #self.lifxlan_dev.get_power()
                #self.lifxlan_dev.get_color()
                for prop in self.properties.values():
                    prop.update()
            except Exception as e:
                print("WARNING: LifxBulb polling failed: " + str(e))
                continue


    def is_color(self):
        """
        Determine whether or not the light is color-changing.
        """
        return bool(self.lifxlan_dev.supports_color())

    def is_white_temperature(self):
        """
        Determine whether or not the light can change white temperature.
        """
        # the only bulb that doesn't support temperature is the mini white,
        # everything else should support it
        return bool(self.lifxlan_dev.supports_temperature())

    def is_on(self):
        """
        Determine whether or not the light is on.
        """
        return bool(self.lifxlan_dev.get_power())

    def set_on(self, state):
        """
        Set whether or not the light is on.
        """
        self.lifxlan_dev.set_power(65535) if state else self.lifxlan_dev.set_power(0)


    def hsv(self):
        """
        Determine the current color of the light.
        """
        color = self.lifxlan_dev.get_color()
        print("Getting HSV")
        hue = color[0]
        saturation = color[1]
        raw_brightness = color[2]
        percent_brightness = (raw_brightness / 65535.0) * 100.0
        print("Current HSV: <hue:" + str(hue) + ", sat:" + str(saturation) + ", bright:" + str(percent_brightness) + ">")
        value = int(percent_brightness)

        return hue, saturation, value

    def set_hsv(self, value):
        """
        Determine the current color of the light.
        """
        print("Set HSV: <hue:" + str(value[0]) + ", sat:" + str(value[1]) + ", bright:" + str(value[2]) + ">")
        self.lifxlan_dev.set_hue(value[0])
        self.lifxlan_dev.set_saturation(value[1])
        self.lifxlan_dev.set_brightness(value[2])

    def brightness(self):
        """
        Determine the current brightness of the light.
        """
        hue, saturation, percent_brightness = self.hsv()
        print("Current brightness: <bright:" + str(percent_brightness) + ">")
        return percent_brightness

    def set_brightness(self, level):
        """
        Set the brightness of the light.
        """
        raw_brightness = (level / 100.0) * 65535.0
        print("Set brightness: <bright:" + str(level) + ", raw:" + str(raw_brightness) + ">")
        self.lifxlan_dev.set_brightness(raw_brightness)

    def temperature(self):
        """
        Determine the current white temperature of the light.
        """
        color = self.lifxlan_dev.get_color()
        value = color[3]
        print("Current color temperature: <temp:" + str(value)  + ">")
        return value

    def set_temperature(self, value):
        """
        Set the white temperature of the light.
        """
        print("Set color temperature: <temp:" + str(value) + ">")
        self.lifxlan_dev.set_colortemp(value)
