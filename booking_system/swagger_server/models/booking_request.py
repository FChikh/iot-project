# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class BookingRequest(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, room_id: str=None, user_name: str=None, _date: date=None, start_time: str=None, end_time: str=None):  # noqa: E501
        """BookingRequest - a model defined in Swagger

        :param room_id: The room_id of this BookingRequest.  # noqa: E501
        :type room_id: str
        :param user_name: The user_name of this BookingRequest.  # noqa: E501
        :type user_name: str
        :param _date: The _date of this BookingRequest.  # noqa: E501
        :type _date: date
        :param start_time: The start_time of this BookingRequest.  # noqa: E501
        :type start_time: str
        :param end_time: The end_time of this BookingRequest.  # noqa: E501
        :type end_time: str
        """
        self.swagger_types = {
            'room_id': str,
            'user_name': str,
            '_date': date,
            'start_time': str,
            'end_time': str
        }

        self.attribute_map = {
            'room_id': 'room_id',
            'user_name': 'user_name',
            '_date': 'date',
            'start_time': 'start_time',
            'end_time': 'end_time'
        }
        self._room_id = room_id
        self._user_name = user_name
        self.__date = _date
        self._start_time = start_time
        self._end_time = end_time

    @classmethod
    def from_dict(cls, dikt) -> 'BookingRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BookingRequest of this BookingRequest.  # noqa: E501
        :rtype: BookingRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def room_id(self) -> str:
        """Gets the room_id of this BookingRequest.


        :return: The room_id of this BookingRequest.
        :rtype: str
        """
        return self._room_id

    @room_id.setter
    def room_id(self, room_id: str):
        """Sets the room_id of this BookingRequest.


        :param room_id: The room_id of this BookingRequest.
        :type room_id: str
        """
        if room_id is None:
            raise ValueError("Invalid value for `room_id`, must not be `None`")  # noqa: E501

        self._room_id = room_id

    @property
    def user_name(self) -> str:
        """Gets the user_name of this BookingRequest.


        :return: The user_name of this BookingRequest.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name: str):
        """Sets the user_name of this BookingRequest.


        :param user_name: The user_name of this BookingRequest.
        :type user_name: str
        """
        if user_name is None:
            raise ValueError("Invalid value for `user_name`, must not be `None`")  # noqa: E501

        self._user_name = user_name

    @property
    def _date(self) -> date:
        """Gets the _date of this BookingRequest.


        :return: The _date of this BookingRequest.
        :rtype: date
        """
        return self.__date

    @_date.setter
    def _date(self, _date: date):
        """Sets the _date of this BookingRequest.


        :param _date: The _date of this BookingRequest.
        :type _date: date
        """
        if _date is None:
            raise ValueError("Invalid value for `_date`, must not be `None`")  # noqa: E501

        self.__date = _date

    @property
    def start_time(self) -> str:
        """Gets the start_time of this BookingRequest.


        :return: The start_time of this BookingRequest.
        :rtype: str
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time: str):
        """Sets the start_time of this BookingRequest.


        :param start_time: The start_time of this BookingRequest.
        :type start_time: str
        """
        if start_time is None:
            raise ValueError("Invalid value for `start_time`, must not be `None`")  # noqa: E501

        self._start_time = start_time

    @property
    def end_time(self) -> str:
        """Gets the end_time of this BookingRequest.


        :return: The end_time of this BookingRequest.
        :rtype: str
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time: str):
        """Sets the end_time of this BookingRequest.


        :param end_time: The end_time of this BookingRequest.
        :type end_time: str
        """
        if end_time is None:
            raise ValueError("Invalid value for `end_time`, must not be `None`")  # noqa: E501

        self._end_time = end_time
