import ConfigParser
import datetime
import re
import time

# Retrieve config
configParser = ConfigParser.ConfigParser()
configParser.read('config.ini')
config = dict(configParser.items('best-of-settings'))
config['best_of_categories'] = config['best_of_categories'].replace(
    ' ', ''
).split(',')


def generate_best_of_lists(r):
    start_timestamp = (
        datetime.datetime(
            int(config['best_of_year']), 1, 1
        ) - datetime.datetime(1970, 1, 1)
    ).total_seconds()

    entries = {
        'categorized': {},
        'uncategorized': set()
    }

    submission = r.get_submission(
        submission_id=config['best_of_nomination_post_id']
    )
    submission.replace_more_comments(limit=None, threshold=0)
    nominations = submission.comments
    for nomination in nominations:
        if nomination.banned_by is not None:
            continue

        body = nomination.body.lower()
        search = re.search(r'(http(s|):\/\/.*?)(\)| |$)', body, re.M | re.I)

        # ignore deleted comments
        if search is None:
            continue

        corrected_url = search.group(1).rsplit('/', 1)[0].replace(
            '://m.', '://www.'
        )

        # ignore bogus urls
        try:
            entry = r.get_submission(corrected_url)
        except:
            continue

        # ignore posts older than this year
        if entry.created_utc < start_timestamp:
            continue

        has_no_category = True
        for category in config['best_of_categories']:
            if category not in entries['categorized']:
                entries['categorized'][category] = set()
            if category in body:
                has_no_category = False
                entries['categorized'][category].add((
                    entry.title, entry.permalink, entry.url, category
                ))

        if has_no_category:
            entries['uncategorized'].add((
                entry.title, entry.permalink, entry.url
            ))

    with open(
        'best_of_{0}_categorized.txt'.format(
            config['best_of_nomination_post_id']
        ),
        'w'
    ) as f:
        for category in sorted(entries['categorized'].keys()):
            f.write('>>>{0}\n'.format(category))
            for entry in entries['categorized'][category]:
                f.write('* [{0}]({1}) - [Photo]({2})\n'.format(
                    entry[0],
                    entry[1],
                    entry[2]
                ))

    with open(
        'best_of_{0}_uncategorized.txt'.format(
            config['best_of_nomination_post_id']
        ),
        'w'
    ) as f:
        for entry in entries['uncategorized']:
            f.write('* [{0}]({1}) - [Photo]({2})\n'.format(
                entry[0],
                entry[1],
                entry[2]
            ))

    print('Aggregation of {0} nomination thread completed'.format(
        config['best_of_nomination_post_id']
    ))


def post_nominations_to_voting_thread(r):
    voting_thread = r.get_submission(
        submission_id=config['best_of_voting_post_id']
    )
    target_parent = ''
    with open(
        'best_of_{0}_categorized.txt'.format(
            config['best_of_nomination_post_id']
        ),
        'r'
    ) as f:
        for line in f:
            if '>>>' in line:
                x = voting_thread.add_comment(line[3:].title()).distinguish()
                target_parent = x['data']['things'][0]
            else:
                target_parent.reply(line).distinguish()
            time.sleep(1)

    print(
        'Population of {0} voting thread completed'.format(
            config['best_of_voting_post_id']
        )
    )


def run(r):
    print('Starting best of processing...')
    generate_best_of_lists(r)
    time.sleep(1)
    post_nominations_to_voting_thread(r)


if __name__ == '__main__':
    print('Not for standalone use')
