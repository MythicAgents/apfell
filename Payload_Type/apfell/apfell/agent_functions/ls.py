from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *
import sys


class LsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                type=ParameterType.String,
                default_value=".",
                description="Path of file or folder on the current system to list",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            )
        ]

    async def parse_arguments(self):
        self.add_arg("path", self.command_line)

    async def parse_dictionary(self, dictionary):
        if "host" in dictionary:
            # then this came from the file browser
            if dictionary["path"][-1] == "/":
                self.add_arg("path", dictionary["path"] + dictionary["file"])
            else:
                self.add_arg("path", dictionary["path"] + "/" + dictionary["file"])

            self.add_arg("file_browser", type=ParameterType.Boolean, value=True)
        else:
            self.load_args_from_dictionary(dictionary)


class LsCommand(CommandBase):
    cmd = "ls"
    needs_admin = False
    help_cmd = "ls /path/to/file"
    description = "Get attributes about a file and display it to the user via API calls. No need for quotes and relative paths are fine"
    version = 2
    author = "@its_a_feature_"
    attackmapping = ["T1106", "T1083"]
    supported_ui_features = ["file_browser:list"]
    argument_class = LsArguments
    browser_script = BrowserScript(script_name="ls_new", author="@its_a_feature_", for_new_ui=True)

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"fileManager.attributesOfItemAtPathError, fileManager.contentsOfDirectoryAtPathError",
            BaseArtifactType="API"
        ))
        if taskData.args.has_arg("file_browser") and taskData.args.get_arg("file_browser"):
            host = taskData.Callback.Host
            response.DisplayParams = host + ":" + taskData.args.get_arg("path")
        else:
            response.DisplayParams = taskData.args.get_arg("path")
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp