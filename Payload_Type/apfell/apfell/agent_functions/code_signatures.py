from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class CodeSignaturesArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                description="path to file (no quotes required)",
                parameter_group_info=[ParameterGroupInfo()]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("path", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "path" in dictionary_arguments:
            self.add_arg("path", dictionary_arguments["path"])
        else:
            raise ValueError("Missing 'path' argument")


class CodeSignaturesCommand(CommandBase):
    cmd = "code_signatures"
    needs_admin = False
    help_cmd = 'code_signatures {/path/to/app.app | /path/to/binary}'
    description = "This uses JXA to list the code signature information for a binary or bundle"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1518"]
    argument_class = CodeSignaturesArguments
    supported_ui_features = ["code_signatures:list"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.DisplayParams = " for " + taskData.args.get_arg("path")
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
