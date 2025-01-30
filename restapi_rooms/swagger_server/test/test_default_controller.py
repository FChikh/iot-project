# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response400 import InlineResponse400  # noqa: E501
from swagger_server.models.inline_response409 import InlineResponse409  # noqa: E501
from swagger_server.models.inline_response500 import InlineResponse500  # noqa: E501
from swagger_server.models.room_air_quality10 import RoomAirQuality10  # noqa: E501
from swagger_server.models.room_air_quality25 import RoomAirQuality25  # noqa: E501
from swagger_server.models.room_co2 import RoomCo2  # noqa: E501
from swagger_server.models.room_data import RoomData  # noqa: E501
from swagger_server.models.room_equipment import RoomEquipment  # noqa: E501
from swagger_server.models.room_humidity import RoomHumidity  # noqa: E501
from swagger_server.models.room_light import RoomLight  # noqa: E501
from swagger_server.models.room_noise import RoomNoise  # noqa: E501
from swagger_server.models.room_temperature import RoomTemperature  # noqa: E501
from swagger_server.models.room_voc import RoomVoc  # noqa: E501
from swagger_server.models.rooms_room_id_body import RoomsRoomIdBody  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_book_rooms_room_id_post(self):
        """Test case for book_rooms_room_id_post

        Book a specific room
        """
        body = RoomsRoomIdBody()
        response = self.client.open(
            '/book/rooms/{room_id}'.format(room_id='room_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_aq_pm10_get(self):
        """Test case for rooms_aq_pm10_get

        Retrieve air quality data (pm10)
        """
        response = self.client.open(
            '/rooms/aq_pm10',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_aq_pm25_get(self):
        """Test case for rooms_aq_pm25_get

        Retrieve air quality data (pm2.5)
        """
        response = self.client.open(
            '/rooms/aq_pm2_5',
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

    def test_rooms_co2_get(self):
        """Test case for rooms_co2_get

        Retrieve CO2 level data for all rooms.
        """
        response = self.client.open(
            '/rooms/co2',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_equipment_get(self):
        """Test case for rooms_equipment_get

        Get information about the equipment in each room
        """
        response = self.client.open(
            '/rooms/equipment',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_humidity_get(self):
        """Test case for rooms_humidity_get

        Retrieve humidity data for all rooms
        """
        response = self.client.open(
            '/rooms/humidity',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_light_get(self):
        """Test case for rooms_light_get

        Retrieve light intensity data for all rooms
        """
        response = self.client.open(
            '/rooms/light',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_noise_get(self):
        """Test case for rooms_noise_get

        Retrieve sound level data for all rooms.
        """
        response = self.client.open(
            '/rooms/noise',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_aq_pm10_get(self):
        """Test case for rooms_room_id_aq_pm10_get

        Get air quality data for a specific room (i.e. pm10)
        """
        response = self.client.open(
            '/rooms/{room_id}/aq_pm10'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_aq_pm25_get(self):
        """Test case for rooms_room_id_aq_pm25_get

        Get air quality data for a specific room (i.e. pm2.5)
        """
        response = self.client.open(
            '/rooms/{room_id}/aq_pm2_5'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_bookings_get(self):
        """Test case for rooms_room_id_bookings_get

        Get bookings for specific room
        """
        query_string = [('start_date', '2013-10-20'),
                        ('days', 56)]
        response = self.client.open(
            '/rooms/{room_id}/bookings'.format(room_id='room_id_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_co2_get(self):
        """Test case for rooms_room_id_co2_get

        Get co2 data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/co2'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_equipment_get(self):
        """Test case for rooms_room_id_equipment_get

        Get the available equipment for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/equipment'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_humidity_get(self):
        """Test case for rooms_room_id_humidity_get

        Retrieve humidity data for a specific room.
        """
        response = self.client.open(
            '/rooms/{room_id}/humidity'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_light_get(self):
        """Test case for rooms_room_id_light_get

        Get light data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/light'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_noise_get(self):
        """Test case for rooms_room_id_noise_get

        Get noise/sound data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/noise'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_sensor_get(self):
        """Test case for rooms_room_id_sensor_get

        Get sensor data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/sensor'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_temperature_get(self):
        """Test case for rooms_room_id_temperature_get

        Retrieve temperature data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/temperature'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_room_id_voc_get(self):
        """Test case for rooms_room_id_voc_get

        Get voc data for a specific room
        """
        response = self.client.open(
            '/rooms/{room_id}/voc'.format(room_id='room_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_sensor_get(self):
        """Test case for rooms_sensor_get

        Get sensor data for all rooms
        """
        response = self.client.open(
            '/rooms/sensor',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_temperature_get(self):
        """Test case for rooms_temperature_get

        Retrieve temperature data for all rooms.
        """
        response = self.client.open(
            '/rooms/temperature',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_rooms_voc_get(self):
        """Test case for rooms_voc_get

        Retrieve VOC concentration data for all rooms.
        """
        response = self.client.open(
            '/rooms/voc',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
