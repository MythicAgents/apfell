from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class DownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                temp_json = json.loads(self.command_line)
                if "host" in temp_json:
                    # this means we have tasking from the file browser rather than the popup UI
                    # the apfell agent doesn't currently have the ability to do _remote_ listings, so we ignore it
                    self.command_line = temp_json["path"] + "/" + temp_json["file"]
                else:
                    raise Exception("Unsupported JSON")
        else:
            raise Exception("Must provide a path to download")


class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download {path to remote file}"
    description = "Download a file from the victim machine to the Mythic server in chunks (no need for quotes in the path)."
    version = 1
    supported_ui_features = ["file_browser:download"]
    author = "@its_a_feature_"
    parameters = []
    attackmapping = ["T1020", "T1030", "T1041"]
    argument_class = DownloadArguments
    browser_script = BrowserScript(script_name="download_new", author="@its_a_feature_", for_new_ui=True)
    attributes = CommandAttributes(
        suggested_command=True
    )

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.NSFileHandle.fileHandleForReadingAtPath, readDataOfLength",
            BaseArtifactType="API"
        ))
        response.DisplayParams = taskData.args.command_line
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
