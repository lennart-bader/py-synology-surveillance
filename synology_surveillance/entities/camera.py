from synology_surveillance.constants import RECORDING_STATUS


class Camera:
    """An representation of a Synology SurveillanceStation camera."""

    def __init__(self, data, video_stream_url_provider):
        """Initialize a Surveillance Station camera."""
        self._camera_id = data['id']
        self._name = data['name']
        self._is_enabled = data['enabled']
        self._recording_status = data['recStatus']
        self._video_stream_url = video_stream_url_provider(self.camera_id)

    @property
    def camera_id(self):
        """Return id of the camera."""
        return self._camera_id

    @property
    def name(self):
        """Return name of the camera."""
        return self._name
 
    @property
    def video_stream_url(self):
        """Return video stream url of the camera."""
        return self._video_stream_url

    @property
    def is_enabled(self):
        """Return true if camera is enabled."""
        return self._is_enabled

    @property
    def is_recording(self):
        """Return true if camera is recording."""
        return self._recording_status in RECORDING_STATUS
        