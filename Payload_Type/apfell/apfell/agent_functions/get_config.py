from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class GetConfigArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class GetConfigCommand(CommandBase):
    cmd = "get_config"
    needs_admin = False
    help_cmd = "get_config"
    description = "Gets the current running config via the C2 class"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1082"]
    argument_class = GetConfigArguments

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"$.NSProcessInfo.processInfo.*, $.NSHost.currentHost.*",
            BaseArtifactType="API"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
