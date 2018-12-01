from hermes.plugins import Plugin
import praw


class Reddit(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.register_job(60, self.reddit_fetch)

    def reddit_fetch(self):
        done = [x.decode("utf-8") for x in self.bot.redis.smembers("reddit-fetch:done")]
        try:
            r = praw.Reddit(user_agent="LineageOS Slack Bot v3.0")
            r.read_only = True
            for post in r.subreddit("lineageos").new(limit=10):
                if post.id in done:
                    continue
                attachment = {
                    "fallback": post.url,
                    "title": "{} * /r/LineageOS".format(post.title),
                    "title_link": post.url,
                    "text": post.selftext[:140]
                    if hasattr(post, "selftext")
                    else "" + "..."
                    if len(post.selftext) > 140
                    else "",
                    "thumb_url": "https://www.redditstatic.com/icon.png",
                    "author_name": "reddit",
                    "author_icon": "https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png",
                }
                self.bot.slack_client.api_call(
                    "chat.postMessage",
                    channel=self.bot.util.get_cid("spam"),
                    attachments=[attachment],
                    unfurl_links=True,
                    as_user=True,
                )
                self.bot.redis.sadd("reddit-fetch:done", post.id)
        except Exception as e:
            print(e)
