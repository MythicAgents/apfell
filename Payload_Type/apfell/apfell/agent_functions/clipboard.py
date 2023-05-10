from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ClipboardArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                display_name="Clipboard Types To Read",
                name="read",
                type=ParameterType.Array,
                default_value=["public.utf8-plain-text"],
                description="Types of clipboard data to retrieve, defaults to public.utf8-plain-text",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    group_name="read"
                )]
            ),
            CommandParameter(
                name="data",
                type=ParameterType.String,
                description="Data to put on the clipboard",
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    group_name="write",
                    ui_position=1
                )]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) != 0:
            self.add_arg("data", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "data" in dictionary_arguments:
            self.add_arg("data", dictionary_arguments["data"])
        else:
            self.remove_arg("data")
        if "read" in dictionary_arguments:
            self.add_arg("read", dictionary_arguments["read"])


class ClipboardCommand(CommandBase):
    cmd = "clipboard"
    needs_admin = False
    help_cmd = "clipboard [data]"
    description = "Get all the types of contents on the clipboard, return specific types, or set the contents of the clipboard. Root has no clipboard!"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1115"]
    argument_class = ClipboardArguments
    supported_ui_features = ["clipboard:list"]
    browser_script = BrowserScript(script_name="clipboard_new", author="@its_a_feature_", for_new_ui=True)

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

        if taskData.args.get_arg("data") != "":
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"$.NSPasteboard.generalPasteboard.setStringForType",
                BaseArtifactType="API"
            ))
        else:
            await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
                TaskID=taskData.Task.ID,
                ArtifactMessage=f"$.NSPasteboard.generalPasteboard.dataForType",
                BaseArtifactType="API"
            ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
