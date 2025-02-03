import connexion
import six

from swagger_server.models.room import Room  # noqa: E501
from swagger_server import util
from modules.decision_logic import get_ranking
from flask import jsonify


def rank_rooms(date, start_time, end_time, seating_capacity, projector, blackboard, smartboard, microphone, pc, whiteboard, air_quality_preference, noise_level, lighting, temperature, equipment_weight, air_quality_weight, temperature_weight, noise_weight, light_weight):  # noqa: E501
    """Get a ranked list of available rooms based on preferences

     # noqa: E501

    :param _date: 
    :type _date: str
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
    :param temperature: 
    :type temperature: str
    :param equipment_weight: 
    :type equipment_weight: int
    :param air_quality_weight: 
    :type air_quality_weight: int
    :param temperature_weight: 
    :type temperature_weight: int
    :param noise_weight: 
    :type noise_weight: int
    :param light_weight: 
    :type light_weight: int

    :rtype: List[Room]
    """
    ranking = get_ranking(
        date=date,
        start_time=start_time,
        end_time=end_time,
        seating_capacity=seating_capacity,
        projector=projector,
        blackboard=blackboard,
        smartboard=smartboard,
        microphone=microphone,
        pc=pc,
        whiteboard=whiteboard,
        air_quality_preference=air_quality_preference,
        noise_level=noise_level,
        lighting=lighting,
        temperature_preference=temperature,
        equipment_weight=equipment_weight,
        air_quality_weight=air_quality_weight,
        temperature_weight=temperature_weight,
        noise_weight=noise_weight,
        light_weight=light_weight
    )
    return jsonify(ranking)
