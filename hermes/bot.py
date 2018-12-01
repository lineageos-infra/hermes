import os
import re
import time

from functools import wraps
from threading import Thread

from slackclient import SlackClient
import redis as _redis

from hermes.util import Util


class Bot:
    default_config = {
        "SLACK_TOKEN": os.environ.get("SLACK_TOKEN"),
        "REDIS_HOST": os.environ.get("REDIS_HOST", "localhost"),
        "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
        "REDIS_DB": int(os.environ.get("REDIS_DB", 0)),
    }

    def __init__(self, config={}):
        self.commands = {}
        self.jobs = {}
        self.regexes = {}
        self.config = self.default_config
        if not self.config["SLACK_TOKEN"]:
            raise Exception("SLACK_TOKEN must be set")
        self.slack_client = SlackClient(self.config["SLACK_TOKEN"])
        self.connect_redis()
        self.util = Util(self)
        self.util.update_users()
        self.util.update_channels()

    def connect_redis(self):
        self.redis = _redis.StrictRedis(
            host=self.config["REDIS_HOST"],
            port=self.config["REDIS_PORT"],
            db=self.config["REDIS_DB"],
        )

    def _job_runner(self):
        while True:
            for timer in self.jobs.keys():
                if time.time() % timer == 0:
                    for job in self.jobs[timer]:
                        try:
                            job()
                        except Exception as e:
                            print(f"Error: {e}")
        time.sleep(1)
        pass

    def run(self):
        """Run the bot
        
        Creates a worker thread for jobs, then connects to Slack's RTM API
        """
        self.job_runner = Thread(target=self._job_runner)
        self.job_runner.start()

        if self.slack_client.rtm_connect(with_team_state=False, auto_reconnect=True):
            while True:
                for event in self.slack_client.rtm_read():
                    if event["type"] == "message" and "text" in event:
                        if event.get("subtype") != "bot_message":
                            # Process the message.
                            words = event.get("text").split()
                            # Command mode, find a matching command.
                            if words and words[0].startswith("!"):
                                command = self.commands.get(words[0][1:])
                                if command:
                                    try:
                                        command(
                                            event, words[1:] if len(words) > 1 else []
                                        )
                                    except Exception as e:
                                        print(f"Error: {e}")

                            for regex in self.regexes:
                                matches = re.findall(regex, " ".join(words))
                                if matches:
                                    for match in matches:
                                        if not match:
                                            # Throw away empty matches
                                            continue
                                        try:
                                            self.regexes[regex](event, match)
                                        except Exception as e:
                                            print(f"Error: {e}")

    def register_command(self, name, f):
        print(f"Registering command: {name}")
        self.commands[name] = f

    def command(self):
        """Defines a command function.

        Command functions take two arguments: 
        - the slack event itself
        - a (possibly empty) list of arguments.
        """

        def decorator(f):
            register_command(f.__name__, f)
            return f

        return decorator

    def require_admin(self, f):
        """Requires admin for a command/regex.
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            print(args, kwargs)
            if self.util.is_admin(args[0].get("user", "")):
                return f(*args, **kwargs)
            else:
                channel = args[0].get("channel", "")
                if channel:
                    self.slack_client.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text="You aren't allowed to do that.",
                        as_user=True,
                    )
                    return lambda args, kwargs: None

        return wrapper

    def register_job(self, timer, f):
        print(f"Registering job {f.__name__} to run every {timer} seconds")
        self.jobs.setdefault(timer, []).append(f)

    def job(self, timer):
        """Defines a job function
        Job functions run, roughly, on a timer.
        """

        def decorator(f):
            self.jobs.register_job(timer, f)
            return f

        return decorator

    def register_regex(self, regex, f):
        print(f"Registering regex {regex}")
        self.regexes[regex] = f

    def regex(self, regex):
        """Defines a regex function

        These are like command functions, and take two arguments:
        - the slack event itself
        - a single string containing the matched string

        For a single event, this may be called multiple times with multiple matches.
        """

        def decorator(f):
            self.register_regex(regex, f)
            return f

        return decorator
