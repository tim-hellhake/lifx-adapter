"""LIFX adapter for WebThings Gateway."""

from gateway_addon import Device
import functools
import threading
import time

from .lifx_property import LifxBulbProperty
from .util import hsv_to_rgb

print = functools.partial(print, flush=True)

_POLL_INTERVAL = 5
_DEBUG = False


class LifxDevice(Device):
    """LIFX device type."""

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
    """LIFX smart bulb type."""

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
            self._type.append('ColorControl')

            self.properties['color'] = LifxBulbProperty(
                self,
                'color',
                {
                    '@type': 'ColorProperty',
                    'title': 'Color',
                    'type': 'string',
                },
                hsv_to_rgb(*self.hsv())
            )

        if self.is_white_temperature():
            if 'ColorControl' not in self._type:
                self._type.append('ColorControl')

            self.properties['colorTemperature'] = LifxBulbProperty(
                self,
                'colorTemperature',
                {
                    '@type': 'ColorTemperatureProperty',
                    'title': 'Color Temperature',
                    'type': 'integer',
                    'unit': 'kelvin',
                    'minimum': lifxlan_dev.get_min_kelvin(),
                    'maximum': lifxlan_dev.get_max_kelvin(),
                },
                self.temperature()
            )

        if self.is_color() and self.is_white_temperature():
            self.properties['colorMode'] = LifxBulbProperty(
                self,
                'colorMode',
                {
                    '@type': 'ColorModeProperty',
                    'title': 'Color Mode',
                    'type': 'string',
                    'enum': [
                        'color',
                        'temperature',
                    ],
                    'readOnly': True,
                },
                self.color_mode()
            )

        self.properties['level'] = LifxBulbProperty(
            self,
            'level',
            {
                '@type': 'BrightnessProperty',
                'title': 'Brightness',
                'type': 'integer',
                'unit': 'percent',
                'minimum': 0,
                'maximum': 100,
            },
            self.brightness()
        )

        if self.is_infrared():
            self.properties['infraredLevel'] = LifxBulbProperty(
                self,
                'infraredLevel',
                {
                    'title': 'Infrared Level',
                    'type': 'integer',
                    'unit': 'percent',
                    'minimum': 0,
                    'maximum': 100,
                },
                self.infrared_level()
            )

        self.properties['on'] = LifxBulbProperty(
            self,
            'on',
            {
                '@type': 'OnOffProperty',
                'title': 'On/Off',
                'type': 'boolean'
            },
            self.is_on()
        )

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
        """Determine whether or not the light is color-changing."""
        return bool(self.lifxlan_dev.supports_color())

    def is_white_temperature(self):
        """Determine whether or not the light can change white temperature."""
        # the only bulb that doesn't support temperature is the mini white,
        # everything else should support it
        return bool(self.lifxlan_dev.supports_temperature())

    def is_infrared(self):
        """Determine whether or not the light has infrared capabilities."""
        return bool(self.lifxlan_dev.supports_infrared())

    def is_on(self):
        """Determine whether or not the light is on."""
        return bool(self.lifxlan_dev.get_power())

    def set_on(self, state):
        """Set whether or not the light is on."""
        if state:
            self.lifxlan_dev.set_power(65535)
        else:
            self.lifxlan_dev.set_power(0)

    def hsv(self):
        """Determine the current color of the light."""
        color = self.lifxlan_dev.get_color()[:3]

        if _DEBUG:
            print("Current HSV: <hue:{}, sat:{}, bright:{}>".format(*color))

        return color

    def set_hsv(self, value):
        """
        Set the light color.

        value -- new color as [h, s, v]
        """
        if _DEBUG:
            print("Set HSV: <hue:{}, sat:{}, bright:{}>".format(*value))

        value = list(value) + [0]
        self.lifxlan_dev.set_color(value)

    def brightness(self):
        """Determine the current brightness of the light."""
        hue, saturation, brightness = self.hsv()

        if _DEBUG:
            print("Current brightness: <bright:{}>".format(brightness))

        return int(brightness / 65535.0 * 100.0)

    def set_brightness(self, level):
        """
        Set the brightness of the light.

        level -- new brightness
        """
        brightness = int(level / 100.0 * 65535.0)

        if _DEBUG:
            print("Set brightness: <bright:{}, raw:{}>"
                  .format(level, brightness))

        self.lifxlan_dev.set_brightness(brightness)

    def infrared_level(self):
        """Determine the current infrared level of the light."""
        level = int(self.lifxlan_dev.get_infrared() / 65535.0 * 100.0)

        if _DEBUG:
            print("Current infrared level: <level:{}>".format(level))

        return level

    def set_infrared_level(self, level):
        """
        Set the infrared level of the light.

        level -- new level
        """
        value = int(level / 100.0 * 65535.0)

        if _DEBUG:
            print("Set infrared level: <level:{}, raw:{}>"
                  .format(value, level))

        self.lifxlan_dev.set_infrared(value)

    def temperature(self):
        """Determine the current white temperature of the light."""
        value = self.lifxlan_dev.get_color()[3]

        if _DEBUG:
            print("Current color temperature: <temp:{}>".format(value))

        return value

    def set_temperature(self, value):
        """
        Set the white temperature of the light.

        value -- new temperature
        """
        if _DEBUG:
            print("Set color temperature: <temp:{}>".format(value))

        self.lifxlan_dev.set_color((0, 0, self.hsv()[2], value))

    def color_mode(self):
        """Determine the current color mode."""
        hsv = self.hsv()
        if hsv[1] == 0:
            return 'temperature'

        return 'color'
