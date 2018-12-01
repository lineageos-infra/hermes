from pygerrit2.rest import GerritRestAPI
import datetime
from hermes.plugins import Plugin


class Gerrit(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.gerrit_url = "https://review.lineageos.org/"
        self.rest = GerritRestAPI(url=self.gerrit_url)
        self.bot.register_regex(
            f"https://review\.lineageos\.org/c/(?:.*/)*(\d+)", self.gerrit_change
        )

    def gerrit_change(self, event, match):
        change = self.rest.get(f"/changes/{match}?o=DETAILED_ACCOUNTS")
        self.bot.slack_client.api_call(
            "chat.postMessage",
            channel=event["channel"],
            as_user=True,
            attachments=[
                {
                    "fallback": f"https://review.lineageos.org/c/{change['_number']}: {change['subject']}",
                    "color": "good",
                    "title": f"{change['_number']}: {change['subject']} ({change['status']})",
                    "title_link": f"https://review.lineageos.org/c/{change['_number']}",
                    "mrkdwn_in": ["text"],
                    "text": (
                        "*Project*: <{base}#/q/project:{project}|{project}> ({branch})\n"
                        "*Topic*: {topic}\n"
                        "*Owner*: <{base}/q/owner:{username}|{name} ({email})>"
                    ).format(
                        project=change["project"],
                        branch=change["branch"],
                        topic="<{}/q/{topic}|{topic}>".format(
                            self.gerrit_url, topic=change["topic"]
                        )
                        if "topic" in change
                        else "None",
                        username=change["owner"]["username"],
                        name=change["owner"]["name"],
                        email=change["owner"]["email"],
                        base=self.gerrit_url,
                    ),
                }
            ],
        )
