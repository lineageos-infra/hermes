class Plugin:
    def __init__(self, bot):
        self.bot = bot


from .echo import Echo
from .utils import Utils
from .cve import Cve
from .reddit import Reddit
from .gerrit import Gerrit
from .git_plugin import GitPlugin