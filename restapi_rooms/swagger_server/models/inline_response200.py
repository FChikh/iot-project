# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class InlineResponse200(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, status: str=None, message: str=None):  # noqa: E501
        """InlineResponse200 - a model defined in Swagger

        :param status: The status of this InlineResponse200.  # noqa: E501
        :type status: str
        :param message: The message of this InlineResponse200.  # noqa: E501
        :type message: str
        """
        self.swagger_types = {
            'status': str,
            'message': str
        }

        self.attribute_map = {
            'status': 'status',
            'message': 'message'
        }
        self._status = status
        self._message = message

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse200':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200 of this InlineResponse200.  # noqa: E501
        :rtype: InlineResponse200
        """
        return util.deserialize_model(dikt, cls)

    @property
    def status(self) -> str:
        """Gets the status of this InlineResponse200.


        :return: The status of this InlineResponse200.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """Sets the status of this InlineResponse200.


        :param status: The status of this InlineResponse200.
        :type status: str
        """

        self._status = status

    @property
    def message(self) -> str:
        """Gets the message of this InlineResponse200.


        :return: The message of this InlineResponse200.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this InlineResponse200.


        :param message: The message of this InlineResponse200.
        :type message: str
        """

        self._message = message
