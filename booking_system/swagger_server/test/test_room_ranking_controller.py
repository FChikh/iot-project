# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.ranking_request import RankingRequest  # noqa: E501
from swagger_server.models.room import Room  # noqa: E501
from swagger_server.test import BaseTestCase


class TestRoomRankingController(BaseTestCase):
    """RoomRankingController integration test stubs"""

    def test_rank_rooms(self):
        """Test case for rank_rooms

        Get ranked list of available rooms
        """
        body = RankingRequest()
        response = self.client.open(
            '/rank-rooms',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
