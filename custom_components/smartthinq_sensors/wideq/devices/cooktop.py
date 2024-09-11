"""------------------for cooktops"""

from __future__ import annotations

from ..const import BIT_OFF, CooktopFeatures, StateOptions
from ..core_async import ClientAsync
from ..device import Device, DeviceStatus
from ..device_info import DeviceInfo



ITEM_STATE_OFF = "@OV_STATE_INITIAL_W"


class CooktopDevice(Device):
    """A higher-level interface for a cooktop."""

    def __init__(self, client: ClientAsync, device_info: DeviceInfo):
        super().__init__(client, device_info, CooktopStatus(self))

    def reset_status(self):
        self._status = CooktopStatus(self)
        return self._status

    async def poll(self) -> CooktopStatus | None:
        """Poll the device's current state."""

        res = await self._device_poll("cooktopState")
        if not res:
            return None

        self._status = CooktopStatus(self, res)
        return self._status


class CooktopStatus(DeviceStatus):
    """
    Higher-level information about an cooktop's current status.

    :param device: The Device instance.
    :param data: JSON data from the API.
    """

    _device: CooktopDevice

    def __init__(self, device: CooktopDevice, data: dict | None = None):
        """Initialize device status."""
        super().__init__(device, data)
        self._state = None

    @property
    def is_on(self):
        """Return if device is on."""
        return self.is_cooktop_on 

    @property
    def is_cooktop_on(self):
        """Return if cooktop is on."""
        for feature in [
            CooktopFeatures.COOKTOP_CENTER_STATE,
            CooktopFeatures.COOKTOP_LEFT_FRONT_STATE,
            CooktopFeatures.COOKTOP_LEFT_REAR_STATE,
            CooktopFeatures.COOKTOP_RIGHT_FRONT_STATE,
            CooktopFeatures.COOKTOP_RIGHT_REAR_STATE,
        ]:
            res = self.device_features.get(feature)
            if res and res != StateOptions.OFF:
                return True
        return False

    @property
    def cooktop_state(self):
        """Return left front cooktop state."""
        # For some cooktops (maybe depending on firmware or model),
        # the five burners do not report individual status.
        # Instead, the cooktop_left_front reports aggregated status for all burners.
        status = self.lookup_enum("burnerOnCounter")
        if status is None:
            return None
        if status == ITEM_STATE_OFF:
            status = BIT_OFF
        return self._update_feature(CooktopFeatures.COOKTOP_LEFT_FRONT_STATE, status)

  

    
    def _update_features(self):
        _ = [
            self.cooktop_state,
        ]
