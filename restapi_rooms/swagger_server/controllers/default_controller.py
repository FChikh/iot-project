import connexion
import six

from swagger_server.models.book_room_id_body import BookRoomIdBody  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response400 import InlineResponse400  # noqa: E501
from swagger_server.models.inline_response409 import InlineResponse409  # noqa: E501
from swagger_server.models.inline_response500 import InlineResponse500  # noqa: E501
from swagger_server.models.room_air_quality import RoomAirQuality  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_humidity import RoomHumidity  # noqa: E501
from swagger_server.models.room_light import RoomLight  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server import util

from .get_funcs.get_sensor_data import get_spec_room_spec_sensor, get_all_room_spec_sensor
from .get_funcs.get_sensor_data import get_spec_room_all_sensor, get_all_room_all_sensor
from .get_funcs.get_booking import get_spec_room_bookings, get_all_room_bookings


def book_room_id_post(body, room_id):  # noqa: E501
    """Book a specific room

    Book a 30-minute time slot for a specific room. # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: InlineResponse200
    """
    if connexion.request.is_json:
        body = BookRoomIdBody.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def room_id_airquality_get(room_id):  # noqa: E501
    """Get air quality data for a specific room

    Retrieve air quality measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomAirQuality
    """
    return get_spec_room_spec_sensor("airquality", room_id, 14)


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


def room_id_humidity_get(room_id):  # noqa: E501
    """Get humidity data for a specific room

    Retrieve humidity measurements for a specific room # noqa: E501

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


def room_id_temperature_get(room_id):  # noqa: E501
    """Get temperature data for a specific room

    Retrieve temperature measurements for a specific room # noqa: E501

    :param room_id: Unique identifier for the room
    :type room_id: str

    :rtype: RoomTemperature
    """
    return get_spec_room_spec_sensor("temperature", room_id, 14)


def rooms_airquality_get():  # noqa: E501
    """Get air quality data for all rooms

    Retrieve air quality measurements for all rooms # noqa: E501


    :rtype: List[RoomAirQuality]
    """
    return get_all_room_spec_sensor("airquality", 14)


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


def rooms_humidity_get():  # noqa: E501
    """Get humidity data for all rooms

    Retrieve humidity measurements for all rooms # noqa: E501


    :rtype: List[RoomHumidity]
    """
    return get_all_room_spec_sensor("humidity", 14)


def rooms_light_get():  # noqa: E501
    """Get light data for all rooms

    Retrieve light measurements for all rooms # noqa: E501


    :rtype: List[RoomLight]
    """
    return get_all_room_spec_sensor("light", 14)


def rooms_temperature_get():  # noqa: E501
    """Get temperature data for all rooms

    Retrieve temperature measurements for all rooms # noqa: E501


    :rtype: List[RoomTemperature]
    """
    return get_all_room_spec_sensor("temperature", 14)


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

    Retrieve all sensor data (temperature and air quality) for all rooms # noqa: E501


    :rtype: List[RoomData]
    """
    return get_all_room_all_sensor(14)
