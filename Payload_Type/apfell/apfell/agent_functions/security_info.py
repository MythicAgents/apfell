from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class SecurityInfoArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class SecurityInfoCommand(CommandBase):
    cmd = "security_info"
    needs_admin = False
    help_cmd = "security_info"
    description = 'This uses JXA to list some security information about the system by contacting the "System Events" application via Apple Events. This can cause a popup or be denied in Mojave and later'
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = SecurityInfoArguments

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
