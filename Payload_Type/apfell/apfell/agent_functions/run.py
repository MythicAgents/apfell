from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class RunArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="args",
                type=ParameterType.Array,
                description="Arguments to pass to the binary",
            ),
            CommandParameter(
                name="path",
                type=ParameterType.String,
                description="Full path to binary to execute",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class RunCommand(CommandBase):
    cmd = "run"
    needs_admin = False
    help_cmd = "run"
    description = "The command uses the ObjectiveC bridge to spawn that process with those arguments on the computer and get your output back. It is not interactive and does not go through a shell, so be sure to specify the full path to the binary you want to run."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1106"]
    argument_class = RunArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"{taskData.args.get_arg('path')} {taskData.args.get_arg('args')}",
            BaseArtifactType="Process Create"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
