"""Lifx adapter for Mozilla WebThings Gateway."""

from gateway_addon import Property

from .util import hsv_to_rgb, rgb_to_hsv


class LifxProperty(Property):
    """Lifx property type."""

    def __init__(self, device, name, description, value):
        """
        Initialize the object.

        device -- the Device this property belongs to
        name -- name of the property
        description -- description of the property, as a dictionary
        value -- current value of this property
        """
        Property.__init__(self, device, name, description)
        self.set_cached_value(value)


class LifxBulbProperty(LifxProperty):
    """Property type for Lifx smart bulbs."""

    def set_value(self, value):
        """
        Set the current value of the property.

        value -- the value to set
        """
        color_mode_prop = None
        if 'colorMode' in self.device.properties:
            color_mode_prop = self.device.properties['colorMode']

        if self.name == 'on':
            self.device.set_on(value)
        elif self.name == 'color':
            new_color = rgb_to_hsv(value)
            self.device.set_hsv(new_color)

            # update the colorMode property
            if color_mode_prop is not None:
                color_mode_prop.set_cached_value('color')
                self.device.notify_property_changed(color_mode_prop)
        elif self.name == 'colorTemperature':
            self.device.set_temperature(value)

            # update the colorMode property
            if color_mode_prop is not None:
                color_mode_prop.set_cached_value('temperature')
                self.device.notify_property_changed(color_mode_prop)
        elif self.name == 'level':
            self.device.set_brightness(value)
        elif self.name == 'infraredLevel':
            self.device.set_infrared_level(value)
        else:
            return

        self.set_cached_value(value)
        self.device.notify_property_changed(self)

    def update(self):
        """
        Update the current value, if necessary.

        light_state -- current state of the light
        """
        if self.name == 'on':
            value = self.device.is_on()
        elif self.name == 'color':
            value = hsv_to_rgb(*self.device.hsv())
        elif self.name == 'colorTemperature':
            value = self.device.temperature()
        elif self.name == 'colorMode':
            value = self.device.color_mode()
        elif self.name == 'level':
            value = self.device.brightness()
        elif self.name == 'infraredLevel':
            value = self.device.infrared_level()
        else:
            return

        if value != self.value:
            self.set_cached_value(value)
            self.device.notify_property_changed(self)
