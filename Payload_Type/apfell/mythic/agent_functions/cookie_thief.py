from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class CookieThiefArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "password": CommandParameter(
                name="User Login Password",
                type=ParameterType.String,
                description="p@55w0rd_here for user login",
                required=True,
                ui_position=1
            ),
            "browser": CommandParameter(
                name="browser",
                type=ParameterType.ChooseOne,
                choices=["chrome", "firefox"],
                required=False,
                description="choose the browser to streal cookies from",
                default_value="chrome",
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                temp_json = json.loads(self.command_line)
                if "host" in temp_json:
                    # this means we have tasking from the file browser rather than the popup UI
                    # the apfell agent doesn't currently have the ability to do _remote_ listings, so we ignore it
                    self.command_line = temp_json["path"] + "/" + temp_json["file"]
                else:
                    raise Exception("Unsupported JSON")
        else:
            raise Exception("Must provide a path to download")


class CookieThiefCommand(CommandBase):
    cmd = "cookie_thief"
    needs_admin = False
    help_cmd = "cookie_thief {user account password} {browser}"
    description = "Downloads the keychain db and browser cookies, decryots the keychain, extracts the cookie key and decrypts the cookies."
    version = 1
    supported_ui_features = ["file_browser:download"] #CHANGE
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    argument_class = CookieThiefArguments
    browser_script = BrowserScript(script_name="cookie_theif", author="@antman1p")

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
