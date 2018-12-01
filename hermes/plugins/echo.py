from . import Plugin


class Echo(Plugin):
    def echo(self, event, match):
        print(event)

    def __init__(self, bot):
        super().__init__(bot)
        bot.register_regex(r".*", self.echo)

    # @bot.regex(r".*")
