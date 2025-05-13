from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *

class RunArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="script", 
                cli_name="script", 
                display_name="Script to Run", 
                type=ParameterType.File, 
                description="Select ruby script to run",
                parameter_group_info=[ 
                    ParameterGroupInfo(
                        required=True,
                        group_name="Default",
                        ui_position=0
                    )
                ]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class RunCommand(CommandBase):
    cmd = "run_ruby"
    needs_admin = False
    help_cmd = "run_ruby"
    description = "The command uses the ObjectiveC bridge to spawn ruby and capture standard input. The supplied script is passed to the new ruby process, evaluated, and the output is returned."
    version = 1
    supported_ui_features = ["file_browser:upload"]
    author = "@robot"
    attackmapping = ["T1059"]
    argument_class = RunArguments
    attributes = CommandAttributes(
        supported_os=[SupportedOS.MacOS],
        load_only=True,
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"/usr/bin/ruby -",
            BaseArtifactType="Process Create"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
