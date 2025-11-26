# Interface Statistics Aggregated Query

Interface statistics Aggregation Query API to retrieve sum of octets for each interface in a given Service VPN of device with system-ip "10.0.0.1" for last 12 hours.

## API URL:

`https://{{manager}}:{{port}}/dataservice/statistics/interface/aggregation`

## Example 1

Method: POST

## Query:

```json
{
  "query": {
    "condition": "AND",
    "rules": [
      {
        "value": [ "12" ],
        "field": "entry_time",
        "type": "date",
        "operator": "last_n_hours"
      },
      {
        "value": [ "10.0.0.1" ],
        "field": "vdevice_name",
        "type": "string",
        "operator": "in"
      },
      {
        "value": [ "1" ],
        "field": "vpn_id",
        "type": "number",
        "operator": "in"
      }
    ]
  },
  "aggregation": {
    "field": [
      {
        "property": "interface",
        "sequence": 1
      }
    ],
    "metrics": [
      {
        "property": "rx_octets",
        "type": "sum"
      },
      {
        "property": "tx_octets",
        "type": "sum"
      }
    ]
  }
}
```

## Sample Response

```json
    "data": [
        {
            "interface": "ge0/2",
            "count": 70,
            "rx_octets": 32509568,
            "tx_octets": 260399334
        },
        {
            "interface": "loopback1",
            "count": 70,
            "rx_octets": 0,
            "tx_octets": 0
        }
    ]
```

## Example 3

Interface statistics Aggregation Query API to retrieve sum of octets for each interface in a given Service VPN across all devices in the fabric for last 12 hours.

Method: POST

Query:

```json
{
  "query": {
    "condition": "AND",
    "rules": [
      {
        "value": [
          "12"
        ],
        "field": "entry_time",
        "type": "date",
        "operator": "last_n_hours"
      },
      {
        "value": [
          "1"
        ],
        "field": "vpn_id",
        "type": "number",
        "operator": "in"
      }
    ]
  },
  "aggregation": {
    "field": [
      {
        "property": "interface",
        "sequence": 1
      },
      {
        "property": "vdevice_name",
        "sequence": 2
      },
      {
        "property": "vpn_id",
        "sequence": 3
      }
    ],
    "metrics": [
      {
        "property": "rx_octets",
        "type": "sum"
      },
      {
        "property": "tx_octets",
        "type": "sum"
      }
    ]
  }
}
```

Sample Response

```json
    "data": [
        {
            "interface": "ge0/2",
            "count": 72,
            "vdevice_name": "1.1.2.211",
            "vpn_id": "1",
            "rx_octets": 261953,
            "tx_octets": 156828
        },
        {
            "interface": "ge0/2",
            "count": 72,
            "vdevice_name": "1.1.2.5",
            "vpn_id": "1",
            "rx_octets": 241920,
            "tx_octets": 0
        },
        {
            "interface": "ge0/2",
            "count": 71,
            "vdevice_name": "1.1.2.210",
            "vpn_id": "1",
            "rx_octets": 257941,
            "tx_octets": 154526
        },
        {
            "interface": "ge0/2",
            "count": 70,
            "vdevice_name": "1.1.2.1",
            "vpn_id": "1",
            "rx_octets": 32509568,
            "tx_octets": 260399334
        },
        {
            "interface": "ge0/2",
            "count": 70,
            "vdevice_name": "1.1.2.200",
            "vpn_id": "1",
            "rx_octets": 266279454,
            "tx_octets": 20932398
        },
<snip>
```
