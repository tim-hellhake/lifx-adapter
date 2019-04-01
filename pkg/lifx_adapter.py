"""Lifx adapter for Mozilla WebThings Gateway."""

from gateway_addon import Adapter
from lifxlan import LifxLAN

from .lifx_device import LifxBulb


_TIMEOUT = 3


class LifxAdapter(Adapter):
    """Adapter for Lifx smart home devices."""

    def __init__(self, verbose=False):
        """
        Initialize the object.

        verbose -- whether or not to enable verbose logging
        """
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'lifx-adapter',
                         'lifx-adapter',
                         verbose=verbose)

        self.pairing = False
        self.start_pairing(_TIMEOUT)

    def start_pairing(self, timeout):
        """
        Start the pairing process.

        timeout -- Timeout in seconds at which to quit pairing
        """
        self.pairing = True

        lan = LifxLAN()
        lan_devices = lan.get_devices()

        for dev in lan_devices:
            if not self.pairing:
                break

            _id = 'lifx-' + dev.get_mac_addr().replace(':', '-')
            if _id not in self.devices:
                device = LifxBulb(self, _id, dev)
                self.handle_device_added(device)

    def cancel_pairing(self):
        """Cancel the pairing process."""
        self.pairing = False
