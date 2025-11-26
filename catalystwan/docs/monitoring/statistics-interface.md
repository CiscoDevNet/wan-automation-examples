# Interface Statistics Simple Query API

Collect interface statistics.

## API URL:

`https://{{manager}}:{{port}}/dataservice/statistics/interface`

## Example 1

Simple API call to collect all interface statistics for 30 mins interval.

### Method

POST

### Query

```json
{
  "query": {
    "condition": "AND",
    "rules": [
        {
            "value": ["2025-11-26T10:00:00 UTC", "2025-11-26T10:30:00 UTC"],
            "field": "entry_time",
            "type": "date",
            "operator": "between"
        }
    ]
  }
}
```

### Sample Response

See [Example 1 response payload](json/interface-stats-example1.json)

## Example 2

collect interface statistics for 30 mins interval, filter on device 10.0.0.1.

### Method

POST

### Query:

```json
{
  "query": {
    "condition": "AND",
    "rules": [
        {
            "value": ["2025-11-01T10:00:00 UTC", "2025-11-30T10:30:00 UTC"],
            "field": "entry_time",
            "type": "date",
            "operator": "between"
        },
        {
            "value": ["10.0.0.1"],
            "field": "vdevice_name",
            "type": "string",
            "operator": "in"
            
        }
    ]
  }
}
```

See [Example 2 response payload](json/interface-stats-example2.json)
