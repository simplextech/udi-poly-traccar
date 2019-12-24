#!/usr/bin/env python3

CLOUD = False
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

    CLOUD = True

import sys
import time
import requests
import fileinput
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

LOGGER = polyinterface.LOGGER


def cardinal_direction(course):
    # Returns the Cardinal Direction Name
    if 0 <= course <= 11.24:
        return 1
    elif 11.25 <= course <= 33.74:
        return 2
    elif 33.75 <= course <= 56.24:
        return 3
    elif 56.25 <= course <= 78.74:
        return 4
    elif 78.75 <= course <= 101.24:
        return 5
    elif 101.25 <= course <= 123.74:
        return 6
    elif 123.75 <= course <= 146.24:
        return 7
    elif 146.25 <= course <= 168.74:
        return 8
    elif 168.75 <= course <= 191.24:
        return 9
    elif 191.25 <= course <= 213.74:
        return 10
    elif 213.75 <= course <= 236.24:
        return 11
    elif 236.25 <= course <= 258.74:
        return 12
    elif 258.75 <= course <= 281.24:
        return 13
    elif 281.25 <= course <= 303.74:
        return 14
    elif 303.75 <= course <= 326.24:
        return 15
    elif 326.25 <= course <= 348.74:
        return 16
    elif 348.75 <= course <= 360:
        return 1
    else:
        return 0

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = "Traccar"
        self.user = None
        self.password = None
        self.traccar_host = None
        self.traccar_port = None
        self.disco = 0
        self.ingress = None
        self.session = requests.Session()

    def traccar_connect(self, api_method):
        try:
            url = "http://" + self.traccar_host + ":" + self.traccar_port + "/api/" + api_method
            r = self.session.get(url, auth=(self.user, self.password))
            data = r.json()
            return data
        except Exception as ex:
            LOGGER.error('Exception in connecting to Traccar server: ' + str(ex))

    def get_devices(self):
        devices = self.traccar_connect('devices')
        return devices

    def get_geofences(self):
        geofences = self.traccar_connect('geofences')
        return geofences

    def get_positions(self):
        positions = self.traccar_connect('positions')
        return positions

    def start(self):
        LOGGER.info('Started Traccar')
        if self.check_params():
            self.discover()

        if CLOUD:
            LOGGER.debug("-----------------------------------")
            LOGGER.debug("httpsIngress: " + str(self.poly.init['netInfo']['httpsIngress']))
            LOGGER.debug("publicIp: " + self.poly.init['netInfo']['publicIp'])
            LOGGER.debug("-----------------------------------")
            self.ingress = self.poly.init['netInfo']['httpsIngress']
            # self.addCustomParam({'ingress_url': self.ingress})
            self.addNotice({'traccarIngress': self.ingress})

            # Start the CallBackServer
            httpd = HTTPServer(('0.0.0.0', 3000), CallBackServer)
            httpd.serve_forever()
        else:
            httpd = HTTPServer(('0.0.0.0', 3180), CallBackServer)
            httpd.serve_forever()

    def shortPoll(self):
        pass
        if self.disco == 1:
            # LOGGER.info('Running Short Poll')
            devices = self.get_devices()
            if devices is not None:
                for device in devices:
                    _id = str(device['id'])
                    _status = device['status']
                    _name = device['name']

                    _geofenceIds = device['geofenceIds']
                    if len(_geofenceIds) > 0:
                        _fenceId = _geofenceIds[0]
                    else:
                        _fenceId = 0

                    if _status == "online":
                        _st = 1
                    elif _status == "offline":
                        _st = 0
                    else:
                        _st = 0

                    self.nodes[_id].setDriver('ST', _st)
                    self.nodes[_id].setDriver('GV0', _fenceId)

            positions = self.get_positions()
            if positions is not None:
                for pos in positions:
                    _id = str(pos['deviceId'])

                    if 'batteryLevel' in pos['attributes']:
                        _battery = int(pos['attributes']['batteryLevel'])
                    else:
                        _battery = 0
                    self.nodes[_id].setDriver('BATLVL', _battery)

                    if 'ignition' in pos['attributes']:
                        ignition = int(pos['attributes']['ignition'])
                    else:
                        ignition = 0
                    self.nodes[_id].setDriver('GV2', ignition)

                    if 'motion' in pos['attributes']:
                        _motion = pos['attributes']['motion']
                        if _motion:
                            _motion = 1
                        else:
                            _motion = 0
                    else:
                        _motion = 0
                    self.nodes[_id].setDriver('GV1', _motion)

                    if 'speed' in pos:
                        _speed = int(pos['speed'])
                    else:
                        _speed = 0
                    self.nodes[_id].setDriver('SPEED', _speed)

                    if 'course' in pos:
                        _course = round(pos['course'], 2)
                        val = cardinal_direction(_course)
                    else:
                        val = 0
                    self.nodes[_id].setDriver('GV3', val)

    def longPoll(self):
        pass

    def query(self, command=None):
        self.shortPoll()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        units = self.get_devices()
        if units is not None:
            for unit in units:
                LOGGER.info("Adding: " + str(unit['id']) + ": " + unit['name'])
                self.addNode(TraccarNode(self, self.address, str(unit['id']).lower(), unit['name']))

            self.update_profile(self)
            self.disco = 1

    def delete(self):
        LOGGER.info('Removing Traccar Nodeserver')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        st = True
        self.remove_notices_all()

        default_user = "YourUserName"
        default_password = "YourPassword"
        default_traccar_host = "127.0.0.1"
        default_traccar_port = "8082"

        if 'user' in self.polyConfig['customParams']:
            self.user = self.polyConfig['customParams']['user']
        else:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(self.user))
            st = False

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = default_password
            LOGGER.error(
                'check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            st = False

        if 'traccar_host' in self.polyConfig['customParams']:
            self.traccar_host = self.polyConfig['customParams']['traccar_host']
        else:
            self.traccar_host = default_traccar_host
            LOGGER.error('check_params: Traccar Host not defined in customParams, please add it.  Using {}'.format(
                self.password))
            st = False

        if 'traccar_port' in self.polyConfig['customParams']:
            self.traccar_port = self.polyConfig['customParams']['traccar_port']
        else:
            self.traccar_port = default_traccar_port

        # Make sure they are in the params
        self.addCustomParam({'user': self.user, 'password': self.password,
                             'traccar_host': self.traccar_host, 'traccar_port': self.traccar_port})

        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password:
            self.addNotice({'myNotice':
                            'Traccar access is not configure.  Please configure and restart this nodeserver'})
            st = False

        if st:
            return True
        else:
            return False

    def remove_notices_all(self):
        LOGGER.info('remove_notices_all:')
        self.removeNoticesAll()

    def update_profile(self, command):
        LOGGER.info('update_profile:')

        file_input = 'profile/nls/en_us.txt'
        geofences = self.get_geofences()
        if geofences is not None:
            # Remove GEOFENCE-NAME Entries
            for line in fileinput.input(file_input, inplace=True, backup='.bak'):
                if re.match(r'^GEOFENCE-NAME-\d+\s=\s\w+.+', line):
                    pass
                else:
                    print(line.rstrip())

            # Add new GEOFENCE-NAME Entries
            nls_file = open(file_input, "a")
            nls_file.write("GEOFENCE-NAME-0 = None" + "\n")
            for fence in geofences:
                nls_file.write("GEOFENCE-NAME-" + str(fence['id']) + " = " + fence['name'] + "\n")

            nls_file.close()

            st = self.poly.installprofile()
            return st

    def callback(self, event_data):
        # LOGGER.debug("Running Callback")
        if 'event' in event_data:
            if event_data['event']['type'] == 'deviceOnline':
                device_id = str(event_data['event']['deviceId'])
                self.nodes[device_id].setDriver('ST', 1)

            if event_data['event']['type'] == 'deviceOffline':
                device_id = str(event_data['event']['deviceId'])
                self.nodes[device_id].setDriver('ST', 0)

            if event_data['event']['type'] == 'deviceMoving':
                device_id = str(event_data['event']['deviceId'])
                self.nodes[device_id].setDriver('GV1', 1)

            if event_data['event']['type'] == 'deviceStopped':
                device_id = str(event_data['event']['deviceId'])
                self.nodes[device_id].setDriver('GV1', 0)

            if event_data['event']['type'] == 'geofenceEnter':
                device_id = str(event_data['event']['deviceId'])
                geofence_id = str(event_data['event']['geofenceId'])
                self.nodes[device_id].setDriver('GV0', geofence_id)

            if event_data['event']['type'] == 'geofenceExit':
                device_id = str(event_data['event']['deviceId'])
                # geofence_id = str(event_data['event']['geofenceId'])
                self.nodes[device_id].setDriver('GV0', 0)

        if 'position' in event_data:
            device_id = str(event_data['position']['deviceId'])
            speed = round(event_data['position']['speed'], 2)
            _course = round(event_data['position']['course'], 2)
            course = cardinal_direction(_course)
            _status = str(event_data['device']['status'])

            if _status == "online":
                val = 1
            else:
                val = 0
            self.nodes[device_id].setDriver('ST', val)

            if 'ignition' in event_data['position']['attributes']:
                ignition = event_data['position']['attributes']['ignition']
                if ignition:
                    val = 100
                else:
                    val = 0
                self.nodes[device_id].setDriver('GV2', val)

            if 'batteryLevel' in event_data['position']['attributes']:
                battery = event_data['position']['attributes']['batteryLevel']
                self.nodes[device_id].setDriver('BATLVL', battery)

            if 'motion' in event_data['position']['attributes']:
                motion = event_data['position']['attributes']['motion']
                if motion:
                    val = 1
                else:
                    val = 0
                self.nodes[device_id].setDriver('GV1', val)

            self.nodes[device_id].setDriver('SPEED', speed)
            self.nodes[device_id].setDriver('GV3', course)

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]


class TraccarNode(polyinterface.Node):
    def __init__(self, controller, primary, address, name):
        super(TraccarNode, self).__init__(controller, primary, address, name)

    def start(self):
        self.setDriver('ST', 0)

    # def setOn(self, command):
    #     self.setDriver('ST', 0)
    #
    # def setOff(self, command):
    #     self.setDriver('ST', 0)

    def query(self):
        self.reportDrivers()

    '''
    ST:     Online
    BATLVL: Battery (mobile app)
    SPEED:  Vehicle/Tracker Speed
    GV0:    Geofence
    GV1:    In Motion
    GV2:    Ignition
    GV3:    Course/Direction
    '''

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'BATLVL', 'value': 0, 'uom': 51},
        {'driver': 'SPEED', 'value': 0, 'uom': 48},
        {'driver': 'GV0', 'value': 0, 'uom': 25},
        {'driver': 'GV1', 'value': 0, 'uom': 2},
        {'driver': 'GV2', 'value': 0, 'uom': 78},
        {'driver': 'GV3', 'value': 0, 'uom': 25},
    ]

    id = 'TRACCAR'
    commands = {
        # 'DON': setOn, 'DOF': setOff
    }


class CallBackServer(BaseHTTPRequestHandler):
    LOGGER.info('Starting CallBack Server')

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_response()

    def do_GET(self):
        self._set_response()

    def do_POST(self):
        self._set_response()
        content_length = int(self.headers['Content-Length'])
        raw_post_data = self.rfile.read(content_length)
        _event = json.loads(raw_post_data.decode('utf-8'))
        control.callback(_event)


if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Traccar')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
        polyglot.stop()
        sys.exit(0)
