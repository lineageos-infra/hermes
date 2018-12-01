from . import Plugin


class Utils(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.register_command("whoami", self.whoami)
        self.bot.register_command("info", self.info)
        self.bot.register_command("admin", self.bot.require_admin(self.admin))
        self.bot.register_command("help", self.help)

    def whoami(self, event, command):
        """Prints username/admin status"""
        username = self.bot.util.get_username(event["user"])
        is_admin = "are" if self.bot.util.is_admin(event["user"]) else "are not"
        text = f"You are {username}. You {is_admin} an admin"
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

    def admin(self, event, args):
        """Admin utilities. !admin help for more information"""
        help = "\n".join(
            [
                "Usage:",
                "admin list - list admins",
                "admin add <username> - add an admin",
                "admin del <username> - delete an admin"
                "admin db <command> <key> <args> - access redis",
            ]
        )
        if not args or args[0] == "help":
            text = help
        elif args[0] == "add":
            if len(args) != 2:
                text = help
            else:
                uid = self.bot.util.get_uid(args[1])
                if uid:
                    self.bot.redis.sadd("admin", uid)
                    text = f"<@{event['user']}>: Done."
                else:
                    text = f"<@{event['user']}>: User not found."
        elif args[0] == "del":
            if len(args) != 2:
                text = help
            else:
                uid = self.bot.util.get_uid(args[1])
                if uid:
                    self.bot.redis.srem("admin", uid)
                    text = f"<@{event['user']}>: Done."
                else:
                    text = f"<@{event['user']}>: User not found."
        elif args[0] == "list":
            text = [
                self.bot.util.get_username(x.decode("utf-8"))
                for x in self.bot.redis.smembers("admin")
            ]
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
                    text = {x.decode("utf-8"): y.decode("utf-8") for x, y in text}
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
