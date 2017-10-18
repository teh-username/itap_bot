import calendar
import datetime
import time
import os
import sys
import praw
import schedule
from utils.config_reader import get_config
from modules.mlm_sidebar_update import run as mlm_run

# system wide flags
timekeeping = -1
debug = True if '--debug' in sys.argv[1:] else False
best_of = True if '--best-of' in sys.argv[1:] else False


# Retrieve config
config = get_config('core')
config['monday'] = int(config['monday'])


# Add-on Module/s
if best_of:
    import imp
    best_of = imp.load_source('best_of', 'modules/best_of.py')


# generate instance of praw
print('Logging in...')

user_agent = "r/itookapicture MLM announcer v4.1.0 by /u/tehusername"

while True:
    try:
        r = praw.Reddit(
            client_id=os.environ['ITAP_ID'],
            client_secret=os.environ['ITAP_SECRET'],
            username=os.environ['ITAP_USERNAME'],
            password=os.environ['ITAP_PASSWORD'],
            user_agent=user_agent
        )
        print('Login successful...')
        break
    except:
        print('Error Logging in. Retrying in 1 minute...')
        time.sleep(60)


def get_content():
    print('Computing date deltas...')
    dt = datetime.datetime.utcnow()
    ret = {
        'is_monday': dt.weekday() == config['monday']
    }

    end_date = None
    if ret['is_monday']:
        (y, m, d) = map(int, str(dt.date()).split('-'))
        end_date = datetime.datetime(y, m, d, 23, 59, 59)
    else:
        ahead = config['monday'] - dt.weekday()
        if ahead <= 0:
            ahead += 7
        (y, m, d) = map(
            int,
            str(dt.date() + datetime.timedelta(ahead)).split('-')
        )
        end_date = datetime.datetime(y, m, d, 0, 1, 0)

    delta_seconds = (end_date - dt).total_seconds()
    m, s = divmod(delta_seconds, 60)
    h, m = map(int, divmod(m, 60))
    d, h = map(int, divmod(h, 24))

    return_time = "<1 hour"
    return_const = 0

    if d >= 1:
        if h >= 12:
            return_time = "%d day/s" % (d + 1)
        else:
            return_time = "%d day/s" % (d)
        return_const = d
    elif h > 1:
        return_time = "%d hour/s" % (h)
        return_const = h

    ret['delta_time'] = {'time': return_time, 'const': return_const}
    return ret


def check_submissions(data):
    print('Checking submissions...')
    if not data['is_monday']:
        last_ts = cur_ts = calendar.timegm(
            datetime.datetime.utcnow().utctimetuple()
        )
        # we've been going at it for a while
        if os.path.exists(config['state_filename']):
            with open(config['state_filename'], 'r') as log:
                last_ts = log.read()  # so get the last timestamp instead
        else:  # just fresh out of monday
            # log to start checking from here on out
            # (don't accidentally remove legit posts)
            with open(config['state_filename'], 'w') as log:
                log.write(str(last_ts))

        # we then retrieve posts inbetween ts
        subreddit = r.subreddit(config['subreddit'])

        # loops thru all posts
        for post in subreddit.submissions(start=last_ts, end=cur_ts):
            if config['mlm_string'] in post.title and post.approved_by is None:
                print('Detected violator: %s, processing...' % post.id)
                warn_string = config['warning_string'].replace(
                    '[time]',
                    data['delta_time']['time']
                ).replace('\n', '\n\n')
                # adds comment then distinguish it
                post.reply(warn_string).mod.distinguish(sticky=True)
                # removes submission
                post.mod.remove()
                if debug:
                    with open(config['log_filename'], "a") as log:
                        log.write('Removed post %s \n' % (post.id))

        # log last time checked
        with open(config['state_filename'], 'w') as log:
            log.write(str(last_ts))
    else:
        # if state file exists, delete it to trigger fresh copy on a non monday
        if os.path.exists(config['state_filename']):
            os.remove(config['state_filename'])


def run_update():
    data = get_content()
    try:
        mlm_run(r)
        check_submissions(data)
    except Exception as e:
        print(str(e))
        print(config['hiccup_string'])


if __name__ == '__main__':
    print('Initial ITAP_bot run')
    run_update()
    schedule.every().minute.do(run_update)
    print('Running on schedule')

    if best_of is not False:
        best_of.run(r)

    while True:
        schedule.run_pending()
        time.sleep(1)
