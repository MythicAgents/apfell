from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class CatArguments(TaskArguments):
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


class CatCommand(CommandBase):
    cmd = "cat"
    needs_admin = False
    help_cmd = "cat /path/to/file"
    description = "Read the contents of a file and display it to the user. No need for quotes and relative paths are fine"
    version = 1
    author = "@its_a_feature_"
    argument_class = CatArguments
    attackmapping = ["T1005", "T1552.001"]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.NSString.stringWithContentsOfFileEncodingError",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
