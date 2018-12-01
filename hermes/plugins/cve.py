import requests
from hermes.plugins import Plugin


class Cve(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.register_regex(r"CVE-\d{4}-\d{4,7}", self.cve)

    def cve(self, event, match):
        r = requests.get("https://cve.circl.lu/api/cve/{}".format(match))
        if r.status_code == 200:
            summary = r.json()["summary"]
            url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(match)
            self.bot.slack_client.api_call(
                "chat.postMessage",
                channel=event["channel"],
                as_user=True,
                attachments=[
                    {
                        "fallback": "{}: {} ({})".format(match, summary, url),
                        "color": "danger",
                        "title": "{}: {}".format(match, summary),
                        "title_link": url,
                    }
                ],
            )
