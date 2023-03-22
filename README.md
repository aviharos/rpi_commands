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

This repository contains only the service. The actual sample configuration and Arduino code is in another repository [here](https://github.com/aviharos/rpi_commands_default_config). You need both the service repository and a config repository for the service.

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
- `"reset"`: the Storage is resetted. If parts accumulate in it during production, it is emptied. If parts are taken repeatedly of it during production, it is filled.
- `"set_empty"`
- `"set_full"`
- `"step"`: an item is taken away from the storage or a part enters the storage, based on the type of the storage.

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

The previous request will order the service to send the "request" key's value as plain text to the iotagent-http over HTTP.

### How the service gets commands from the microcontroller
The microcontroller sends commands to this service through USB connection. Each json consists of a command id and an optional argument as follows:

    {"InjectionMouldingMachine1_on": null}

This triggers the `"InjectionMouldingMachine1_on"` command without any argument.


## Demo

You can try the OEE microservice as described [here](https://github.com/aviharos/momams#try-momams).

## Testing

WARNING: the tests set environment variables, change the Orion Context Broker and PostgreSQL data. Any overwritten data is deleted forever. Proceed at your own risk.

## Limitations
The service currently cannot handle HTTPS and Fiware’s authentication system.

## License

[MIT license](LICENSE)

The Robo4Toys TTE does not hold any copyright of any FIWARE or 3rd party software.

