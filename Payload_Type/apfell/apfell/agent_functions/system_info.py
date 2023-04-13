from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class SystemInfoArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class SystemInfoCommand(CommandBase):
    cmd = "system_info"
    needs_admin = False
    help_cmd = "system_info"
    description = "This uses JXA to get some system information. It doesn't send Apple Events to any other applications though, so it shouldn't cause popups."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = SystemInfoArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"currentApp.systemInfo()",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
