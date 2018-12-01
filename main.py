from hermes.bot import Bot

bot = Bot()

from hermes.plugins import Echo, Utils, Cve, Reddit, Gerrit

Cve(bot)
Echo(bot)
Reddit(bot)
Utils(bot)
Gerrit(bot)


if __name__ == "__main__":
    bot.run()
