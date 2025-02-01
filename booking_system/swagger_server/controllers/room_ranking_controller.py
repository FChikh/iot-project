import connexion
import six

from swagger_server.models.ranking_request import RankingRequest  # noqa: E501
from swagger_server.models.room import Room  # noqa: E501
from swagger_server import util


def rank_rooms(body):  # noqa: E501
    """Get ranked list of available rooms

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: List[Room]
    """
    if connexion.request.is_json:
        body = RankingRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
