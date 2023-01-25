ERROR_CODE_SESSION_EXPIRED = 105

BASE_API_INFO = {
    'auth': {
        'name': 'SYNO.API.Auth',
        'version': 3
    },
    'camera': {
        'name': 'SYNO.SurveillanceStation.Camera',
        'version': 1
    },
    'camera_event': {
        'name': 'SYNO.SurveillanceStation.Camera.Event',
        'version': 1
    },
    'video_stream': {
        'name': 'SYNO.SurveillanceStation.VideoStreaming',
        'version': 1
    },
    'home_mode': {
        'name': 'SYNO.SurveillanceStation.HomeMode',
        'version': 1
    },
    'snapshot': {
        'name': 'SYNO.SurveillanceStation.SnapShot',
        'version': 1
    },
}

API_NAMES = [api['name'] for api in BASE_API_INFO.values()]

RECORDING_STATUS = [
    # Continue recording schedule
    1,
    # Motion detect recording schedule
    2,
    # Digital input recording schedule
    3,
    # Digital input recording schedule
    4,
    # Manual recording schedule
    5,
    # External
    6,
    # Analytics
    7]
MOTION_DETECTION_SOURCE_DISABLED = -1
MOTION_DETECTION_SOURCE_BY_CAMERA = 0
MOTION_DETECTION_SOURCE_BY_SURVEILLANCE = 1

HOME_MODE_ON = "true"
HOME_MODE_OFF = "false"

SNAPSHOT_SIZE_ICON = 1
SNAPSHOT_SIZE_FULL = 2