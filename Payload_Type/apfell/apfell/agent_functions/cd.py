from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

class CdArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                description="path to change directory to",
                parameter_group_info=[ParameterGroupInfo()]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Need to specify a path")
        self.add_arg("path", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "path" in dictionary_arguments:
            self.add_arg("path", dictionary_arguments["path"])
        else:
            raise ValueError("Missing 'path' argument")


class CdCommand(CommandBase):
    cmd = "cd"
    needs_admin = False
    help_cmd = "cd [path]"
    description = "Change the current working directory to another directory. No quotes are necessary and relative paths are fine"
    version = 1
    author = "@its_a_feature_"
    argument_class = CdArguments
    attackmapping = ["T1083"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"fileManager.changeCurrentDirectoryPath",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
