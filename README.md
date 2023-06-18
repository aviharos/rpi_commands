# rpi_commands
[![License: MIT](https://img.shields.io/github/license/ramp-eu/TTE.project1.svg)](https://opensource.org/licenses/MIT)

A GNU/Linux service that can send data to the Fiware Orion Context Broker based on pre-defined events

## Contents

- [OEE](#title)
  - [Contents](#contents)
  - [Background](#background)
  - [Usage](#usage)
  - [API](#api)
  - [Demo](#demo)
  - [Testing](#testing)
  - [Limitations](#limitations)
  - [License](#license)

## Background

The [Fiware Orion Context Broker]() can be configured to send notifications to Fiware Cygnus whenever an object changes. Cygnus can be configured to log all historical data into a time series database (in our case, PostgreSQL), as you can see [here](https://github.com/FIWARE/tutorials.Historic-Context-Flume).

This service is designed to be used with [MOMAMS](https://github.com/aviharos/momams), an open-source manufacturing informatics system based on [Fiware technology](https://github.com/Fiware/tutorials.Getting-Started). MOMAMS gets data from a piece of manufacturing equipment (a machine, a PLC, a robot controller, etc.). Sometimes these data are only available as 0-24 V DC signals, but not as JSON data packets sent over HTTP. This microservice can be used with a microcontroller to help this issue. Optocouplers can be used to transform 0-24 V DC signals to 0-5 V DC signals. Then a microcontroller can read and decode the signals. Whenever a significant change occurs in the supervised manufacturing system, the microcontroller sends a JSON to this service. This service then uploads a specific data packet to the Orion Context Broker through HTTP.

The microservice can run directly on the MOMAMS server or a Raspberry Pi.

This repository contains only the service. It is up to you to write the microcontroller's program. The sample configuration and Arduino code is in a config repository [here](https://github.com/aviharos/rpi_commands_default_config). You need both the service repository and a config repository for the service. You can modify the configuration repository according to the details listed here.

## Requirements

You need MOMAMS up and running and the configuration files ready in the config repository according to this documentation. Make sure to read the MOMAMS docs first, including the OEE microservice's logs.

## Usage

### Identify the significant events
You need to identify all the significant events in your manufacturing system. For example:
- the machine is turned on 
- the machine is turned off
- a set of good products is made
- a set of reject products are made.

### Specify a command for each event
Then you need to specify a command for each event in [commands.json](https://github.com/aviharos/rpi_commands_default_config/blob/main/commands.json) in the configuration repository. The key-value pairs in this JSON file are the command id and command data respectively. For example, in the following example `"InjectionMouldingMachine1_on"` is the key. The `"object_id"` means the id of the Orion object to be changed, in this case: `"urn:ngsiv2:i40Asset:InjectionMouldingMachine1"`. `"type"` means the type of action to perform, in this case: `"turn_on"`.

    "InjectionMouldingMachine1_on": {
            "object_id": "urn:ngsiv2:i40Asset:InjectionMouldingMachine1",
            "type": "turn_on"
    }

### Valid command types for the different object types

#### "urn:ngsiv2:i40Asset", "i40AssetType": "Workstation"
- `"turn_on"`: when the Workstation is turned on 
- `"turn_off"`: when the Workstation is turned off
- `"handle_good_cycle"`: a set of good parts is made
- `"handle_reject_cycle"`: a set of reject parts is made

#### "urn:ngsiv2:i40Asset", "i40AssetType": "Storage"
Storages can have two types:
- `"filling"`: the storage is normally empty and items accumulate in it during production. It needs to be emptied from time to time.
- `"emptying"`: the storage is normally full and items leave it during production. It needs to be filled from time to time.

- `"reset"`: the Storage is resetted. If parts accumulate in it during production, it is emptied. If parts are taken repeatedly of it during production, it is filled.
- `"set_empty"`
- `"set_full"`
- `"step"`: an item is taken away from the storage (type: `"emptying"`) or a part enters the storage (type: `"filling"`), based on the type of the storage.

You do not need to provide the current number of items in the storage, just these events. The microservice tracks the number of items in the storage and updates the MOMAMS objects accordingly.

### Special requests
Special requests are forwarded to the [iotagent-http](https://github.com/aviharos/iotagent-http) of MOMAMS. For example:

    "change_job_to_202200047": {
        "special": null,
        "request": {
            "url": "http://orion:1026/v2/entities/urn:ngsi_ld:Workstation:InjectionMoulding1/attrs/RefJob/value",
            "method": "PUT",
            "headers": [
                "Content-Type: text/plain"
            ],
            "data": "urn:ngsi_ld:Job:202200047"
        }
    }

The value of the key `"request"` will be sent in plain text format to the IoT agent over HTTP. For more details about how to construct a custom request, see the IoT agent's docs.

### How the service gets commands from the microcontroller
The microcontroller sends commands to this service through USB connection. Each json consists of a command id and an optional argument as follows:

    {"InjectionMouldingMachine1_on": null}

This triggers the `"InjectionMouldingMachine1_on"` command without any argument. You need to program your microcontroller so that whenever an important change happens in the manufacturing system, the microcontroller sends a JSON over serial connection with the proper event id specified.

### Setting environment variables
The microservice gets to know necessary information using environment variables. These need to be specified in the config repo's `.env` file.

- `IOTAGENT_HTTP_PORT=4315`: the IoT agent's port on the MOMAMS server.
- `LOGGING_LEVEL=WARNING`: the logging level. The more detailed logs you want, the more space the log file will take. Options:
    - `DEBUG`
    - `INFO`
    - `WARNING`
    - `ERROR`
    - `CRITICAL`
- `ORION_HOST=localhost`: the MOMAMS host that is equivalent to the Orion host.
- `ORION_PORT=1026`: the Orion port.
- `TIMEOUT=10`: the timeout of the HTTP requests.

The log file's location according to [rc.local](rc.local): `/tmp/rc.local.log`.

### Auto-starting the service
It is recommended that you auto-start the service whenever the device used to run the service turns on. To do so, make a copy of rc.local and replace it with the rc.local found in this directory. Whenever the OS starts up, it will run `/etc/rc.local` as a shell script. For this reason, make sure that it has no errors that could possibly break the startup of the OS.

    sudo cp /etc/rc.local /etc/rc.local.bak 
    sudo cp /path/to/new/rc.local /etc/rc.local 

3 other things need to be set in addition in rc.local in separate environment variables.
    - the path to the service repository (line 24)
    - the path to the config repository (line 25)
    - the selected microcontroller (line 26)

    sudo nano /etc/rc.local

You can get the Arduino's path in various ways, for example using the command below.

    ls /dev/ttyUSB*

## Demo

You can try MOMAMS as described [here](https://github.com/aviharos/momams#try-momams).

If you want to try MOMAMS with this microservice and an Arduino sensing the events, you will need:
- a computer running docker on native GNU/Linux (x64) that will be used as the MOMAMS server
- a Raspberry Pi for running this service (python 3.6+ is required) (you can use any suitable computer, but we will refer to the second one as "Raspberry Pi")
- an Arduino
- a breadboard
- 3 buttons
- a few wires
- an USB cable to connect the Arduino with the computer.

### Install MOMAMS on the server
Please follow the the [Try MOMAMS section's instructions](https://github.com/aviharos/momams#try-momams) from subsection [Install curl](https://github.com/aviharos/momams#install-curl) to [Install Postman](https://github.com/aviharos/momams#install-postman).

### Create the connections for the Arduino
You should follow [this](https://docs.arduino.cc/tutorials/generic/digital-input-pullup) setup for pins 2, 3 and 4 using separate buttons. You need to connect all buttons in the same way to pins 2-4. It would be nice to have a toggle for button 2, but it is not needed.

Pin layout:
- pin 2: availability signal:
    - continuous HIGH: injection moulding machine on
    - continuous LOW: injection moulding machine off
- pin 3: mould close signal:
    - as long as the mould is closed, continuous HIGH
    - LOW otherwise
- pin 4: reject part signal:
    - impulse: if a reject part has been detected.

When the availability signal has a positive edge, the Arduino sends the event `"InjectionMouldingMachine1_on"`. When it has a negative edge, the Arduino sends the event `"InjectionMouldingMachine1_off"`. Both events are resent every 60 seconds.

The Arduino code is written in a way so that whenever pin 3 has a negative edge, the Arduino will notify the service that parts are completed. If there was a positive edge of the reject signal during the mould close signal's HIGH state, the Arduino will send `"InjectionMouldingMachine1_reject_parts_completed"`. Otherwise: `"InjectionMouldingMachine1_good_parts_completed"`.

When testing, you should press button 2, then make parts using buttons 3 and 4.

### Load the Arduino code to the Arduino
The [code](https://github.com/aviharos/rpi_commands_default_config/blob/main/rpi_commands_default_config.ino) can be found in the config repository. You can test the way the Arduino works using Arduino IDE.

### Plug the Arduino into the Raspberry Pi via USB
The Arduino will get power from the Raspberry Pi and send data through USB.

### Install and configure the microservice to start automatically on the Raspberry Pi

#### Installing the microservice
Install python package requests for HTTP connection, pyserial for USB communication:

    pip install requests pyserial

Clone the repositories. Print their paths:

    cd ~
    git clone https://github.com/aviharos/rpi_commands_default_config.git
    git clone https://github.com/aviharos/rpi_commands.git
    echo $(pwd)/rpi_commands_default_config
    echo $(pwd)/rpi_commands 

Note the last two paths you see. The first is the absolute path of the microservice, the second is the absolute path of the config directory. You will need to specify them as absolute paths later, not relative paths, because `~` means something different for the root user running rc.local.

If you are using the default username, the repositories will be located at 

    /home/pi/rpi_commands_default_config
    /home/pi/rpi_commands

The default config will be used with the default environment variables.

#### Set the MOMAMS host's IP address in the Raspberry Pi
    
    cd rpi_commands_default_config
    nano .env

In this .env file, set the ORION_HOST environment variable to the IP address of the MOMAMS server.


#### Find the Arduino's path
Plug in the Arduino to the Raspberry Pi that will eventually run the microservice. You will need its path. These queries often work:

    ls /dev/ttyUSB*
    ls /dev/ttyA*

If you have only one Arduino plugged in, the path you see will most likely be the Arduino. However you can check its path the Arduino IDE. Note: the Arduino IDE and the microservice cannot run simultaneously. Note this path.

##### Configure auto-start
Make the microservice auto-start:

    sudo cp /etc/rc.local /etc/rc.local.bak 
    sudo cp ~/rpi_commands/rc.local /etc/rc.local 

#### Specify key environment variables:

    sudo nano /etc/rc.local

Write the config repository's absolute path into the template in line 24, the microservice's absolute path in line 25, the Arduino's path in line 26.

From now on, any time the Raspberry Pi reboots, the microservice will start. You can inspect its logs any time:

    cat /tmp/rc.local.log

Now the configuration is complete. You just need to start up the system.

### Start MOMAMS on the server
Please follow the the [Try MOMAMS section's instructions](https://github.com/aviharos/momams#try-momams) from the subsection [Start MOMAMS](https://github.com/aviharos/momams#start-momams) to [Notify Cygnus of context changes](https://github.com/aviharos/momams#notify-cygnus-of-all-context-changes). Do not perform any action in Postman.

### Init objects in MOMAMS
The Raspberry Pi - Arduino duo will not create new data objects in MOMAMS under normal operating conditions. For this reason, you need to create the objects yourself at startup so that the Raspberry Pi can modify them.

Since the config directory is already present at the Raspberry Pi, we will use it to create the objects all at once.

Change the directory to the configuration repository (`/path/to/rpi_commands_default_config`), then issue the commands

    cd /path/to/rpi_commands_default_config
    source set_env.sh
    python reupload_jsons_to_Orion.py

The last line runs a python script that uploads the default config's data objects to MOMAMS. If those objects already exist, they will be overwritten.

### Start the microservice
You only need to reboot the Raspberry Pi to start the microservice.

    sudo reboot

### Use the buttons connected to the Arduino to control the "injection moulding machine"
Now you can use the Arduino's buttons to imitate production. You can always query any Orion object to see how objects change according to your button pushes like [this](https://www.tinkercad.com/things/bfzLSh7QfSl-rpi-commands-demo-arduino-setup). When using an actual production machine, you have your machine's signals transformed to 5 V levels using optocouplers instead of the buttons.

You can query the current state of the `InjectionMouldingMachine1` and the `Job000001` objects and verify that MOMAMS is working, the `goodPartCounter` and `rejectPartCounter` attributes are tracked and the OEE values are calculated:

    curl --location --request GET 'http://localhost:1026/v2/entities/urn:ngsiv2:i40Asset:InjectionMouldingMachine1?options=keyValues' | json_pp

    curl --location --request GET 'http://localhost:1026/v2/entities/urn:ngsiv2:i40Process:Job000001?options=keyValues' | json_pp

The default configuration can be used out-of-the-box with an injection moulding machine with the following pin layout:

- pin 2: injection moulding machine automatic / not automatic
- pin 3: mould close signal
- pin 4: reject signal

## Testing

WARNING: the service's tests set environment variables, change the Orion Context Broker and PostgreSQL data. Any overwritten data is deleted forever. Proceed at your own risk. You can run the [test](test) folder's tests one by one.

## Limitations
The service currently cannot handle HTTPS and Fiware’s authentication system.

## License

[MIT license](LICENSE)

The Robo4Toys TTE does not hold any copyright of any FIWARE or 3rd party software.

