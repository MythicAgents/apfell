from mythic_payloadtype_container.MythicCommandBase import *
import sys
import json
from mythic_payloadtype_container.MythicResponseRPC import *


class ShellArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "command": CommandParameter(
                name="command", type=ParameterType.String, description="Command to run"
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("command", self.command_line)
        else:
            raise ValueError("Missing arguments")


class ShellOPSEC(CommandOPSEC):
    injection_method = ""
    process_creation = "/bin/bash -c"
    authentication = ""

    async def opsec_pre(self, task: MythicTask):

        processes = await MythicResponseRPC(task).search_database(
            table="process",
            search={"host": task.callback.host}
        )
        if len(processes.response) == 0:
            task.opsec_pre_blocked = True
            task.opsec_pre_message = f"This spawns {self.process_creation} and there is no process data on the host yet."
            task.opsec_pre_message += "\nRun \"list_apps\" first to check for dangerous processes"
            task.opsec_pre_bypass_role = "operator"
            return
        else:
            processes = await MythicResponseRPC(task).search_database(
                table="process",
                search={"name": "Microsoft Defender", "host": task.callback.host}
            )
            if len(processes.response) > 0:
                task.opsec_pre_blocked = True
                task.opsec_pre_message = f"Microsoft Defender spotted on the host in running processes. Don't spawn commands this way"

    async def opsec_post(self, task: MythicTask):
        processes = await MythicResponseRPC(task).search_database(
            table="process",
            search={"name": "Microsoft Defender", "host": task.callback.host}
        )
        if len(processes.response) > 0:
            task.opsec_post_blocked = True
            task.opsec_post_message = f"Microsoft Defender spotted on the host in running processes. Really, don't do this"


class ShellCommand(CommandBase):
    cmd = "shell"
    needs_admin = False
    help_cmd = "shell {command}"
    description = """This runs {command} in a terminal by leveraging JXA's Application.doShellScript({command}).
WARNING! THIS IS SINGLE THREADED, IF YOUR COMMAND HANGS, THE AGENT HANGS!"""
    version = 1
    is_exit = False
    is_file_browse = False
    is_process_list = False
    is_download_file = False
    is_remove_file = False
    is_upload_file = False
    author = "@its_a_feature_"
    attackmapping = ["T1059"]
    argument_class = ShellArguments
    opsec_class = ShellOPSEC
    attributes = CommandAttributes(
        spawn_and_injectable=True,
        supported_os=[SupportedOS.MacOS]
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicResponseRPC(task).register_artifact(
            artifact_instance="/bin/sh -c {}".format(task.args.get_arg("command")),
            artifact_type="Process Create",
        )
        resp = await MythicResponseRPC(task).register_artifact(
            artifact_instance="{}".format(task.args.get_arg("command")),
            artifact_type="Process Create",
        )
        return task

    async def process_response(self, response: AgentResponse):
        #print(response.response)
        #sys.stdout.flush()
        #resp = await MythicResponseRPC(response.task).callback_tokens(host=response.task.callback.host,
        #                                                     add=response.response, remove=[])
        pass
