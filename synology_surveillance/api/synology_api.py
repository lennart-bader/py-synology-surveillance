"""Python Synology SurveillanceStation API wrapper."""
import json
from typing import List
import urllib

import requests

from synology_surveillance.constants import API_NAMES, BASE_API_INFO, ERROR_CODE_SESSION_EXPIRED, HOME_MODE_OFF, HOME_MODE_ON
from synology_surveillance.entities.camera import Camera
from synology_surveillance.entities.motion_setting import MotionSetting
from synology_surveillance.session_expired_exception import SessionExpiredException


class SynologyApi:
    """An implementation of a Synology SurveillanceStation API."""

    def __init__(self, url, username, password, timeout=10, verify_ssl=True):
        """Initialize a Synology Surveillance API."""
        self._base_url = url + '/webapi/'
        self._username = username
        self._password = password
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._api_info = None
        self._sid = None

        self._initialize_api_info()
        self._initialize_api_sid()

    def _initialize_api_info(self, **kwargs):
        payload = dict({
            'api': 'SYNO.API.Info',
            'method': 'query',
            'version': '1',
            'query': ','.join(API_NAMES),
        }, **kwargs)
        response = self._get_json_with_retry(self._base_url + 'entry.cgi',
                                             payload)

        self._api_info = BASE_API_INFO
        for api in self._api_info.values():
            api_name = api['name']
            api['url'] = self._base_url + response['data'][api_name]['path']

    def _initialize_api_sid(self, **kwargs):
        api = self._api_info['auth']
        payload = dict({
            'api': api['name'],
            'method': 'login',
            'version': api['version'],
            'account': self._username,
            'passwd': self._password,
            'session': 'SurveillanceStation',
            'format': 'sid',
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        self._sid = response['data']['sid']

    def home_mode_set_state(self, state, **kwargs):
        """Set the state of Home Mode"""

        # It appears that surveillance station needs lowercase text
        # true/false for the on switch
        if state not in (HOME_MODE_ON, HOME_MODE_OFF):
            raise ValueError('Invalid home mode state')

        api = self._api_info['home_mode']
        payload = dict({
            'api': api['name'],
            'method': 'Switch',
            'version': api['version'],
            'on': state,
            '_sid': self._sid,
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        if response['success']:
            return True

        return False

    def home_mode_status(self, **kwargs):
        """Returns the status of Home Mode"""
        api = self._api_info['home_mode']
        payload = dict({
            'api': api['name'],
            'method': 'GetInfo',
            'version': api['version'],
            '_sid': self._sid
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        return response['data']['on']

    def camera_list(self, **kwargs) -> List[Camera]:
        """Return a list of cameras."""
        api = self._api_info['camera']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'List',
            'version': api['version'],
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        cameras = []

        for data in response['data']['cameras']:
            print(json.dumps(data, indent=4))
            cameras.append(Camera(data, self._video_stream_url))

        return cameras

    def camera_info(self, camera_ids, **kwargs):
        """Return a list of cameras matching camera_ids."""
        api = self._api_info['camera']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'GetInfo',
            'version': api['version'],
            'cameraIds': ', '.join(str(id) for id in camera_ids),
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)
        print(json.dumps(response, indent=4))

        cameras = []

        for data in response['data']['cameras']:
            cameras.append(Camera(data, self._video_stream_url))

        return cameras

    def camera_snapshot(self, camera_id, **kwargs):
        """Return bytes of camera image."""
        api = self._api_info['camera']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'GetSnapshot',
            'version': api['version'],
            'cameraId': camera_id,
        }, **kwargs)
        response = self._get(api['url'], payload)

        return response.content

    def take_camera_snapshot(self, camera_id, save=True, **kwargs):
        """Trigger a snapshot capture of camera image."""
        api = self._api_info['snapshot']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'TakeSnapshot',
            'version': api['version'],
            'camId': camera_id,
            'blSave': int(save)
        }, **kwargs)

        response = self._get_json_with_retry(api['url'], payload)

        return response

    def get_camera_snapshot(self, snapshot_id, snapshot_size, **kwargs):
        """Return bytes of camera image."""
        api = self._api_info['snapshot']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'LoadSnapshot',
            'version': api['version'],
            'id': snapshot_id,
            'imgSize': snapshot_size
        }, **kwargs)
        response = self._get(api['url'], payload)

        return response.content

    def camera_disable(self, camera_id, **kwargs):
        """Disable camera."""
        api = self._api_info['camera']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'Disable',
            'version': 9,
            'idList': camera_id,
        }, **kwargs)
        print(api['url'])
        print(payload)
        response = self._get(api['url'], payload)

        return response['success']

    def camera_enable(self, camera_id, **kwargs):
        """Enable a camera"""
        api = self._api_info['camera']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'Enable',
            'version': 9,
            'idList': camera_id,
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        return response['success']

    def camera_event_motion_enum(self, camera_id, **kwargs):
        """Return motion settings matching camera_id."""
        api = self._api_info['camera_event']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'MotionEnum',
            'version': api['version'],
            'camId': camera_id,
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        return MotionSetting(camera_id, response['data']['MDParam'])

    def camera_event_md_param_save(self, camera_id, **kwargs):
        """Update motion settings matching camera_id with keyword args."""
        api = self._api_info['camera_event']
        payload = dict({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'MDParamSave',
            'version': api['version'],
            'camId': camera_id,
        }, **kwargs)
        response = self._get_json_with_retry(api['url'], payload)

        return response['data']['camId']

    def camera_start_recording(self, camera_id, **kwargs):
        """Start a manual recording for the given camera_id"""
        pass

    def camera_stop_recording(self, camera_id, **kwargs):
        """Stop a (manual) recording for the given camera_id"""
        pass

    def _video_stream_url(self, camera_id, video_format='mjpeg'):
        api = self._api_info['video_stream']

        return api['url'] + '?' + urllib.parse.urlencode({
            '_sid': self._sid,
            'api': api['name'],
            'method': 'Stream',
            'version': api['version'],
            'cameraId': camera_id,
            'format': video_format,
        })

    def _get(self, url, payload):
        response = requests.get(url, payload, timeout=self._timeout,
                                verify=self._verify_ssl)

        response.raise_for_status()
        return response

    def _get_json_with_retry(self, url, payload):
        try:
            return self._get_json(url, payload)
        except SessionExpiredException:
            self._initialize_api_sid()
            return self._get_json(url, payload)

    def _get_json(self, url, payload):
        response = self._get(url, payload)
        content = response.json()

        if 'success' not in content or content['success'] is False:
            error_code = content.get('error', {}).get('code')

            if ERROR_CODE_SESSION_EXPIRED == error_code:
                raise SessionExpiredException('Session expired')

            raise ValueError('Invalid or failed response', content)

        return content
