from ..authenticate import get_influx_client

import os
from flask import abort, jsonify

from influxdb_client.client.query_api import QueryApi



def get_spec_room_spec_sensor(sensor_type, room_id, days):

    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')

    sensor_map_influx = {"pm2_5":"air_quality_pm2_5",
                  "pm10":"air_quality_pm10",
                  "co2":"co2",
                  "voc":"voc",
                  "noise":"sound",
                  "temperature":"temperature",
                  "light":"light",
                  "humidity":"humidity"
    }

    
    try:
        # Get the Query API
        query_api: QueryApi = client.query_api()

        # Flux query to retrieve data for the specific room
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "{sensor_map_influx[sensor_type]}")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # Execute the query
        result = query_api.query(org=org, query=flux_query)

        
        # Prepare the air quality data in the desired format
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })

        if not data:
            return jsonify({"error": f"No {sensor_type} data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            sensor_type: data
        })

    finally:
        # Close the client
        client.close()






def get_all_room_spec_sensor(sensor_type, days):

    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')

    sensor_map_influx = {"pm2_5":"air_quality_pm2_5",
                  "pm10":"air_quality_pm10",
                  "co2":"co2",
                  "voc":"voc",
                  "noise":"sound",
                  "temperature":"temperature",
                  "light":"light",
                  "humidity":"humidity"
    }


    try:
        query_api: QueryApi = client.query_api()
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "{sensor_map_influx[sensor_type]}")
          |> group(columns: ["room_id"])
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        
        result = query_api.query(org=org, query=flux_query)
        
        # Dictionary to store data for each room
        rooms_data = {}
        
        # Process the results
        for table in result:
            for record in table.records:
                room_id = record.values.get("room_id")
                
                # Initialize room data if not exists
                if room_id not in rooms_data:
                    rooms_data[room_id] = {
                        "room": room_id,
                        sensor_type: []
                    }
                
                # Add light measurement
                rooms_data[room_id][sensor_type].append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })
        
        if not rooms_data:
            return jsonify({"error": f"No {sensor_type} data found for any rooms"}), 404
            
        # Convert dictionary to list for response
        response_data = list(rooms_data.values())
        
        return jsonify(response_data)
        
    finally:
        client.close()




def get_spec_room_all_sensor(room_id, days):  # noqa: E501
    """Get sensor data for a specific room

    Retrieve all sensor data for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomData
    """

    
    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')
    
    try:
        query_api: QueryApi = client.query_api()
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> group(columns: ["room_id", "_field"])
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # maps from influx terms to restapi terms
        sensor_map = {"air_quality_pm2_5": "pm2_5",
                      "air_quality_pm10": "pm10",
                      "co2":"co2",
                      "voc":"voc",
                      "sound":"noise",
                      "temperature":"temperature",
                      "light":"light",
                      "humidity":"humidity"
        }
        
        result = query_api.query(org=org, query=flux_query)
        
        # Dictionary to store data for each room
        rooms_data = {}
        
        # Process the results
        for table in result:
            for record in table.records:
                roomid = record.values.get("room_id")
                sensor_type = record.get_field()
                
                # Initialize room data if not exists
                if room_id not in rooms_data:
                    rooms_data[roomid] = {
                        "room": roomid,
                        "pm2_5": [],
                        "pm10": [],
                        "voc": [],
                        "noise": [],
                        "temperature": [],
                        "airquality": [],
                        "light": [],
                        "humidity": []
                    }
                
                
                
                mapped_sensor = sensor_map[sensor_type]
                if mapped_sensor:
                    rooms_data[room_id][mapped_sensor].append({
                        'timestamp': record.get_time().isoformat(),
                        'value': record.get_value()
                    })
        
        if not rooms_data:
            return jsonify({"error": f"No sensor data found for room {room_id}"}), 404
            
        # Convert dictionary to list for response
        response_data = list(rooms_data.values())
        
        return jsonify(response_data)
        
    finally:
        client.close()



def get_all_room_all_sensor(days):  # noqa: E501
    """Get sensor data for all rooms

    Retrieve all sensor data (temperature, air quality, etc.) for all rooms # noqa: E501


    :rtype: List[RoomData]
    """

    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')
    
    try:
        query_api: QueryApi = client.query_api()
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> group(columns: ["room_id", "_field"])
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        sensor_map = {"air_quality_pm2_5": "pm2_5",
                      "air_quality_pm10": "pm10",
                      "co2":"co2",
                      "voc":"voc",
                      "sound":"noise",
                      "temperature":"temperature",
                      "light":"light",
                      "humidity":"humidity"
        }

        result = query_api.query(org=org, query=flux_query)
        
        # Dictionary to store data for each room
        rooms_data = {}
        
        # Process the results
        for table in result:
            for record in table.records:
                room_id = record.values.get("room_id")
                sensor_type = record.get_field()
                
                # Initialize room data if not exists
                if room_id not in rooms_data:
                    rooms_data[room_id] = {
                        "room": room_id,
                        "pm2_5": [],
                        "pm10": [],
                        "voc": [],
                        "noise": [],
                        "temperature": [],
                        "airquality": [],
                        "light": [],
                        "humidity": []
                    }
                
                
                mapped_sensor = sensor_map.get(sensor_type)
                if mapped_sensor:
                    rooms_data[room_id][mapped_sensor].append({
                        'timestamp': record.get_time().isoformat(),
                        'value': record.get_value()
                    })
        
        if not rooms_data:
            return jsonify({"error": "No sensor data found for any rooms"}), 404
            
        # Convert dictionary to list for response
        response_data = list(rooms_data.values())
        
        return jsonify(response_data)
        
    finally:
        client.close()




