hermes
---

Hermes is a python 3 slackbot wrapper.

A very basic bot looks like this:

```
from hermes import bot

bot = Bot()

bot.datastore_._kind = bot.datastore.REDIS

@bot.command()
def whoami(event, args):
    print(f"You are {bot.util.get_username(uid)}")

@bot.job(60):
def run_task():
    bot.slack_client.api_call("chat.postMessage", channel="C0XXXXXX", text="I ran a task!")

@bot.regex(r".*")
def regex_test(event, match):
    print(f'You said {event.get("message")}')

if __name__ == "__main__":
    bot.run()
```

