import calendar
import datetime
import os
from utils.config_reader import get_config
from modules.mlm_sidebar_update import (
    compute_how_much_time_left
)


def notify_violating_submissions(r, config, last_ts):
    cur_ts = calendar.timegm(
        datetime.datetime.utcnow().utctimetuple()
    )
    time_left = compute_how_much_time_left(
        datetime.datetime.utcnow(),
        int(config['monday'])
    )
    subreddit = r.subreddit(config['subreddit'])
    for post in subreddit.submissions(start=last_ts, end=cur_ts):
        if config['mlm_string'] in post.title and post.approved_by is None:
            print('Detected violator: %s, processing...' % post.id)
            warn_string = config['warning_string'].replace(
                '[time]',
                time_left
            ).replace('\n', '\n\n')
            post.reply(warn_string).mod.distinguish(sticky=True)
            post.mod.remove()


def get_last_timestamp(config):
    last_ts = calendar.timegm(
        datetime.datetime.utcnow().utctimetuple()
    )
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
