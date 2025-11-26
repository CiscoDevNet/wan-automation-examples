# Monitoring APIs

3 main Monitoring API Categories:

- Device real-time monitoring: `/dataservice/device` endpoints
- Statistics APIs: `/dataservice/statistics` endpoints
- Statistics Bulk APIs: `/dataservice/data` endpoints

## From Device - Realtime Monitoring

`/dataservice/device` endpoints

Realtime monitoring APIs query device state and information in real time. Real-time monitoring API are very CPU intensive and should be used for troubleshooting only. These should not be used continuously for active monitoring of the devices.

Examples:

- Application-Aware Routing - API calls for real-time monitoring of application-aware routing
    - SLA Class - Display information about the SLA classes operating on the router
    - Statistics - Display statistics about data traffic characteristics for all operational data plane tunnel
- ARP - API calls for real-time monitoring of ARP information.
- BFD - API calls for real-time monitoring of BFD information
- etc

## From Statistics DB - APIs

`/dataservice/statistics` endpoints

The SD-WAN Manager NMS statistics database collects statistics from all WAN Edge routers periodically, starting from when they joined the overlay network. 

The SD-WAN Manager API query language allows you to build queries that retrieve selected statistics from the SD-WAN Manager NMS statistics database

Simple Query

- In a simple query, you specify the name or names of the fields whose values you want to retrieve, the time period over which to retrieve the value, and the order in which to sort the retrieved data.
- For example, you can retrieve statistics for an IP address for the last 6 hours, and you can sort them in descending order by hostname

Aggregated Query

- vManage aggregate queries retrieve aggregated data from the vManage statistics database.
- You can sum, count, and average data in retrieved records, display the minimum and maximum values in the retrieved records, and display a specific record
- In addition, you can group and bucketize data.
- In an aggregation query, you define the number of records to retrieve, the query conditions and rules, and the operation to aggregate the retrieved data in the output.

Examples:

- Example 1: [Interface statistics Simple Query API](monitoring/statistics-interface.md)
- Example 2: [Interface Statistics aggregated query](monitoring/statistics-interface-aggregated.md)
- Example 3: [App Route Statistics](monitoring/approute.md)

## From Statistics DB - Bulk APIs

`/dataservice/data` endpoints

Bulk API calls allow you to issue a single API request to collect information about multiple WAN Edge devices in the overlay network. The information is returned in batches.

You can perform two types of bulk API operations:

- State — These operations return status information about the devices, such as the number and state of OMP and BFD sessions.
- Statistics — These operations return statistics from the devices, such as the number of transmitted and received data packets.
