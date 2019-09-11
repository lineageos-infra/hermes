class Util:
    def __init__(self, bot):
        self.bot = bot

    def update_channels(self):
        conversations = self.bot.slack_client.api_call("conversations.list")
        for channel in conversations.get("channels"):
            self.bot.redis.hset("channels:cid_name", channel["id"], channel["name"])
            self.bot.redis.hset("channels:name_cid", channel["name"], channel["id"])
        print(self.bot.redis.hgetall("channels"))

    def get_channelname(self, cid):
        channelname = self.bot.redis.hget("chanenls:name_cid", cid)
        return channelname.decode("utf-8") if channel else None

    def get_cid(self, channel):
        cid = self.bot.redis.hget("channels:name_cid", channel)
        return cid.decode("utf-8" if cid else None)

    def update_users(self):
        users = self.bot.slack_client.api_call("users.list")
        for user in users.get("members"):
            username = user["name"]
            self.bot.redis.hset("users:uid_name", user["id"], username)
            self.bot.redis.hset("users:name_uid", username, user["id"])
            if user.get("is_admin", False) or user.get("is_owner", False):
                self.bot.redis.hset("permissions", user["id"], 90)
            if username == "zifnab":
                self.bot.redis.hset("permissions", user["id"], 9001)

    def get_username(self, uid):
        username = self.bot.redis.hget("users:uid_name", uid)
        return username.decode("utf-8") if username else None

    def get_uid(self, username):
        uid = self.bot.redis.hget("users:name_uid", username)
        return uid.decode("utf-8") if uid else None

    def get_perm(self, uid):
        level = self.bot.redis.hget("permissions", uid)
        if not level:
            return 0
        else:
            return int(level)
