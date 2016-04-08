import calendar
import ConfigParser
import datetime
import time
import os
import sys
import praw
import schedule


# Retrieve config
configParser = ConfigParser.ConfigParser()
configParser.read('config.ini')
config = dict(configParser.items('core-settings'))
config['monday'] = int(config['monday'])


# system wide flags
timekeeping = -1
debug = True if len(sys.argv) == 2 and sys.argv[1] == '--debug' else False


# generate instance of praw
print 'Logging in...'
user_agent = "r/itookapicture MLM announcer v2.0.0 by /u/tehusername"
r = praw.Reddit(user_agent = user_agent)
r.login(disable_warning=True)
print 'Login successful...'


# settings for submission_between helper
sub_helper_kwargs = {
    'reddit_session': r,
    'subreddit': config['subreddit'],
    'newest_first': False,
    'verbosity': 0   
}


def update_sidebar(data):
    global timekeeping
    if timekeeping != data['delta_time']['const']:
        print 'Updating %s sidebar...' % config['subreddit']
        token = '\n\n'
        mark_string = 'Mona Lisa Monday is currently'
        before_string = '**Posting Suggestions:**'
        monday = "Mona Lisa Monday is currently **active**! MLM will end in %s."
        non_monday = "Mona Lisa Monday is currently **not active**! MLM will begin in %s."

        desc = r.get_settings(config['subreddit'])['description'].split(token)
        index = [k for k, i in enumerate(desc) if mark_string in i]
        announce_text = (monday if data['is_monday'] else non_monday) % (data['delta_time']['time'])

        if not index:
            index = [k for k, i in enumerate(desc) if before_string in i][0]
            desc.insert(index, announce_text)
        else:
            desc[index[0]] = announce_text

        r.update_settings(r.get_subreddit(config['subreddit']), description=token.join(desc))
        timekeeping = data['delta_time']['const']

        if debug:
            with open(config['log_filename'], "a") as log:
                log.write(str(datetime.datetime.utcnow()) + '\n')

        print 'Update successful! Sleeping...'
    else:
        print 'Not yet time to update. Sleeping...'

def get_content():
    print 'Computing date deltas...'
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
        (y, m, d) = map(int, str(dt.date() + datetime.timedelta(ahead)).split('-'))
        end_date = datetime.datetime(y, m, d, 0, 1, 0)

    delta_seconds = (end_date - dt).total_seconds()
    m, s = divmod(delta_seconds, 60)
    h, m = map(int, divmod(m, 60))
    d, h = map(int, divmod(h, 24))
    
    return_time = "less than a minute"
    return_const = 0
    if d >= 1:
        return_time = "%d day/s" % (d)
        return_const = d
    elif h >= 1:
        return_time = "%d hour/s" % (h)
        return_const = h
    elif m >= 1:
        return_time = "%d minute/s" % (m)
        return_const = m

    ret['delta_time'] = {'time': return_time, 'const': return_const}
    return ret

def check_submissions(data):
    print 'Checking submissions...'
    if not data['is_monday']:
        last_ts = cur_ts = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        if os.path.exists(config['state_filename']): # we've been going at it for a while
            with open(config['state_filename'], 'r') as log:
                last_ts = log.read() # so get the last timestamp instead
        else: # just fresh out of monday
            with open(config['state_filename'], 'w') as log: # log to start checking from here on out (don't accidentally remove legit posts)
                log.write(str(last_ts))

        # we then retrieve posts inbetween ts
        sub_helper_kwargs['lowest_timestamp'] = last_ts
        sub_helper_kwargs['highest_timestamp'] = cur_ts

        # loops thru all posts
        for post in praw.helpers.submissions_between(**sub_helper_kwargs):
            if config['mlm_string'] in post.title:
                print 'Detected violator: %s, processing...' % post.id
                warn_string = config['warning_string'].replace('[time]', data['delta_time']['time']).replace('\n', '\n\n')
                post.add_comment(warn_string).distinguish() # adds comment then distinguish it
                post.remove() # removes submission
                if debug:
                    with open(config['log_filename'], "a") as log:
                        log.write('Removed post %s \n' %(post.id))

        # log last time checked
        with open(config['state_filename'], 'w') as log:
            log.write(str(last_ts))
    else:
        if os.path.exists(config['state_filename']): # if state file exists, delete it to trigger fresh copy on a non monday
            os.remove(config['state_filename'])

def run_update():
    data = get_content()
    update_sidebar(data)
    check_submissions(data)

if __name__ == '__main__':
    print 'Initial ITAP_bot run'
    run_update()
    schedule.every().minute.do(run_update)
    print 'Running on schedule'
    while True:
        schedule.run_pending()
        time.sleep(1)
