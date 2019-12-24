# Traccar Nodeserver

## Basic Requirements
* Traccar Server
* Traccar Clients
  * Mobile App
  * Real GPS devices
* Polyglot / Polisy
  
## Installation
- Install from the Polyglot Store

## Basic Configuration
* Configuration is done in the Polyglot Traccar Nodeserver configuration page.  You 
will need to know your Traccar Server information
  * Traccar admin username / password
    * Can be none admin as long as permissions are setup correctly
  * Traccar IP or name if DNS is setup correctly
  * Traccar Web Port (default unless changed by you)

## Basic Functions
* The Nodeserver by default will poll the Traccar server every 1 minute to get updated
device and position information.  This can be changed via shortPoll option.

* Geofences are pulled from the Traccar server and the profile is auto created with
the proper names.  If you add a Geofence to Traccar you will need to upload the profile
and restart the Admin Console.  The upload profile button is in the primary Traccar node.

### Usage
A node is created for each Traccar client (GPS unit) within the Traccar server.  Each node
currently has the following status values:
* Online
  * GPS Units send a heartbeat to Traccar.  This value will change from True/False when the device changes
  from online/offline within the Traccar server.
* Battery Level
  * Mobile App client provides the phone battery level
  * Some vehicle GPS units provide the vehicle battery information
* Speed
  * Current speed of the vehicle or gps client
* Geofence
  * Current geofence a unit is inside of
* In Motion
  * True/False is the unit in motion
* Ignition
  * If supported by the GPS unit the vehicle ignition is reported
* Course
  * Cardinal direction the GPS unit is heading/facing

There are a lot more possible status values available.  If there's something you would like that is available submit
a issue requesting it and provide use case example for use to present via the nodeserver.

## Advanced Configuration
Full documentation on Github [udi-poly-traccar](https://github.com/simplextech/udi-poly-traccar)
