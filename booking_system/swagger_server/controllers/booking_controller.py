import connexion
import six

from swagger_server.models.booking_confirmation import BookingConfirmation  # noqa: E501
from swagger_server.models.booking_rejection import BookingRejection  # noqa: E501
from swagger_server.models.booking_request import BookingRequest  # noqa: E501
from swagger_server import util


def book_room(body):  # noqa: E501
    """Book a specific room

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: BookingConfirmation
    """
    if connexion.request.is_json:
        body = BookingRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
