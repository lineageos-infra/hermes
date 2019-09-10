from . import Plugin


class Utils(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.register_command("admin", self.bot.require_perm(100)(self.admin))
        self.bot.register_command("echo", self.echo)
        self.bot.register_command("help", self.help)
        self.bot.register_command("info", self.info)
        self.bot.register_command("perms", self.perms)
        self.bot.register_command("whoami", self.whoami)

    def whoami(self, event, command):
        """Prints username/admin status"""
        username = self.bot.util.get_username(event["user"])
        level = self.bot.util.get_perm(event["user"])
        text = f"You are {username}. You level is {level}"
        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )

    def info(self, event, args):
        """Shows loaded command info"""
        text = "\n".join(
            [
                "Loaded Commands",
                ", ".join([f"`{x}`" for x in self.bot.commands.keys()]),
                "Loaded Regexes",
                ", ".join([f"`{x}`" for x in self.bot.regexes.keys()]),
                "Loaded Jobs",
                ", ".join([f"`{k}:{v}" for k, v in self.bot.jobs.items()]),
            ]
        )

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )

    def echo(self, event, args):
        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=f"{event['user']} {event['channel']} {args}", as_user=True
        )


    def admin(self, event, args):
        """(9) Admin utilities. !admin help for more information"""
        help = "\n".join(
            [
                "Usage:",
                "admin db <command> <key> <args> - access redis",
            ]
        )
        if not args or args[0] == "help":
            text = help
        elif args[0] == "db":
            if len(args) < 2:
                text = help
            else:
                try:
                    if len(args) > 2:
                        text = getattr(self.bot.redis, args[1])(*args[2:])
                    else:
                        text = getattr(self.bot.redis, args[2])()
                except Exception as e:
                    text = str(e)

                if type(text) is list or type(text) is set:
                    text = [x.decode("utf-8") for x in text]
                elif type(text) is dict:
                    text = {x.decode("utf-8"): y.decode("utf-8") for x, y in text.items()}
                elif type(text) is bytes:
                    text = text.decode("utf-8")
            pass
        else:
            text = help

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )

    def help(self, event, args):
        """This message"""
        commands = []
        for name, command in self.bot.commands.items():
            commands.append(f"{name}: {command.__doc__}")
        self.bot.slack_client.api_call(
            "chat.postMessage",
            channel=event["channel"],
            text="\n".join(sorted(commands)),
            as_user=True,
        )

    def perms(self, event, args):
        """Modify permissions. !perms help for more information"""
        help = "\n".join([
            "Modifies permissions.",
            "perms list: list all permissions",
            "perms set <user> <level>: Set a users permissions. Must be lower than your own."
        ])
        if not args or args[0] == help:
            text = help
        elif args[0] == "list":
            permissions = {self.bot.util.get_username(x.decode("utf-8")): int(y) for (x,y) in self.bot.redis.hgetall("permissions").items()}
            data = {}
            for user,level in permissions.items():
                data.setdefault(level, []).append(user)
            text = []
            for level in sorted(data.keys(), reverse=True):
                text.append(f"{level}: " + " ".join(data.get(level)))
            text = "\n".join(text)
        elif args[0] == "set" and len(args) == 3:
            user = args[1]
            uid = self.bot.util.get_uid(user)
            new_level = int(args[2])
            level = self.bot.util.get_perm(event["user"])
            if uid == event["user"]:
                text = f"This is dumb. Your problem. It's done."
                self.bot.redis.hset("permissions", uid, new_level)
            elif not uid:
                text = f"I'm sorry but {user} wasn't found"
            elif new_level >= level:
                text = f"I'm sorry but you can't do that, you can only assign permissions below your level ({new_level} >= {level})"
            elif new_level < 0:
                text = f"If you say so. {user} is now {new_level}..."
                self.bot.redis.hset("permissions", uid, new_level)
            else:
                self.bot.redis.hset("permissions", uid, new_level)
                text = "Done!"
        else:
            text = help

        self.bot.slack_client.api_call(
            "chat.postMessage",
            channel=event["channel"],
            text=text,
            as_user=True,
        )
