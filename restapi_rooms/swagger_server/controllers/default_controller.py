import connexion
import six
from flask import abort
from dateutil import parser

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.room_air_quality import RoomAirQuality  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server import util

from .authenticate import get_calendar_service
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




def room_room_id_air_quality_get(room_id):  # noqa: E501
    """Get air quality data for a specific room

    Retrieve air quality measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality
    """
    return 'do some magic!'


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


    return 'do some magic!'


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
    return 'do some magic!'


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
