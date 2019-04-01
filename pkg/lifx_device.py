"""Lifx adapter for Mozilla WebThings Gateway."""

import functools
import threading
import time

import gateway_addon
from gateway_addon import Device

from .lifx_property import LifxBulbProperty
from .util import hsv_to_rgb

print = functools.partial(print, flush=True)

_POLL_INTERVAL = 5
_DEBUG = False


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
        self._type = []

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

        self._type.extend(['OnOffSwitch', 'Light'])

        if self.is_color():
            if _DEBUG:
                print("Bulb supports color")

            self.type = 'onOffColorLight'
            self._type.append('ColorControl')

            self.properties['color'] = LifxBulbProperty(
                self,
                'color',
                {
                    '@type': 'ColorProperty',
                    'label': 'Color',
                    'type': 'string'
                },
                hsv_to_rgb(*self.hsv()))
        elif gateway_addon.API_VERSION >= 2 and self.is_white_temperature():
            if _DEBUG:
                print("Bulb supports white temperature")

            self.type = 'dimmableColorLight'
            self._type.append('ColorControl')

            self.properties['colorTemperature'] = LifxBulbProperty(
                self,
                'colorTemperature',
                {
                    '@type': 'ColorTemperatureProperty',
                    'label': 'Color Temperature',
                    'type': 'number',
                    'unit': 'kelvin',
                    'min': lifxlan_dev.get_min_kelvin(),
                    'max': lifxlan_dev.get_max_kelvin()
                },
                self.temperature())
        else:
            if _DEBUG:
                print("Bulb supports dimming")

            self.type = 'dimmableLight'

        if not self.is_color():
            self.properties['level'] = LifxBulbProperty(
                self,
                'level',
                {
                    '@type': 'BrightnessProperty',
                    'label': 'Brightness',
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
        if state:
            self.lifxlan_dev.set_power(65535)
        else:
            self.lifxlan_dev.set_power(0)

    def hsv(self):
        """
        Determine the current color of the light.
        """
        color = self.lifxlan_dev.get_color()[:3]

        if _DEBUG:
            print("Current HSV: <hue:{}, sat:{}, bright:{}>".format(*color))

        return color

    def set_hsv(self, value):
        """
        Determine the current color of the light.
        """
        if _DEBUG:
            print("Set HSV: <hue:{}, sat:{}, bright:{}>".format(*value))

        value = list(value) + [3500]
        self.lifxlan_dev.set_color(value)

    def brightness(self):
        """
        Determine the current brightness of the light.
        """
        hue, saturation, brightness = self.hsv()

        if _DEBUG:
            print("Current brightness: <bright:{}>".format(brightness))

        return int(brightness / 65535.0 * 100.0)

    def set_brightness(self, level):
        """
        Set the brightness of the light.
        """
        brightness = int(level / 100.0 * 65535.0)

        if _DEBUG:
            print("Set brightness: <bright:{}, raw:{}>"
                  .format(level, brightness))

        self.lifxlan_dev.set_brightness(brightness)

    def temperature(self):
        """
        Determine the current white temperature of the light.
        """
        value = self.lifxlan_dev.get_color()[3]

        if _DEBUG:
            print("Current color temperature: <temp:{}>".format(value))

        return value

    def set_temperature(self, value):
        """
        Set the white temperature of the light.
        """
        if _DEBUG:
            print("Set color temperature: <temp:{}>".format(value))

        self.lifxlan_dev.set_colortemp(value)
