# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.room import Room  # noqa: E501
from swagger_server.test import BaseTestCase


class TestRoomRankingController(BaseTestCase):
    """RoomRankingController integration test stubs"""

    def test_rank_rooms(self):
        """Test case for rank_rooms

        Get a ranked list of available rooms based on preferences
        """
        query_string = [('_date', '2013-10-20'),
                        ('start_time', 'start_time_example'),
                        ('end_time', 'end_time_example'),
                        ('seating_capacity', 2),
                        ('projector', false),
                        ('blackboard', false),
                        ('smartboard', false),
                        ('microphone', false),
                        ('pc', false),
                        ('whiteboard', false),
                        ('air_quality_preference', 'normal'),
                        ('noise_level', 'normal'),
                        ('lighting', 'normal'),
                        ('temperature', 'moderate'),
                        ('equipment_weight', 1),
                        ('air_quality_weight', 1),
                        ('temperature_weight', 1),
                        ('noise_weight', 1),
                        ('light_weight', 1)]
        response = self.client.open(
            '/rank-rooms',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
