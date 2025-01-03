import connexion, six, os
from flask import abort, jsonify
from dateutil import parser
from datetime import datetime, timedelta

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.room_air_quality import RoomAirQuality  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_humidity import RoomHumidity  # noqa: E501
from swagger_server.models.room_light import RoomLight  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server import util

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi

from .authenticate import get_calendar_service, get_influx_client



def room_id_airquality_get(room_id):  # noqa: E501
    """Get air quality data for a specific room

    Retrieve air quality measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality
    """

    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')


    try:
        # Get the Query API
        query_api: QueryApi = client.query_api()

        # Flux query to retrieve data for the specific room
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -20d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "co2")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # Execute the query
        result = query_api.query(org=org, query=flux_query)

        
        # Prepare the air quality data in the desired format
        air_quality_data = []
        for table in result:
            for record in table.records:
                # Assuming the field is "co2_level"
                air_quality_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })

        if not air_quality_data:
            return jsonify({"error": "No air quality data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            "air_quality": air_quality_data
        })

    finally:
        # Close the client
        client.close()




def room_id_bookings_get(room_id, start_date=None, days=None):  # noqa: E501
    """Get bookings for specific room

    Retrieve booking timestamps for a specific room within a specified time interval # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str
    :param start_date: Start date for the booking period (YYYY-MM-DD)
    :type start_date: str
    :param days: Number of days to retrieve bookings for
    :type days: int

    :rtype: InlineResponse200
    """
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=days)
        
        service = get_calendar_service()
        calendar_id = os.getenv('GOOGLE_CAL_ID')
        
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z", 
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        bookings = {}
        for event in events:
            room = event["location"]
            temp1 = event["start"].get("dateTime")
            start_time = parser.parse(temp1).strftime('%Y-%m-%d %H:%M:%S')

            
            if room == room_id:
                if room not in bookings:
                    bookings[room] = []
                bookings[room].append(start_time)

        return bookings

    except HttpError as error:
        print(error)
        abort(500, f"Google Calendar API error: {str(error)}")
    except Exception as error:
        print(error)
        abort(500, f"Internal server error: {str(error)}")




def room_id_humidity_get(room_id):  # noqa: E501
    """Get humidity data for a specific room

    Retrieve humidity measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomHumidity
    """

    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')


    try:
        # Get the Query API
        query_api: QueryApi = client.query_api()

        # Flux query to retrieve data for the specific room
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -20d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "humidity")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # Execute the query
        result = query_api.query(org=org, query=flux_query)

        
        # Prepare the air quality data in the desired format
        humidity_data = []
        for table in result:
            for record in table.records:
                # Assuming the field is "co2_level"
                humidity_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })

        if not humidity_data:
            return jsonify({"error": "No air quality data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            "humidity": humidity_data
        })

    finally:
        # Close the client
        client.close()




def room_id_light_get(room_id):  # noqa: E501
    """Get light data for a specific room

    Retrieve light measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomLight
    """
    
    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')


    try:
        # Get the Query API
        query_api: QueryApi = client.query_api()

        # Flux query to retrieve data for the specific room
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -20d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "light")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # Execute the query
        result = query_api.query(org=org, query=flux_query)

        
        # Prepare the air quality data in the desired format
        light_data = []
        for table in result:
            for record in table.records:
                # Assuming the field is "co2_level"
                light_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })

        if not light_data:
            return jsonify({"error": "No air quality data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            "light": light_data
        })

    finally:
        # Close the client
        client.close()




def room_id_temperature_get(room_id):  # noqa: E501
    """Get temperature data for a specific room

    Retrieve temperature measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomTemperature
    """
    client = get_influx_client()
    org = os.getenv('INFLUXDB_ORG', 'myorg')
    bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')


    try:
        # Get the Query API
        query_api: QueryApi = client.query_api()

        # Flux query to retrieve data for the specific room
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: -20d)
          |> filter(fn: (r) => r["_measurement"] == "room_data")
          |> filter(fn: (r) => r["_field"] == "temperature")
          |> filter(fn: (r) => r["room_id"] == "{room_id}")
          |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''

        # Execute the query
        result = query_api.query(org=org, query=flux_query)

        
        # Prepare the air quality data in the desired format
        temperature_data = []
        for table in result:
            for record in table.records:
                # Assuming the field is "co2_level"
                temperature_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'value': record.get_value()
                })

        if not temperature_data:
            return jsonify({"error": "No air quality data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            "temperature": temperature_data
        })

    finally:
        # Close the client
        client.close()



def rooms_airquality_get():  # noqa: E501
    """Get air quality data for all rooms

    Retrieve air quality measurements for all rooms # noqa: E501


    :rtype: List[RoomAirQuality]
    """
    return 'do some magic!'


def rooms_bookings_get(start_date=None, days=None):  # noqa: E501
    """Get bookings for all rooms

    Retrieve booking timestamps for all rooms within a specified time interval # noqa: E501

    :param start_date: Start date for the booking period (YYYY-MM-DD)
    :type start_date: str
    :param days: Number of days to retrieve bookings for
    :type days: int

    :rtype: Dict[str, List[Booking]]
    """

    try:
        print(start_date)
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        print(start_date)
        # creds = authenticate()
        end_date = start_date + timedelta(days=days)
        print(end_date)
        
        service = get_calendar_service()
        calendar_id = os.getenv('GOOGLE_CAL_ID')
        
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z", 
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        bookings = {}
        for event in events:
            room = event["location"]
            temp1 = event["start"].get("dateTime")
            start_time = parser.parse(temp1).strftime('%Y-%m-%d %H:%M:%S')
            print(start_time)

            
            if room not in bookings:
                bookings[room] = []
            bookings[room].append(start_time)

        return bookings

    except HttpError as error:
        print(error)
        abort(500, f"Google Calendar API error: {str(error)}")
    except Exception as error:
        print(error)
        abort(500, f"Internal server error: {str(error)}")



def rooms_humidity_get():  # noqa: E501
    """Get humidity data for all rooms

    Retrieve humidity measurements for all rooms # noqa: E501


    :rtype: List[RoomHumidity]
    """
    return 'do some magic!'


def rooms_light_get():  # noqa: E501
    """Get light data for all rooms

    Retrieve light measurements for all rooms # noqa: E501


    :rtype: List[RoomLight]
    """
    return 'do some magic!'


def rooms_temperature_get():  # noqa: E501
    """Get temperature data for all rooms

    Retrieve temperature measurements for all rooms # noqa: E501


    :rtype: List[RoomTemperature]
    """
    return 'do some magic!'


def sensor_room_id_get(room_id):  # noqa: E501
    """Get sensor data for a specific room

    Retrieve all sensor data for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomData
    """
    return 'do some magic!'


def sensor_rooms_get():  # noqa: E501
    """Get sensor data for all rooms

    Retrieve all sensor data (temperature and air quality) for all rooms # noqa: E501


    :rtype: List[RoomData]
    """
    return 'do some magic!'
