import unittest
from unittest.mock import patch, MagicMock
from utils import date_helpers
import datetime


class DateHelpersTestCase(unittest.TestCase):
    @patch('datetime.datetime')
    def test_is_target_day(self, datetime_mock):
        mock = datetime.datetime
        mock.weekday = MagicMock(return_value=0)
        datetime_mock.utcnow.return_value = mock
        self.assertEqual(
            date_helpers.is_target_day(0),
            True
        )

        mock.weekday = MagicMock(return_value=5)
        datetime_mock.utcnow.return_value = mock
        self.assertEqual(
            date_helpers.is_target_day(1),
            False
        )

    def test_convert_seconds_to_dhms(self):
        self.assertEqual(
            date_helpers.convert_seconds_to_dhms(345334),
            {'days': 3, 'hours': 23, 'minutes': 55, 'seconds': 34}
        )

        self.assertEqual(
            date_helpers.convert_seconds_to_dhms(999),
            {'days': 0, 'hours': 0, 'minutes': 16, 'seconds': 39}
        )
