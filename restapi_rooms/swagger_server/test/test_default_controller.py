# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.room_air_quality import RoomAirQuality  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_humidity import RoomHumidity  # noqa: E501
from swagger_server.models.room_light import RoomLight  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_room_id_airquality_get(self):
        """Test case for room_id_airquality_get

        Get air quality data for a specific room
        """
        response = self.client.open(
            '/{room_id}/airquality'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_room_id_bookings_get(self):
        """Test case for room_id_bookings_get

        Get bookings for specific room
        """
        query_string = [('start_date', '2013-10-20'),
                        ('days', 56)]
        response = self.client.open(
            '/{room_id}/bookings'.format(room_id='room_id_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_room_id_humidity_get(self):
        """Test case for room_id_humidity_get

        Get humidity data for a specific room
        """
        response = self.client.open(
            '/{room_id}/humidity'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_room_id_light_get(self):
        """Test case for room_id_light_get

        Get light data for a specific room
        """
        response = self.client.open(
            '/{room_id}/light'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_room_id_temperature_get(self):
        """Test case for room_id_temperature_get

        Get temperature data for a specific room
        """
        response = self.client.open(
            '/{room_id}/temperature'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_airquality_get(self):
        """Test case for rooms_airquality_get

        Get air quality data for all rooms
        """
        response = self.client.open(
            '/rooms/airquality',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_bookings_get(self):
        """Test case for rooms_bookings_get

        Get bookings for all rooms
        """
        query_string = [('start_date', '2013-10-20'),
                        ('days', 56)]
        response = self.client.open(
            '/rooms/bookings',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_humidity_get(self):
        """Test case for rooms_humidity_get

        Get humidity data for all rooms
        """
        response = self.client.open(
            '/rooms/humidity',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_light_get(self):
        """Test case for rooms_light_get

        Get light data for all rooms
        """
        response = self.client.open(
            '/rooms/light',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_temperature_get(self):
        """Test case for rooms_temperature_get

        Get temperature data for all rooms
        """
        response = self.client.open(
            '/rooms/temperature',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sensor_room_id_get(self):
        """Test case for sensor_room_id_get

        Get sensor data for a specific room
        """
        response = self.client.open(
            '/sensor/{room_id}'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sensor_rooms_get(self):
        """Test case for sensor_rooms_get

        Get sensor data for all rooms
        """
        response = self.client.open(
            '/sensor/rooms',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
