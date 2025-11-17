# Alarms APIs

[Cisco IOS XE Catalyst SD-WAN Alarms Guide](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/alarms-reference-guide/cisco-ios-xe-catalyst-sd-wan-alarms-guide/sd-wan-alarms-guide.html)

## Notes

With our current (Viptela) API monitoring solution, we are currently using both **rulename** and **component** fields to specifically group and correlate events for our ITOM platform to reduce ticket noise, my concern is that since there are a number of new alarms then there could also be new variables to consider.

We have been able to find the component variables list using /event/component/keyvalue API, but having trouble finding an equivalent variables list for "rulename".

Would you have a list of all the variables that can be returned in the "rulename" field? (highlighted in the sample JSON response below).

The closest I've been able to find is using the /event/types/keyvalue endpoint, are they the same values? if so we can use those.

## TL/DR

- Get alarms: `GET https://{{vmanage}}:{{port}}/dataservice/alarms`
- Get the components: `GET https://<>/dataservice/event/component/keyvalue`
- Get the event names (rulenames): `GET https://<>/dataservice/event/types/keyvalue`
- Get the rulenames: `https://{{vmanage}}:{{port}}/dataservice/alarms/rulenamedisplay/keyvalue`
- Get severity mapping: `GET https://{{vmanage}}:{{port}}/dataservice/alarms/severitymappings`

## Get Alarms

`GET https://{{vmanage}}:{{port}}/dataservice/alarms` endpoint:

Example:

```json
    "data": [
        {
            "suppressed": false,
            "devices": [
                {
                    "system-ip": "10.10.1.15"
                }
            ],
            "eventname": "memory-usage",
            "type": "memory-usage",
            "rulename": "memory-usage",
            "component": "System",
            "entry_time": 1752550188330,
            "statcycletime": 1752549967210,
            "message": "System memory usage is above 93%",
            "severity": "Critical",
            "severity_number": 1,
            "uuid": "36055fd8-b802-495e-88f8-de80f00bf6fd",
            "values": [
                {
                    "system-ip": "10.10.1.15",
                    "host-name": "site2-cedge01",
                    "memory-status": "usage-critical"
                }
            ],
            "rule_name_display": "Memory_Usage",
            "receive_time": 1752550188329,
            "values_short_display": [
                {
                    "host-name": "site2-cedge01",
                    "system-ip": "10.10.1.15",
                    "memory-status": "usage-critical"
                }
            ],
            "system_ip": "10.10.1.15",
            "acknowledged": false,
            "active": true,
            "tenant": "default",
            "id": "AZgMIaUvQA2v7zEucE-M"
        },
 ```

Bulk API to collect alarms:

`GET https://{{vmanage}}:{{port}}/dataservice/data/device/statistics/alarm?startDate={{startDate}}&endDate={{endDate}}&timeZone={{timeZone}}&count={{count}}"

## Components

Find the component variables (Policy, NAT, BFD, APP-Route, System, Control...)

The following endoint returns components:

`GET https://<>/dataservice/event/component/keyvalue`

See [Example of response (20.18)](./alarms/components.json)

## Types (event names, rulenames)

**Event type** possible values, get the list using:

`https://{{vmanage}}:{{port}}/dataservice/event/types/keyvalue`

See [Example](./alarms/event-types.json)

**rulename** possible values, get the list using:

`https://{{vmanage}}:{{port}}/dataservice/alarms/rulenamedisplay/keyvalue`

See [Example](./alarms/alarms-rulenamedisplay.json)

## Severity Mappings

Get all possible values for alarms, and the corresponding severity mapping:

`GET https://{{vmanage}}:{{port}}/dataservice/alarms/severitymappings`

Check [Example of response (20.18)](./alarms/severity-mapping.json)

