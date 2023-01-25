from synology_surveillance.constants import MOTION_DETECTION_SOURCE_DISABLED


class MotionSetting:
    """An representation of a Synology SurveillanceStation motion setting."""

    def __init__(self, camera_id, data):
        """Initialize a Surveillance Station motion setting."""
        self._camera_id = camera_id
        self._source = data['source']

    @property
    def camera_id(self):
        """Return id of the camera."""
        return self._camera_id

    @property
    def is_enabled(self):
        """Return true if motion detection is enabled."""
        return MOTION_DETECTION_SOURCE_DISABLED != self._source
