config = {
    'core': {
        'monday': 0,
        'subreddit': 'itookapicture',
        'mlm_string': '[MLM]',
        'warning_string': (
            'Mona Lisa Monday tag detected, please resubmit on a '
            '**Monday (midnight - midnight GMT)**. '
            'Mona Lisa Monday begins in [time]. '
            'If your post was only a little late, '
            'please message the moderators for manual approval.\n'
            '---\n'
            '*This action was performed automatically. '
            'If you think there\'s been an error, please '
            '[message the subreddit\'s moderators]'
            '(https://www.reddit.com/message/compose?'
            'to=%2Fr%2Fitookapicture&subject=&message=).*'
        ),
        'state_filename': 'time.txt',
        'log_filename': 'log.txt',
        'hiccup_string': 'Something went wrong. Will retry next iteration.',
        'key_color': '#545452',
    },
    'best_of': {
        'best_of_categories': 'portrait, landscape, animal, street',
        'best_of_nomination_post_id': '56qtt0',
        'best_of_voting_post_id': '56w6pu',
        'best_of_year': '2016',
    }
}
