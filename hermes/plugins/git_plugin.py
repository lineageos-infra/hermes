import re

import git
import requests
from hermes.plugins import Plugin


class GitPlugin(Plugin):
    def __init__(self, bot):
        super().__init__(bot)
        assert self.bot.config.get("GITLAB_FORCEPUSH_TRIGGER_TOKEN")
        self.bot.register_command("gitadmin", self.bot.require_admin(self.gitadmin))

    def gitadmin(self, event, args):
        """Git admin utilities. !gitadmin help for more information"""
        help = "\n".join(
            [
                "Usage:",
                "'remote' is always in the form 'https://github.com/zifnab06/android.git#lineage-16.0",
                "'local' is always in the form LineageOS/android#lineage-16.0",
                "",
                "gitadmin fp <remote> <local> - forcepush remote to local",
            ]
        )

        if len(args) == 0:
            text = help
        elif args[0] == "fp" and len(args) == 3:  # remote local
            """This triggers a gitlab-ci job at https://gitlab.com/lineageos/infra/forcepush
               It was originally done via python, but the whole bot locks up while it's running
               and kernels are massive. """
            remote = args[1].replace("<", "").replace(">", "")
            local = args[2]
            print(remote, local)
            if not re.match(r"LineageOS/.*\.git#.*", local):
                text = (
                    "'local' is always in the form LineageOS/android.git#lineage-16.0"
                )
            elif not re.match(r"https://.*\.git#.*", remote):
                text = (
                    "'remote' is always in the form 'https://github.com/zifnab06/android.git#lineage-16.0",
                )
            else:
                remote_repo, remote_branch = remote.split("#")
                local_repo, local_branch = remote.split("#")
                gitlab_url = f"https://gitlab.com/api/v4/projects/9750215/trigger/pipeline?token={self.bot.config['GITLAB_FORCEPUSH_TRIGGER_TOKEN']}&ref=master"
                data = {
                    "variables[OUR_REPO]": local_repo,
                    "variables[OUR_BRANCH]": local_branch,
                    "variables[THEIR_REPO]": remote_repo,
                    "variables[THEIR_BRANCH]": remote_branch,
                }
                req = requests.post(gitlab_url, data)
                if req.status_code == 201:
                    text = f"Started at {req.json()['web_url']}"
                else:
                    text = f"ERROR: {req.status_code}, {req.text}"
        else:
            text = help

        self.bot.slack_client.api_call(
            "chat.postMessage", channel=event["channel"], text=text, as_user=True
        )
