from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class PersistFolderactionArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="code",
                type=ParameterType.String,
                description="osascript code",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    group_name="code"
                )]
            ),
            CommandParameter(
                name="url",
                type=ParameterType.String,
                description="http://url.of.host/payload",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    group_name="url"
                )]
            ),
            CommandParameter(
                name="folder",
                type=ParameterType.String,
                description="/path/to/folder/to/watch",
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=1, group_name="url"),
                    ParameterGroupInfo(ui_position=1, group_name="code")
                ]
            ),
            CommandParameter(
                name="script_path",
                type=ParameterType.String,
                description="/path/to/script/to/create/on/disk",
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=2, group_name="url"),
                    ParameterGroupInfo(ui_position=2, group_name="code")
                ]
            ),
            CommandParameter(
                name="language",
                type=ParameterType.ChooseOne,
                choices=["JavaScript", "AppleScript"],
                default_value="JavaScript",
                description="If supplying custom 'code', this is the language",
                parameter_group_info=[
                    ParameterGroupInfo(ui_position=3, group_name="url", required=False),
                    ParameterGroupInfo(ui_position=3, group_name="code", required=False)
                ]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class PersistFolderactionCommand(CommandBase):
    cmd = "persist_folderaction"
    needs_admin = False
    help_cmd = "persist_folderaction"
    description = "Use Folder Actions to persist a compiled script on disk. You can either specify a 'URL' and automatically do a backgrounding one-liner, or supply your own code and language."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1546"]
    argument_class = PersistFolderactionArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of System Events",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
