# USAGE

3 Main Monitoring API Categories:

- Device real-time monitoring: `/dataservice/device` endpoint
- Statistics APIs: `/dataservice/statistics` endpoint
- Statistics Bulk APIs: `/dataservice/data` endpoint

## Realtime Statistics

Realtime monitoring APIs query device state and information in real time.

Example: Get realtime tunnel performance for a specific tunnel between two sdwan edge routers

```bash
❯ python app.py approute-device
Enter System IP address : 10.0.0.1
Enter Remote System IP address : 10.0.0.2
Enter color : mpls

Realtime App route statistics for 10.0.0.1 to 10.0.0.2

╒═════════════════════╤════════════════════╤═════════╤════════════════╤═══════════════╤═════════════╤═══════════════════╤══════════════════╤════════╕
│ vdevice-host-name   │ remote-system-ip   │   Index │   Mean Latency │   Mean Jitter │   Mean Loss │   average-latency │   average-jitter │   loss │
╞═════════════════════╪════════════════════╪═════════╪════════════════╪═══════════════╪═════════════╪═══════════════════╪══════════════════╪════════╡
│ edge1-paris         │ 10.0.0.2           │       0 │              1 │             0 │           0 │                 1 │                0 │      0 │
├─────────────────────┼────────────────────┼─────────┼────────────────┼───────────────┼─────────────┼───────────────────┼──────────────────┼────────┤
│ edge1-paris         │ 10.0.0.2           │       1 │              1 │             0 │           0 │                 1 │                0 │      0 │
├─────────────────────┼────────────────────┼─────────┼────────────────┼───────────────┼─────────────┼───────────────────┼──────────────────┼────────┤
│ edge1-paris         │ 10.0.0.2           │       2 │              1 │             0 │           0 │                 1 │                0 │      0 │
├─────────────────────┼────────────────────┼─────────┼────────────────┼───────────────┼─────────────┼───────────────────┼──────────────────┼────────┤
│ edge1-paris         │ 10.0.0.2           │       3 │              1 │             0 │           0 │                 1 │                0 │      0 │
├─────────────────────┼────────────────────┼─────────┼────────────────┼───────────────┼─────────────┼───────────────────┼──────────────────┼────────┤
│ edge1-paris         │ 10.0.0.2           │       4 │              1 │             0 │           0 │                 1 │                0 │      0 │
╘═════════════════════╧════════════════════╧═════════╧════════════════╧═══════════════╧═════════════╧═══════════════════╧══════════════════╧════════╛

❯
```

## Statistics APIs

### Overview

The SD-WAN Manager NMS statistics database collects statistics from all WAN Edge routers periodically, starting from when they joined the overlay network.
The SD-WAN Manager API query language allows you to build queries that retrieve selected statistics from the SD-WAN Manager NMS statistics database

Simple Query

- In a simple query, you specify the name or names of the fields whose values you want to retrieve, the time period over which to retrieve the value, and the order in which to sort the retrieved data.
- For example, you can retrieve statistics for an IP address for the last 6 hours, and you can sort them in descending order by hostname

Aggregated Query

- vManage aggregate queries retrieve aggregated data from the vManage statistics database. With aggregation, you can sum, count, and average data in retrieved records, display the minimum and maximum values in the retrieved records, and display a specific record. In addition, you can group and bucketize data.
- In an aggregation query, you define the number of records to retrieve, the query conditions and rules, and the operation to aggregate the retrieved data in the output. 

Aggregation API query is created using below constructs

- Query Conditions
- Aggregation components:
  - Field
  - Histogram
  - Metrics

For example, we need to first define Query Conditions(rules) Based on these rules the data records are extracted from vManage. Some of the common supported rules are to select based on stats entry_time to get statistics in specific intervals of time, then use various query fields like local system-ip, local color, remote color to retrieve the records for specific vEdge routers transport circuits in that time interval.

Once the query conditions are determined, you then provide the fields, histogram and metrics, which determine how data is aggregated.

### Commands available

```bash
❯ python app.py
Usage: app.py [OPTIONS] COMMAND [ARGS]...

  Command line tool for to collect application names and tunnel performances.

Options:
  --help  Show this message and exit.

Commands:
  app-list         Retrieve the list of Applications.
  app-list2        Retrieve the list of Applications.
  app-qosmos       Retrieve the list of Qosmos Applications (original...
  approute-device  Get Realtime Approute statistics for a specific tunnel...
  approute-fields  Retrieve App route Aggregation API Query fields.
  approute-stats   Create Average Approute statistics for all tunnels...

>
```

### Example-1 - Query fields

Example

```bash
❯ python app.py approute-fields
vdevice_name(string)  local_system_ip(string)   src_ip(string)    loss_percentage(number)  name(string)
host_name(string)     remote_system_ip(string)  dst_ip(string)    jitter(number)           loss(number)
device_model(string)  local_color(string)       src_port(number)  tx_pkts(number)
statcycletime(date)   remote_color(string)      dst_port(number)  rx_pkts(number)
entry_time(date)      proto(string)             total(number)     tx_octets(number)
vip_idx(number)       window(number)            latency(number)   rx_octets(number)

❯ 
```

### Example-2 - approute-stats

The following example query retrieves average latency/loss/jitter and vqoe score for the last hour for all tunnels between routers with provided local and remote system-ip.

payload snippet:

```json
{
    "query": {
        "condition": "AND",
        "rules": [
            {
                "value": ["1"],
                "field": "entry_time",
                "type": "date",
                "operator": "last_n_hours",
            },
            {
                "value": [rtr1_systemip],
                "field": "local_system_ip",
                "type": "string",
                "operator": "in",
            },
            {
                "value": [rtr2_systemip],
                "field": "remote_system_ip",
                "type": "string",
                "operator": "in",
            },
        ],
    },
    "aggregation": {
        "field": [{"property": "name", "sequence": 1, "size": 6000}],
        "metrics": [
            {"property": "loss_percentage", "type": "avg"},
            {"property": "vqoe_score", "type": "avg"},
            {"property": "latency", "type": "avg"},
            {"property": "jitter", "type": "avg"},
        ],
    },
}
```

Sample response:

```bash
❯ python app.py approute-stats
Enter Router-1 System IP address : 10.0.0.1
Enter Router-2 System IP address : 10.0.0.2

Average App route statistics between 10.0.0.1 and 10.0.0.2 for last 1 hour

╒═════════════════════════════╤══════════════╤═══════════╤═══════════════════╤══════════╕
│ Tunnel name                 │   vQoE score │   Latency │   Loss percentage │   Jitter │
╞═════════════════════════════╪══════════════╪═══════════╪═══════════════════╪══════════╡
│ 10.0.0.1:mpls-10.0.0.2:mpls │         9.96 │         1 │             0.029 │    0.039 │
╘═════════════════════════════╧══════════════╧═══════════╧═══════════════════╧══════════╛

Average App route statistics between 10.0.0.2 and 10.0.0.1 for last 1 hour

╒═════════════════════════════╤══════════════╤═══════════╤═══════════════════╤══════════╕
│ Tunnel name                 │   vQoE score │   Latency │   Loss percentage │   Jitter │
╞═════════════════════════════╪══════════════╪═══════════╪═══════════════════╪══════════╡
│ 10.0.0.2:mpls-10.0.0.1:mpls │           10 │     1.305 │                 0 │        0 │
╘═════════════════════════════╧══════════════╧═══════════╧═══════════════════╧══════════╛

❯ 
```
