import connexion
import six

from swagger_server.models.room import Room  # noqa: E501
from swagger_server import util
from modules.decision_logic import get_ranking
from flask import jsonify


def rank_rooms(date, start_time, end_time, seating_capacity, projector, blackboard, smartboard, microphone, pc, whiteboard, air_quality_preference, noise_level, lighting):  # noqa: E501
    """Get ranked list of available rooms

     # noqa: E501

    :param date: 
    :type date: str
    :param start_time: 
    :type start_time: str
    :param end_time: 
    :type end_time: str
    :param seating_capacity: 
    :type seating_capacity: int
    :param projector: 
    :type projector: bool
    :param blackboard: 
    :type blackboard: bool
    :param smartboard: 
    :type smartboard: bool
    :param microphone: 
    :type microphone: bool
    :param pc: 
    :type pc: bool
    :param whiteboard: 
    :type whiteboard: bool
    :param air_quality_preference: 
    :type air_quality_preference: str
    :param noise_level: 
    :type noise_level: str
    :param lighting: 
    :type lighting: str

    :rtype: List[Room]
    """
    ranking = get_ranking(date, start_time, end_time, seating_capacity, projector, blackboard, smartboard, microphone, pc, whiteboard, air_quality_preference, noise_level, lighting)
    return jsonify(ranking)
