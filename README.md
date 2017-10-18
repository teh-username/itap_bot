# r/itookapicture bot [![Build Status](https://travis-ci.org/teh-username/itap_bot.svg?branch=master)](https://travis-ci.org/teh-username/itap_bot)

Reddit bot for [r/itookapicture](https://www.reddit.com/r/itookapicture)

### Feature List

* Updates countdown in the sidebar for Mona Lisa Monday
* Automatically removes non-mod approved MLM related submissions on a non-monday
* Aggregates top-level comments of a "Best Of" submission thread (turned off by default)

### Prerequisites
* Python 2.7.9 and above (developed on Python 3.5.2)
* [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
* git


### Installation
```bash
# clone repository
git clone https://github.com/teh-username/itap_bot.git

cd itap_bot

# setup virtual env for bot
virtualenv itap

# install requirements
itap/bin/pip install -r requirements.txt

# run the bot
itap/bin/python itap_bot.py
```


### Additional Configs
* Script retrieves credentials environment variable. Please set the following (more info [here](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#script-application)):
    * `ITAP_ID`
    * `ITAP_SECRET`
    * `ITAP_USERNAME`
    * `ITAP_PASSWORD`


### Execution flags
* `--debug` enables logging of relevant states of the bot.
* `--best-of` enables one-time execution of "Best Of" feature.
