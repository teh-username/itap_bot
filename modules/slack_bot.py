from slackclient import SlackClient


def send_error_log(token, channel, exception_message):
    if not token:
        return

    client = SlackClient(token)
    client.api_call(
      "chat.postMessage",
      channel=channel,
      text="""
        Bot encountered an error!

        ```{}```
      """.format(exception_message)
    )
