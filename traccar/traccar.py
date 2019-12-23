try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import json
import requests
from requests.auth import HTTPBasicAuth

LOGGER = polyinterface.LOGGER


class Traccar:
    def __init__(self, host, port, username, password):
        self.traccar_host = host
        self.traccar_port = port
        self.username = username
        self.password = password

    def test(self):
        print("Traccar.test: " + self.username, self.password, self.traccar_host, self.traccar_port)

    def connect(self, api_method):
        url = "http://" + self.traccar_host + ":" + self.traccar_port + "/api/" + api_method
        r = requests.get(url, auth=HTTPBasicAuth(self.username, self.password))
        resp = r.json()
        return resp

    def get_devices(self):
        devices = self.connect('devices')
        # prettyd = json.dumps(devices, indent=2)
        # print(prettyd)
        for dev in devices:
            _id = dev['id']
            _name = dev['name']
            _status = dev['status']
            _geofenceIds = dev['geofenceIds']
            print(_id, _name, _geofenceIds)

        return devices

    def get_geofences(self):
        geofences = self.connect('geofences')
        return geofences

    def get_positions(self):
        positions = self.connect('positions')
        return positions

