import unittest
from unittest.mock import patch, Mock, PropertyMock
import datetime
from modules import mlm_sidebar_update


class MLMSidebarUpdateModuleTestCase(unittest.TestCase):
    @patch('modules.mlm_sidebar_update.update_announcement_text')
    @patch(
        'modules.mlm_sidebar_update.get_mlm_announcement_index_in_description'
    )
    @patch('modules.mlm_sidebar_update.compute_how_much_time_left')
    @patch('modules.mlm_sidebar_update.get_config')
    @patch('datetime.datetime')
    def test_should_call_update_announcement_text_correctly(
            self,
            datetime_mock,
            get_config_mock,
            compute_how_much_time_left_mock,
            get_mlm_announcement_index_in_description_mock,
            update_announcement_text_mock,
    ):
        # config mock
        get_config_mock.return_value = {
            'subreddit': 'REEEEE',
            'monday': '0'
        }

        # reddit mock
        mod_mock = Mock()
        mod_mock.settings.return_value = {
            'wise': 'Darth Plagueis'
        }
        reddit_mock = Mock()
        type(reddit_mock.subreddit.return_value).mod = PropertyMock(
            return_value=mod_mock
        )

        # datetime mock
        datetime_mock.utcnow.return_value = 9872

        # compute time left mock
        compute_how_much_time_left_mock.return_value = '1 Day/s'

        # get announcement index mock
        get_mlm_announcement_index_in_description_mock.return_value = 75

        mlm_sidebar_update.run(reddit_mock)

        # assertions
        reddit_mock.subreddit.assert_called_once_with('REEEEE')
        compute_how_much_time_left_mock.assert_called_once_with(9872, 0)
        get_mlm_announcement_index_in_description_mock.assert_called_once_with(
            {'wise': 'Darth Plagueis'}
        )
        update_announcement_text_mock.assert_called_once_with(
            {'subreddit': 'REEEEE', 'monday': '0'},
            mod_mock,
            {'wise': 'Darth Plagueis'},
            75,
            '1 Day/s'
        )

    def test_should_compute_the_correct_time_left(self):
        self.assertEqual(
            mlm_sidebar_update.compute_how_much_time_left(
                datetime.datetime(2017, 8, 5, 8, 58, 57, 218258),
                0
            ),
            '2 day/s'
        )

        self.assertEqual(
            mlm_sidebar_update.compute_how_much_time_left(
                datetime.datetime(2017, 8, 6, 20, 58, 57, 218258),
                0
            ),
            '3 hour/s'
        )

        self.assertEqual(
            mlm_sidebar_update.compute_how_much_time_left(
                datetime.datetime(2017, 8, 6, 23, 58, 57, 218258),
                0
            ),
            '<1 hour'
        )

    def test_should_return_correct_index_in_description(self):
        self.assertEqual(
            mlm_sidebar_update.get_mlm_announcement_index_in_description(
                {
                    'description': (
                        'Did you ever hear the tragedy of REEE The Wise?\n\n'
                        'It’s not a story the Normies would tell you.\n\n'
                        'Mona Lisa Monday is currently It’s a Sith legend.\n\n'
                        'Darth Plagueis was a Dark Lord of the Sith\n\n'
                    )
                }
            ),
            2
        )

    def test_should_raise_exception_if_marker_is_not_found(self):
        with self.assertRaises(Exception):
            mlm_sidebar_update.get_mlm_announcement_index_in_description(
                {
                    'description': (
                        'Did you ever hear the tragedy of REEE The Wise?\n\n'
                        'It’s not a story the Normies would tell you.\n\n'
                        'It’s a Sith legend.\n\n'
                        'Darth Plagueis was a Dark Lord of the Sith\n\n'
                    )
                }
            )

    @patch('datetime.datetime')
    def test_should_not_update_description_non_mlm(self, datetime_mock):
        datetime_mock.utcnow.weekday.return_value = 1
        mod_mock = Mock()
        settings = {
            'description': (
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'non_mlm_time 3 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            )
        }
        mlm_sidebar_update.non_mlm_string = 'non_mlm_time %s'
        mlm_sidebar_update.update_announcement_text(
            {'monday': '0'},
            mod_mock,
            settings,
            1,
            '3 day/s'
        )

        mod_mock.update.assert_not_called()

    @patch('datetime.datetime')
    def test_should_not_update_description_mlm(self, datetime_mock):
        datetime_mock.utcnow.weekday.return_value = 1
        mod_mock = Mock()
        settings = {
            'description': (
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'mlm_time 3 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            )
        }
        mlm_sidebar_update.non_mlm_string = 'mlm_time %s'
        mlm_sidebar_update.update_announcement_text(
            {'monday': '0'},
            mod_mock,
            settings,
            1,
            '3 day/s'
        )

        mod_mock.update.assert_not_called()

    @patch('datetime.datetime')
    def test_should_update_description_non_mlm(self, datetime_mock):
        datetime_mock.utcnow.weekday.return_value = 0
        mod_mock = Mock()
        settings = {
            'description': (
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'non_mlm_time 5 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            )
        }
        mlm_sidebar_update.non_mlm_string = 'non_mlm_time %s'
        mlm_sidebar_update.update_announcement_text(
            {'monday': '0'},
            mod_mock,
            settings,
            1,
            '3 day/s'
        )

        mod_mock.update.assert_called_once_with(
            description=(
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'non_mlm_time 3 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            ),
            key_color='#545452',
            show_media_preview=True,
            allow_images=True
        )

    @patch('datetime.datetime')
    def test_should_update_description_mlm(self, datetime_mock):
        datetime_mock.utcnow.weekday.return_value = 0
        mod_mock = Mock()
        settings = {
            'description': (
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'mlm_time 5 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            )
        }
        mlm_sidebar_update.non_mlm_string = 'mlm_time %s'
        mlm_sidebar_update.update_announcement_text(
            {'monday': '0'},
            mod_mock,
            settings,
            1,
            '3 day/s'
        )

        mod_mock.update.assert_called_once_with(
            description=(
                'Did you ever hear the tragedy of REEE The Wise?\n\n'
                'mlm_time 3 day/s\n\n'
                'It’s a Sith legend.\n\n'
                'Darth Plagueis was a Dark Lord of the Sith\n\n'
            ),
            key_color='#545452',
            show_media_preview=True,
            allow_images=True
        )
