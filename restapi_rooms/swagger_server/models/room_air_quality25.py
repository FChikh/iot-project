# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.air_quality25_reading import AirQuality25Reading  # noqa: F401,E501
from swagger_server import util


class RoomAirQuality25(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, room: str=None, pm2_5: List[AirQuality25Reading]=None):  # noqa: E501
        """RoomAirQuality25 - a model defined in Swagger

        :param room: The room of this RoomAirQuality25.  # noqa: E501
        :type room: str
        :param pm2_5: The pm2_5 of this RoomAirQuality25.  # noqa: E501
        :type pm2_5: List[AirQuality25Reading]
        """
        self.swagger_types = {
            'room': str,
            'pm2_5': List[AirQuality25Reading]
        }

        self.attribute_map = {
            'room': 'room',
            'pm2_5': 'pm2_5'
        }
        self._room = room
        self._pm2_5 = pm2_5

    @classmethod
    def from_dict(cls, dikt) -> 'RoomAirQuality25':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The RoomAirQuality25 of this RoomAirQuality25.  # noqa: E501
        :rtype: RoomAirQuality25
        """
        return util.deserialize_model(dikt, cls)

    @property
    def room(self) -> str:
        """Gets the room of this RoomAirQuality25.

        Room identifier  # noqa: E501

        :return: The room of this RoomAirQuality25.
        :rtype: str
        """
        return self._room

    @room.setter
    def room(self, room: str):
        """Sets the room of this RoomAirQuality25.

        Room identifier  # noqa: E501

        :param room: The room of this RoomAirQuality25.
        :type room: str
        """

        self._room = room

    @property
    def pm2_5(self) -> List[AirQuality25Reading]:
        """Gets the pm2_5 of this RoomAirQuality25.


        :return: The pm2_5 of this RoomAirQuality25.
        :rtype: List[AirQuality25Reading]
        """
        return self._pm2_5

    @pm2_5.setter
    def pm2_5(self, pm2_5: List[AirQuality25Reading]):
        """Sets the pm2_5 of this RoomAirQuality25.


        :param pm2_5: The pm2_5 of this RoomAirQuality25.
        :type pm2_5: List[AirQuality25Reading]
        """

        self._pm2_5 = pm2_5
