import connexion
import six

from swagger_server.models.book_room_id_body import BookRoomIdBody  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response400 import InlineResponse400  # noqa: E501
from swagger_server.models.inline_response409 import InlineResponse409  # noqa: E501
from swagger_server.models.inline_response500 import InlineResponse500  # noqa: E501
from swagger_server.models.room_air_quality10 import RoomAirQuality10  # noqa: E501
from swagger_server.models.room_air_quality25 import RoomAirQuality25  # noqa: E501
from swagger_server.models.room_co2 import RoomCo2  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_equipment import RoomEquipment  # noqa: E501
from swagger_server.models.room_humidity import RoomHumidity  # noqa: E501
from swagger_server.models.room_light import RoomLight  # noqa: E501
from swagger_server.models.room_noise import RoomNoise  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server.models.room_voc import RoomVoc  # noqa: E501
from swagger_server import util

from .get_funcs.get_sensor_data import get_spec_room_spec_sensor, get_all_room_spec_sensor
from .get_funcs.get_sensor_data import get_spec_room_all_sensor, get_all_room_all_sensor
from .get_funcs.get_booking import get_spec_room_bookings, get_all_room_bookings
from .get_funcs.get_equipment import get_equipment_by_room, get_equipment_all_rooms
from .post_funcs.post_book_room import post_book_room_id


def book_room_id_post(body, room_id):  # noqa: E501
    """Book a specific room

    Book a 30-minute time slot for a specific room. # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: InlineResponse200
    """

    """Book a specific room"""
    print("Starting booking process...")  # Debug log
    print(f"Received body: {body}")      # Debug log
    print(f"Room ID: {room_id}")         # Debug log

    if connexion.request.is_json:
            body = BookRoomIdBody.from_dict(connexion.request.get_json())
            print(f"Parsed body: {body}") # Debug log

    return post_book_room_id(body, room_id)



def equipment_room_id_get(room_id):  # noqa: E501
    """Get the available equipment for a specific room

    Fetches information/data about the equipment of a specific room, such as capacity, if it has a projector etc. # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomEquipment
    """
    return get_equipment_by_room(room_id)


def equipment_rooms_get():  # noqa: E501
    """Get information about the equipment in each room

    Retrieve the equipment status of each room, such as amount of seats, if there is a projector, etc. # noqa: E501


    :rtype: List[RoomEquipment]
    """
    return get_equipment_all_rooms()


def room_id_aq_pm10_get(room_id):  # noqa: E501
    """Get air quality data for a specific room (i.e. pm10)

    Fetches the air quality measurements, including particulate matter (μg/m³) for smaller particles (i.e. pm10) of a single room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality10
    """
    return get_spec_room_spec_sensor("pm10", room_id, 14)


def room_id_aq_pm2_5_get(room_id):  # noqa: E501
    """Get air quality data for a specific room (i.e. pm2.5)

    Fetches the air quality measurements, including particulate matter (μg/m³) for smaller particles (i.e. pm2.5) of a single room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality25
    """
    return get_spec_room_spec_sensor("pm2_5", room_id, 14)


def room_id_bookings_get(room_id, start_date=None, days=None):  # noqa: E501
    """Get bookings for specific room

    Retrieve booking timestamps for a specific room within a specified time interval # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str
    :param start_date: Start date for the booking period (YYYY-MM-DD)
    :type start_date: str
    :param days: Number of days to retrieve bookings for
    :type days: int

    :rtype: InlineResponse2001
    """
    return get_spec_room_bookings(room_id, start_date, days)


def room_id_co2_get(room_id):  # noqa: E501
    """Get co2 data for a specific room

    Retrieve co2 measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomCo2
    """
    return get_spec_room_spec_sensor("co2", room_id, 14)


def room_id_humidity_get(room_id):  # noqa: E501
    """Retrieve humidity data for a specific room.

    Fetches relative humidity measurements in percentage (%) to assess moisture level in a specific room. # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomHumidity
    """
    return get_spec_room_spec_sensor("humidity", room_id, 14)


def room_id_light_get(room_id):  # noqa: E501
    """Get light data for a specific room

    Retrieve light measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomLight
    """
    return get_spec_room_spec_sensor("light", room_id, 14)


def room_id_noise_get(room_id):  # noqa: E501
    """Get noise/sound data for a specific room

    Retrieve noise/sound measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomNoise
    """
    return get_spec_room_spec_sensor("noise", room_id, 14)


def room_id_temperature_get(room_id):  # noqa: E501
    """Retrieve temperature data for a specific room

    Provides temperature measurements in degrees Celsius (°C) to monitor indoor climate conditions for a specific room. # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomTemperature
    """
    return get_spec_room_spec_sensor("temperature", room_id, 14)


def room_id_voc_get(room_id):  # noqa: E501
    """Get voc data for a specific room

    Retrieve voc measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomVoc
    """
    return get_spec_room_spec_sensor("voc", room_id, 14)


def rooms_aq_pm10_get():  # noqa: E501
    """Retrieve air quality data (pm10)

    Fetches the air quality measurement, including particulate matter (μg/m³) for smaller particles(i.e. pm10) for all rooms # noqa: E501


    :rtype: List[RoomAirQuality10]
    """
    return get_all_room_spec_sensor("pm10", 14)


def rooms_aq_pm2_5_get():  # noqa: E501
    """Retrieve air quality data (pm2.5)

    Fetches the air quality measurement, including particulate matter (μg/m³) for smaller particles(i.e. pm2.5) for all rooms # noqa: E501


    :rtype: List[RoomAirQuality25]
    """
    return get_all_room_spec_sensor("pm2_5", 14)


def rooms_bookings_get(start_date=None, days=None):  # noqa: E501
    """Get bookings for all rooms

    Retrieve booking timestamps for all rooms within a specified time interval # noqa: E501

    :param start_date: Start date for the booking period (YYYY-MM-DD)
    :type start_date: str
    :param days: Number of days to retrieve bookings for
    :type days: int

    :rtype: Dict[str, List[Booking]]
    """
    return get_all_room_bookings(start_date, days)


def rooms_co2_get():  # noqa: E501
    """Retrieve CO2 level data for all rooms.

    Provides the CO2 concentration measurements in parts per million (ppm) for monitoring air quality in various rooms # noqa: E501


    :rtype: List[RoomCo2]
    """
    return get_all_room_spec_sensor("co2", 14)


def rooms_humidity_get():  # noqa: E501
    """Retrieve humidity data for all rooms

    Fetches relative humidity measurements in percentage (%) to assess moisture levels in different rooms # noqa: E501


    :rtype: List[RoomHumidity]
    """
    return get_all_room_spec_sensor("humidity", 14)


def rooms_light_get():  # noqa: E501
    """Retrieve light intensity data for all rooms

    Fetches the light intensity measurements in lux (lx) for all rooms to assess illumination levels # noqa: E501


    :rtype: List[RoomLight]
    """
    return get_all_room_spec_sensor("light", 14)


def rooms_noise_get():  # noqa: E501
    """Retrieve sound level data for all rooms.

    Provides sound level measurements in decibels (dB) to monitor noise levels in different rooms. # noqa: E501


    :rtype: List[RoomNoise]
    """
    return get_all_room_spec_sensor("noise", 14)


def rooms_temperature_get():  # noqa: E501
    """Retrieve temperature data for all rooms.

    Provides temperature measurements in degrees Celsius (°C) to monitor indoor climate conditions # noqa: E501


    :rtype: List[RoomTemperature]
    """
    return get_all_room_spec_sensor("temperature", 14)


def rooms_voc_get():  # noqa: E501
    """Retrieve VOC concentration data for all rooms.

    Fetches the volatile organic compounds (VOC) concentration in micrograms per cubic meter (μg/m³) to evaluate indoor air pollution. # noqa: E501


    :rtype: List[RoomVoc]
    """
    return get_all_room_spec_sensor("voc", 14)


def sensor_room_id_get(room_id):  # noqa: E501
    """Get sensor data for a specific room

    Retrieve all sensor data for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomData
    """
    return get_spec_room_all_sensor(room_id, 14)


def sensor_rooms_get():  # noqa: E501
    """Get sensor data for all rooms

    Retrieve all sensor data for all rooms # noqa: E501


    :rtype: List[RoomData]
    """
    return get_all_room_all_sensor(14)
