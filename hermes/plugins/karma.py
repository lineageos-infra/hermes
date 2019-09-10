import re
import random

from hermes.plugins import Plugin


class Karma(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.register_command("point", self.point)
        self.bot.register_command("lick", self.point)
        self.bot.register_command("poke", self.point)
        self.bot.register_command("karma", self.karma)
        self.bot.register_command("kick", self.kick)

    def _get_all_points(self):
        return {self.bot.util.get_username(x.decode("utf-8")): y.decode("utf-8") for x,y in self.bot.redis.hgetall("points").items()}

    def _get_point(self, uid):
        value = self.bot.redis.hget("points", uid)
        return 0 if not value else int(value)

    def _set_point(self, uid, value):
        self.bot.redis.hset("points", uid, value)

    def point(self, event, args):
        """Grants a user a point. Usage: !point <user>"""
        if not args:
            text = "Usage: !point <user>"
        else:
            user = args[0]
            uid = self.bot.util.get_uid(user)
            if uid == event["user"]:
                points = self._get_point(event["user"]) - 1
                text = f"You lost a point! New score: {points}"
                self._set_point(event['user'], points)
            elif not uid:
                text = "User not found!"
            else:
                points = self._get_point(uid) + 1
                self._set_point(uid, points)
                text = f"Point granted to {user}! New score: {points}"

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )

    def karma(self, event, args):
        """Get karma"""
        points = self._get_all_points()
        values = {}
        for user, score in points.items():
            values.setdefault(score, []).append(user)
        text = []
        for score in sorted(values.keys(), reverse=True):
            text.append(f"{score}: " + ", ".join(values[score]))

        text = "\n".join(text)

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )

    def kick(self, event, args):
        """Kicking people is wrong"""
        if not args or not self.bot.util.get_uid(args[0]):
            points = self._get_point(event["user"]) - 1
            self._set_point(event["user"], points)
            text = f"I kicked you. You lost a point. New score: {points}"
        else:
            uid = self.bot.util.get_uid(args[0])
            points = self._get_point(uid) - 1
            self._set_point(uid, points)
            text = f"{args[0]} was kicked, new score {points}"

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )
