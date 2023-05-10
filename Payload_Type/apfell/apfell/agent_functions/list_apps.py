from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ListAppsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ListAppsCommand(CommandBase):
    cmd = "list_apps"
    needs_admin = False
    help_cmd = "list_apps"
    description = "This uses NSApplication.RunningApplications api to get information about running applications."
    version = 1
    supported_ui_features = ["process_browser:list"]
    author = "@its_a_feature_"
    attackmapping = ["T1057"]
    argument_class = ListAppsArguments
    browser_script = BrowserScript(script_name="list_apps_new", author="@its_a_feature_", for_new_ui=True)

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.NSWorkspace.sharedWorkspace.runningApplications",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
