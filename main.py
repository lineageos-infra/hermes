from hermes.bot import Bot

bot = Bot()

from hermes.plugins import Echo, Utils, Cve, Reddit, Gerrit

Cve(bot)
Echo(bot)
# Reddit(bot)
Utils(bot)
Gerrit(bot)

# @bot.regex(r".*")
# def echo(event, match):
#     print(event)


# @bot.command()
# def whoami(event, command):
#     """Prints username/admin status"""
#     username = bot.util.get_username(event["user"])
#     is_admin = "are" if bot.util.is_admin(event["user"]) else "are not"
#     text = f"You are {username}. You {is_admin} an admin"
#     bot.slack_client.api_call(
#         "chat.postMessage", channel=event["channel"], text=text, as_user=True
#     )


# @bot.command()
# def info(event, args):
#     """Shows loaded command info"""
#     text = "\n".join(
#         [
#             "Loaded Commands",
#             ", ".join([f"`{x}`" for x in bot.commands.keys()]),
#             "Loaded Regexes",
#             ", ".join([f"`{x}`" for x in bot.regexes.keys()]),
#             "Loaded Jobs",
#             ", ".join(
#                 [f"`{x.__name__}`" for items in bot.jobs.values() for x in items]
#             ),
#         ]
#     )

#     bot.slack_client.api_call(
#         "chat.postMessage", channel=event["channel"], text=text, as_user=True
#     )


# @bot.command()
# @bot.require_admin
# def admin(event, args):
#     """Admin utilities. !admin help for more information"""
#     help = "\n".join(
#         [
#             "Usage:",
#             "admin list - list admins",
#             "admin add <username> - add an admin",
#             "admin del <username> - delete an admin"
#             "admin db <command> <key> <args> - access redis",
#         ]
#     )
#     if not args or args[0] == "help":
#         text = help
#     elif args[0] == "add":
#         if len(args) != 2:
#             text = help
#         else:
#             uid = bot.util.get_uid(args[1])
#             if uid:
#                 bot.redis.sadd("admin", uid)
#                 text = f"<{event['user']}>: Done."
#             else:
#                 text = f"<{event['user']}>: User not found."
#     elif args[0] == "del":
#         if len(args) != 2:
#             text = help
#         else:
#             uid = bot.util.get_uid(args[1])
#             if uid:
#                 bot.redis.srem("admin", uid)
#                 text = f"<{event['user']}>: Done."
#             else:
#                 text = f"<{event['user']}>: User not found."
#     elif args[0] == "list":
#         text = [
#             bot.util.get_username(x.decode("utf-8"))
#             for x in bot.redis.smembers("admin")
#         ]
#     elif args[0] == "db":
#         if len(args) < 2:
#             text = help
#         else:
#             try:
#                 if len(args) > 2:
#                     text = getattr(bot.redis, args[1])(*args[2:])
#                 else:
#                     text = getattr(bot.redis, args[2])()
#             except Exception as e:
#                 text = str(e)

#             if type(text) is list or type(text) is set:
#                 text = [x.decode("utf-8") for x in text]
#             elif type(text) is dict:
#                 text = {x.decode("utf-8"): y.decode("utf-8") for x, y in text}
#             elif type(text) is bytes:
#                 text = text.decode("utf-8")
#         pass
#     else:
#         text = help

#     bot.slack_client.api_call(
#         "chat.postMessage", channel=event["channel"], text=text, as_user=True
#     )


# @bot.command()
# def help(event, args):
#     """This message"""
#     commands = []
#     for name, command in bot.commands.items():
#         commands.append(f"{name}: {command.__doc__}")
#     bot.slack_client.api_call(
#         "chat.postMessage",
#         channel=event["channel"],
#         text="\n".join(sorted(commands)),
#         as_user=True,
#     )

if __name__ == "__main__":
    bot.run()
