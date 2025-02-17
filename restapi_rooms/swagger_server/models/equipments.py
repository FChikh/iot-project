# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Equipments(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, capacity: float=None, projector: bool=None, pc: bool=None, computer_class: bool=None, microphone: bool=None, smartboard: bool=None, blackboard: bool=None, whiteboard: bool=None):  # noqa: E501
        """Equipments - a model defined in Swagger

        :param capacity: The capacity of this Equipments.  # noqa: E501
        :type capacity: float
        :param projector: The projector of this Equipments.  # noqa: E501
        :type projector: bool
        :param pc: The pc of this Equipments.  # noqa: E501
        :type pc: bool
        :param computer_class: The computer_class of this Equipments.  # noqa: E501
        :type computer_class: bool
        :param microphone: The microphone of this Equipments.  # noqa: E501
        :type microphone: bool
        :param smartboard: The smartboard of this Equipments.  # noqa: E501
        :type smartboard: bool
        :param blackboard: The blackboard of this Equipments.  # noqa: E501
        :type blackboard: bool
        :param whiteboard: The whiteboard of this Equipments.  # noqa: E501
        :type whiteboard: bool
        """
        self.swagger_types = {
            'capacity': float,
            'projector': bool,
            'pc': bool,
            'computer_class': bool,
            'microphone': bool,
            'smartboard': bool,
            'blackboard': bool,
            'whiteboard': bool
        }

        self.attribute_map = {
            'capacity': 'capacity',
            'projector': 'projector',
            'pc': 'pc',
            'computer_class': 'computer-class',
            'microphone': 'microphone',
            'smartboard': 'smartboard',
            'blackboard': 'blackboard',
            'whiteboard': 'whiteboard'
        }
        self._capacity = capacity
        self._projector = projector
        self._pc = pc
        self._computer_class = computer_class
        self._microphone = microphone
        self._smartboard = smartboard
        self._blackboard = blackboard
        self._whiteboard = whiteboard

    @classmethod
    def from_dict(cls, dikt) -> 'Equipments':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Equipments of this Equipments.  # noqa: E501
        :rtype: Equipments
        """
        return util.deserialize_model(dikt, cls)

    @property
    def capacity(self) -> float:
        """Gets the capacity of this Equipments.

        Number of seats  # noqa: E501

        :return: The capacity of this Equipments.
        :rtype: float
        """
        return self._capacity

    @capacity.setter
    def capacity(self, capacity: float):
        """Sets the capacity of this Equipments.

        Number of seats  # noqa: E501

        :param capacity: The capacity of this Equipments.
        :type capacity: float
        """

        self._capacity = capacity

    @property
    def projector(self) -> bool:
        """Gets the projector of this Equipments.

        Status if there is a projector in the room  # noqa: E501

        :return: The projector of this Equipments.
        :rtype: bool
        """
        return self._projector

    @projector.setter
    def projector(self, projector: bool):
        """Sets the projector of this Equipments.

        Status if there is a projector in the room  # noqa: E501

        :param projector: The projector of this Equipments.
        :type projector: bool
        """

        self._projector = projector

    @property
    def pc(self) -> bool:
        """Gets the pc of this Equipments.

        If the room contains a computer for the teacher  # noqa: E501

        :return: The pc of this Equipments.
        :rtype: bool
        """
        return self._pc

    @pc.setter
    def pc(self, pc: bool):
        """Sets the pc of this Equipments.

        If the room contains a computer for the teacher  # noqa: E501

        :param pc: The pc of this Equipments.
        :type pc: bool
        """

        self._pc = pc

    @property
    def computer_class(self) -> bool:
        """Gets the computer_class of this Equipments.

        If the room is a computer class. If this is the case the capacity equals to the amount of computers  # noqa: E501

        :return: The computer_class of this Equipments.
        :rtype: bool
        """
        return self._computer_class

    @computer_class.setter
    def computer_class(self, computer_class: bool):
        """Sets the computer_class of this Equipments.

        If the room is a computer class. If this is the case the capacity equals to the amount of computers  # noqa: E501

        :param computer_class: The computer_class of this Equipments.
        :type computer_class: bool
        """

        self._computer_class = computer_class

    @property
    def microphone(self) -> bool:
        """Gets the microphone of this Equipments.

        If the room has a microphone  # noqa: E501

        :return: The microphone of this Equipments.
        :rtype: bool
        """
        return self._microphone

    @microphone.setter
    def microphone(self, microphone: bool):
        """Sets the microphone of this Equipments.

        If the room has a microphone  # noqa: E501

        :param microphone: The microphone of this Equipments.
        :type microphone: bool
        """

        self._microphone = microphone

    @property
    def smartboard(self) -> bool:
        """Gets the smartboard of this Equipments.

        If the room contains a smartboard with capabilities of doing a remote/virtual class  # noqa: E501

        :return: The smartboard of this Equipments.
        :rtype: bool
        """
        return self._smartboard

    @smartboard.setter
    def smartboard(self, smartboard: bool):
        """Sets the smartboard of this Equipments.

        If the room contains a smartboard with capabilities of doing a remote/virtual class  # noqa: E501

        :param smartboard: The smartboard of this Equipments.
        :type smartboard: bool
        """

        self._smartboard = smartboard

    @property
    def blackboard(self) -> bool:
        """Gets the blackboard of this Equipments.

        If the room has a blackboard  # noqa: E501

        :return: The blackboard of this Equipments.
        :rtype: bool
        """
        return self._blackboard

    @blackboard.setter
    def blackboard(self, blackboard: bool):
        """Sets the blackboard of this Equipments.

        If the room has a blackboard  # noqa: E501

        :param blackboard: The blackboard of this Equipments.
        :type blackboard: bool
        """

        self._blackboard = blackboard

    @property
    def whiteboard(self) -> bool:
        """Gets the whiteboard of this Equipments.

        If the room has a whiteboard  # noqa: E501

        :return: The whiteboard of this Equipments.
        :rtype: bool
        """
        return self._whiteboard

    @whiteboard.setter
    def whiteboard(self, whiteboard: bool):
        """Sets the whiteboard of this Equipments.

        If the room has a whiteboard  # noqa: E501

        :param whiteboard: The whiteboard of this Equipments.
        :type whiteboard: bool
        """

        self._whiteboard = whiteboard
