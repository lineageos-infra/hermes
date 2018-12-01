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
            self.bot.redis.hset("users:uid_name", user["id"], user["name"])
            self.bot.redis.hset("users:name_uid", user["name"], user["id"])
            if user.get("is_admin", False) or user.get("is_owner", False):
                self.bot.redis.sadd("admin", user["id"])

    def get_username(self, uid):
        username = self.bot.redis.hget("users:uid_name", uid)
        return username.decode("utf-8") if username else None

    def get_uid(self, username):
        uid = self.bot.redis.hget("users:name_uid", username)
        return uid.decode("utf-8") if uid else None

    def is_admin(self, uid):
        return self.bot.redis.sismember("admin", uid)
