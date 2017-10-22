import unittest
from unittest.mock import patch, mock_open
from modules import mlm_submission_check


class MLMSubmissionCheckModuleTestCase(unittest.TestCase):
    @patch('modules.mlm_submission_check.utc_timestamp_now')
    @patch('modules.mlm_submission_check.os.path')
    @patch('modules.mlm_submission_check.open', new_callable=mock_open)
    def test_should_generate_timestamp_as_now(
            self,
            open_mock,
            os_path_mock,
            utc_now_mock,
    ):
        utc_now_mock.return_value = 1337
        os_path_mock.exists.return_value = False
        last_ts = mlm_submission_check.get_last_timestamp({
            'state_filename': 'wot'
        })

        self.assertEqual(last_ts, 1337)
        open_mock().write.assert_called_with('1337')

    @patch('modules.mlm_submission_check.utc_timestamp_now')
    @patch('modules.mlm_submission_check.os.path')
    @patch(
        'modules.mlm_submission_check.open',
        new_callable=mock_open,
        read_data='15'
    )
    def test_should_get_timestamp_from_file(
            self,
            open_mock,
            os_path_mock,
            utc_now_mock,
    ):
        utc_now_mock.return_value = 1337
        os_path_mock.exists.return_value = True
        last_ts = mlm_submission_check.get_last_timestamp({
            'state_filename': 'wot'
        })
        self.assertEqual(
            open_mock().read.call_count,
            1
        )
        self.assertEqual(last_ts, '15')

    @patch('modules.mlm_submission_check.datetime.datetime')
    def test_should_not_check_for_submissions(
            self,
            datetime_mock
    ):
        datetime_mock.utcnow.return_value.weekday.return_value = 1
        self.assertEqual(
            mlm_submission_check.should_check_submissions({
                'monday': 0
            }),
            True
        )

    @patch('modules.mlm_submission_check.datetime.datetime')
    def test_should_check_for_submissions(
            self,
            datetime_mock
    ):
        datetime_mock.utcnow.return_value.weekday.return_value = 0
        self.assertEqual(
            mlm_submission_check.should_check_submissions({
                'monday': 0
            }),
            False
        )
