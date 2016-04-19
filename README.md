# r/itookapicture bot

---

Reddit bot for [r/itookapicture](https://www.reddit.com/r/itookapicture)

### Feature List

* Updates countdown in the sidebar for Mona Lisa Monday
* Automatically removes non-mod approved MLM related submissions on a non-monday

### Prerequisites
* Python 2.7.9 and above (developed on Python 2.7.11)
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
* Script retrieves credentials via `ITAP_USERNAME` and `ITAP_PASSWORD` environment variables (will migrate to OAuth in the future).


### Execution flags
* `--debug` enables logging of relevant states of the bot.
