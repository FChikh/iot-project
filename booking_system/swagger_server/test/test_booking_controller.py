# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.booking_confirmation import BookingConfirmation  # noqa: E501
from swagger_server.models.booking_rejection import BookingRejection  # noqa: E501
from swagger_server.models.booking_request import BookingRequest  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBookingController(BaseTestCase):
    """BookingController integration test stubs"""

    def test_book_room(self):
        """Test case for book_room

        Book a specific room
        """
        body = BookingRequest()
        response = self.client.open(
            '/bookings',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
