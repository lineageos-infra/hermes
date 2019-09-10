import os
from hermes.bot import Bot

bot = Bot()
bot.config["GITLAB_FORCEPUSH_TRIGGER_TOKEN"] = os.environ.get("GITLAB_FORCEPUSH_TRIGGER_TOKEN")

from hermes.plugins import Echo, Utils, Cve, Reddit, Gerrit, GitPlugin

Cve(bot)
Reddit(bot)
Utils(bot)
Gerrit(bot)
GitPlugin(bot)



if __name__ == "__main__":
    bot.run()
