from config import config
from slackclient import SlackClient

# https://api.slack.com/apps
sc = SlackClient(
    config['slack_bot']['token']
)

sc.api_call(
  "chat.postMessage",
  channel=config['slack_bot']['channel'],
  text='Mic test 123'
)
