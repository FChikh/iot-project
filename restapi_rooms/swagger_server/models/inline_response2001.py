# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.booking import Booking  # noqa: F401,E501
from swagger_server import util


class InlineResponse2001(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, room_id: List[Booking]=None):  # noqa: E501
        """InlineResponse2001 - a model defined in Swagger

        :param room_id: The room_id of this InlineResponse2001.  # noqa: E501
        :type room_id: List[Booking]
        """
        self.swagger_types = {
            'room_id': List[Booking]
        }

        self.attribute_map = {
            'room_id': 'room_id'
        }
        self._room_id = room_id

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2001':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_1 of this InlineResponse2001.  # noqa: E501
        :rtype: InlineResponse2001
        """
        return util.deserialize_model(dikt, cls)

    @property
    def room_id(self) -> List[Booking]:
        """Gets the room_id of this InlineResponse2001.


        :return: The room_id of this InlineResponse2001.
        :rtype: List[Booking]
        """
        return self._room_id

    @room_id.setter
    def room_id(self, room_id: List[Booking]):
        """Sets the room_id of this InlineResponse2001.


        :param room_id: The room_id of this InlineResponse2001.
        :type room_id: List[Booking]
        """

        self._room_id = room_id
