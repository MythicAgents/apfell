from mythic_payloadtype_container.PayloadBuilder import *
from mythic_payloadtype_container.MythicCommandBase import *
import sys
import json

class Apfell(PayloadType):

    name = "apfell"
    file_extension = "js"
    author = "@its_a_feature_"
    supported_os = [SupportedOS.MacOS]
    wrapper = False
    wrapped_payloads = []
    note = """This payload uses JavaScript for Automation (JXA) for execution on macOS boxes."""
    supports_dynamic_loading = True
    build_parameters = {}
    c2_profiles = ["http", "dynamichttp", "smbserver"]
    support_browser_scripts = [
        BrowserScript(script_name="create_table", author="@its_a_feature_")
    ]
    translation_container = None #"translator"

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        build_msg = ""
        try:
            command_code = ""
            for cmd in self.commands.get_commands():
                command_code += (
                    open(self.agent_code_path / "{}.js".format(cmd), "r").read() + "\n"
                )
            base_code = open(
                self.agent_code_path / "base" / "apfell-jxa.js", "r"
            ).read()
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("COMMANDS_HERE", command_code)
            all_c2_code = ""
            for c2 in self.c2info:
                c2_code = ""
                try:
                    profile = c2.get_c2profile()
                    c2_code = open(
                        self.agent_code_path
                        / "c2_profiles"
                        / "{}.js".format(profile["name"]),
                        "r",
                    ).read()
                    for key, val in c2.get_parameters_dict().items():
                        if isinstance(val, dict):
                            c2_code = c2_code.replace(key, val["enc_key"] if val["enc_key"] is not None else "")
                        elif not isinstance(val, str):
                            c2_code = c2_code.replace(key, json.dumps(val))
                        else:
                            c2_code = c2_code.replace(key, val)
                except Exception as p:
                    build_msg += str(p)
                all_c2_code += c2_code
            base_code = base_code.replace("C2PROFILE_HERE", all_c2_code)
            resp.payload = base_code.encode()
            resp.message = "Successfully built!\n"
            resp.build_error = build_msg
        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.set_message("Error building payload: " + str(e))
        return resp
