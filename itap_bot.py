import datetime
import time
import sys
import praw
import schedule

# vars
WEEKDAY_MONDAY = 0
timekeeping = -1
subreddit = 'itookapicture'
debug = True if len(sys.argv) == 2 and sys.argv[1] == '--debug' else False

# generate instance of praw
print 'Logging in...'
user_agent = "r/itookapicture MLM announcer v1.0.1 by /u/tehusername"
r = praw.Reddit(user_agent = user_agent)
r.login(disable_warning=True)
print 'Login successful...'

def update_sidebar(r, data):
    global timekeeping
    if timekeeping != data['delta_time']['const']:
        print 'Updating %s sidebar...' % subreddit
        token = '\n\n'
        mark_string = 'Mona Lisa Monday is currently'
        before_string = '**Posting Suggestions:**'
        monday = "Mona Lisa Monday is currently **active**! MLM will end in %s."
        non_monday = "Mona Lisa Monday is currently **not active**! MLM will begin in %s."

        desc = r.get_settings(subreddit)['description'].split(token)
        index = [k for k, i in enumerate(desc) if mark_string in i]
        announce_text = (monday if data['is_monday'] else non_monday) % (data['delta_time']['time'])

        if not index:
            index = [k for k, i in enumerate(desc) if before_string in i][0]
            desc.insert(index, announce_text)
        else:
            desc[index[0]] = announce_text

        r.update_settings(r.get_subreddit(subreddit), description=token.join(desc))
        timekeeping = data['delta_time']['const']

        if debug:
            with open("log.txt", "a") as log:
                log.write(str(datetime.datetime.utcnow()) + '\n')

        print 'Update successful! Sleeping...'
    else:
        print 'Not yet time to update. Sleeping...'

def get_content():
    print 'Computing date deltas...'
    dt = datetime.datetime.utcnow()
    ret = {
        'is_monday': dt.weekday() == WEEKDAY_MONDAY
    }

    end_date = None
    if ret['is_monday']:
        (y, m, d) = map(int, str(dt.date()).split('-'))
        end_date = datetime.datetime(y, m, d, 23, 59, 59)
    else:
        ahead = WEEKDAY_MONDAY - dt.weekday()
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

def run_update():
    data = get_content()
    update_sidebar(r, data)

if __name__ == '__main__':
    print 'Initial ITAP_bot run'
    run_update()
    schedule.every().minute.do(run_update)
    print 'Running on schedule'
    while True:
        schedule.run_pending()
        time.sleep(1)
