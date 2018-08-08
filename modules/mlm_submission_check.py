import datetime
import os
import requests
import time

from utils.config_reader import get_config
from utils.date_helpers import utc_timestamp_now
from modules.mlm_sidebar_update import (
    compute_how_much_time_left
)


def get_submissions(subreddit, start, end):
    api_url = (
        "https://api.pushshift.io/reddit/search/submission/?"
        "subreddit={}&before={}&after={}"
    ).format(subreddit, end, start)
    print('Getting submissions from %s' % api_url)
    response = requests.get(api_url)
    return response.json()['data']


def is_violator(post, mlm_string):
    if post.approved_by is not None:
        return False

    if post.banned_by is not None:
        return False

    if mlm_string not in post.title:
        return False

    return True


def notify_violating_submissions(r, config, last_ts):
    cur_ts = utc_timestamp_now()
    time_left = compute_how_much_time_left(
        datetime.datetime.utcnow(),
        int(config['monday'])
    )
    submissions = get_submissions(
        subreddit=config['subreddit'],
        start=last_ts,
        end=cur_ts
    )
    for submission in submissions:
        post = r.submission(id=submission['id'])
        if is_violator(post, config['mlm_string']):
            print('Detected violator: %s, processing...' % post.id)
            warn_string = config['warning_string'].replace(
                '[time]',
                time_left
            ).replace('\n', '\n\n')
            post.reply(warn_string).mod.distinguish(sticky=True)
            post.mod.remove()
            time.sleep(0.5)


def get_last_timestamp(config):
    last_ts = utc_timestamp_now()
    # we've been going at it for a while
    if os.path.exists(config['state_filename']):
        with open(config['state_filename'], 'r') as log:
            last_ts = log.read()
    else:  # just fresh out of monday
        # log to start checking from here on out
        # (don't accidentally remove legit posts)
        with open(config['state_filename'], 'w') as log:
            log.write(str(last_ts))

    return last_ts


def should_check_submissions(config):
    return (
        datetime.datetime.utcnow().weekday() !=
        int(config['monday'])
    )


def run(r):
    print('Checking submissions...')
    config = get_config('core')
    if should_check_submissions(config):
        notify_violating_submissions(
            r,
            config,
            get_last_timestamp(config)
        )
    else:
        # if state file exists, delete it to trigger fresh copy on a non monday
        if os.path.exists(config['state_filename']):
            os.remove(config['state_filename'])
    print('Submission purge complete!')


if __name__ == '__main__':
    print('Not for standalone use')
