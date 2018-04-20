import os
import time
import traceback
import sys
import praw
import schedule
from utils.config_reader import get_config
from modules.mlm_sidebar_update import run as mlm_sidebar_update
from modules.mlm_submission_check import (
    run as mlm_submission_check
)

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

user_agent = "r/itookapicture MLM announcer v4.2.0 by /u/tehusername"

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
    except:  # noqa
        print('Error Logging in. Retrying in 1 minute...')
        time.sleep(60)


def run_update():
    try:
        mlm_sidebar_update(r)
        mlm_submission_check(r)
    except Exception as e:  # noqa
        print(traceback.format_exc())
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
