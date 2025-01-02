import connexion
import six
from flask import abort, jsonify
from dateutil import parser
import os

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.room_air_quality import RoomAirQuality  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server import util

from .authenticate import get_calendar_service, get_influx_client
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi






def room_room_id_air_quality_get(room_id):  # noqa: E501
    """Get air quality data for a specific room

    Retrieve air quality measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality
    """

     # Configuration

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
                    'co2_level': record.get_value()
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



def room_room_id_bookings_get(room_id, start_date=None, days=None):  # noqa: E501
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
        calendar_id = "7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"
        
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
            # start_time = datetime.fromisoformat(temp1)
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




def room_room_id_get(room_id):  # noqa: E501
    """Get sensor data for a specific room

    Retrieve all sensor data for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomData
    """
    return 'do some magic!'


def room_room_id_temperature_get(room_id):  # noqa: E501
    """Get temperature data for a specific room

    Retrieve temperature measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomTemperature
    """
         # Configuration

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
        temp_data = []
        for table in result:
            for record in table.records:
                # Assuming the field is "co2_level"
                temp_data.append({
                    'timestamp': record.get_time().isoformat(),
                    'temperature': record.get_value()
                })

        if not temp_data:
            return jsonify({"error": "No air quality data found for the given room"}), 404

        # Return the data in the desired format
        return jsonify({
            "room": room_id,
            "temperature": temp_data
        })

    finally:
        # Close the client
        client.close()




def rooms_air_quality_get():  # noqa: E501
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

    :rtype: Dict[str, List[datetime]]
    """

    try:
        print(start_date)
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        print(start_date)
        # creds = authenticate()
        end_date = start_date + timedelta(days=days)
        print(end_date)
        
        # service = build("calendar", "v3", credentials=creds)
        service = get_calendar_service()
        calendar_id = "7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"
        
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
            # start_time = datetime.fromisoformat(temp1)
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


    # start_date = util.deserialize_date(start_date)


def rooms_get():  # noqa: E501
    """Get sensor data for all rooms

    Retrieve all sensor data (temperature and air quality) for all rooms # noqa: E501


    :rtype: List[RoomData]
    """
    return 'do some magic!'


def rooms_temperature_get():  # noqa: E501
    """Get temperature data for all rooms

    Retrieve temperature measurements for all rooms # noqa: E501


    :rtype: List[RoomTemperature]
    """
    return 'do some magic!'
