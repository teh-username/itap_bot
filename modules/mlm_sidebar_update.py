import datetime
from utils.config_reader import get_config
from utils.date_helpers import convert_seconds_to_dhms

mlm_desc_marker_string = 'Mona Lisa Monday is currently'
mlm_string = 'Mona Lisa Monday is currently **active**! MLM will end in %s.'
non_mlm_string = (
    'Mona Lisa Monday is currently **not active**!' +
    ' MLM will begin in %s.'
)


def update_announcement_text(
    config,
    mod,
    mod_settings,
    announcement_index,
    display_time
):
    description = mod_settings['description'].split('\n\n')
    cur_announcement = description[announcement_index]
    new_announcement = non_mlm_string
    if datetime.datetime.utcnow().weekday() == int(config['monday']):
        new_announcement = mlm_string
    new_announcement = new_announcement % display_time

    if new_announcement == cur_announcement:
        print('Nothing to do')
        return

    description[announcement_index] = new_announcement
    mod.update(
        description='\n\n'.join(description),
        key_color='#545452',
        show_media_preview=True,
        allow_images=True
    )


def get_mlm_announcement_index_in_description(mod_settings):
    desc = mod_settings['description'].split('\n\n')
    index = [k for k, i in enumerate(desc) if mlm_desc_marker_string in i][0]
    if index:
        return index
    raise Exception(
        'Cannot determine where to put announcement in description'
    )


def compute_how_much_time_left(now, target_day):
    end_datetime = datetime.datetime.combine(
        now.date(),
        datetime.time(23, 59, 59)
    )
    if now.weekday() != target_day:
        days_left = target_day - now.weekday()
        if days_left <= 0:
            days_left += 7

        end_datetime = datetime.datetime.combine(
            now.date() + datetime.timedelta(days_left),
            datetime.time(0, 0, 0)
        )

    dhms = convert_seconds_to_dhms(
        (end_datetime - now).total_seconds()
    )

    return_time = '<1 hour'

    if dhms['days'] >= 1:
        if dhms['hours'] >= 12:
            dhms['days'] += 1
        return_time = '{} day/s'.format(dhms['days'])
    elif dhms['hours'] > 1:
        return_time = '{} hour/s'.format(dhms['hours'])

    return return_time


def run(r):
    print('Starting update of sidebar...')
    config = get_config('core')
    mod = r.subreddit(config['subreddit']).mod
    mod_settings = mod.settings()

    time_left = compute_how_much_time_left(
        datetime.datetime.utcnow(),
        int(config['monday'])
    )

    announcement_index = get_mlm_announcement_index_in_description(
        mod_settings
    )

    update_announcement_text(
        config,
        mod,
        mod_settings,
        announcement_index,
        time_left
    )
    print('Update of sidebar successful!')


if __name__ == '__main__':
    print('Not for standalone use')
